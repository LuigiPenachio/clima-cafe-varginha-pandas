"""ETL: INMET (estação A515) + IBGE PAM/PPM municipais de Varginha/MG."""

from __future__ import annotations

import io
import sys
import zipfile

import numpy as np
import pandas as pd
import requests

sys.stdout.reconfigure(encoding="utf-8")

from config import (
    BOVINO_CODE,
    DATA,
    ESTACAO_CODE,
    GEOJSON_URL,
    MUNICIPIO_CODE,
    PAM_CLASS,
    PAM_TABLE,
    PRODUCT_CODES,
    PPM_CLASS,
    PPM_TABLE,
    PROCESSED,
    RAW,
    SIDRA_BASE,
    YEARS,
)

MONTHLY_FILE = PROCESSED / "clima_varginha_mensal.csv"
ANNUAL_FILE = PROCESSED / "clima_varginha_anual.csv"
PANEL_FILE = PROCESSED / "painel_varginha.csv"
GEOJSON_FILE = DATA / "raw" / "geojson_mg_municipios.geojson"

USECOLS = [0, 1, 2, 7, 9, 10, 15]
NAMES = ["data", "hora", "precip", "temp", "tmax", "tmin", "umid"]
SIDRA_CODES = [
    "NC", "NN", "MC", "MN", "V",
    "D1C", "D1N", "D2C", "D2N", "D3C", "D3N", "D4C", "D4N",
]


def _sidra_json(path: str) -> pd.DataFrame:
    response = requests.get(SIDRA_BASE + path, timeout=180)
    response.raise_for_status()
    payload = response.json()
    if len(payload[0]) == len(SIDRA_CODES):
        return pd.DataFrame(payload[1:], columns=SIDRA_CODES)
    return pd.DataFrame(payload[1:]).rename(columns=payload[0])


def fetch_pam() -> pd.DataFrame:
    codes = ",".join(str(c) for c in PRODUCT_CODES.values())
    path = (
        f"t/{PAM_TABLE}/n6/{MUNICIPIO_CODE}/c{PAM_CLASS}/{codes}"
        f"/v/112/p/{YEARS[0]}-{YEARS[-1]}"
    )
    raw = _sidra_json(path)
    label = {str(v): k for k, v in PRODUCT_CODES.items()}
    out = pd.DataFrame({
        "ano": pd.to_numeric(raw["D4N"], errors="coerce").astype("Int64"),
        "cultura": raw["D2C"].astype(str).map(label),
        "rendimento": pd.to_numeric(raw["V"], errors="coerce"),
    })
    out = out.dropna(subset=["ano", "rendimento"])
    return out.replace(0, np.nan)


def fetch_ppm() -> pd.DataFrame:
    path = (
        f"t/{PPM_TABLE}/n6/{MUNICIPIO_CODE}/c{PPM_CLASS}/{BOVINO_CODE}"
        f"/v/105/p/{YEARS[0]}-{YEARS[-1]}"
    )
    raw = _sidra_json(path)
    out = pd.DataFrame({
        "ano": pd.to_numeric(raw["D4N"], errors="coerce").astype("Int64"),
        "rebanho_bovino": pd.to_numeric(raw["V"], errors="coerce"),
    })
    return out.dropna(subset=["ano", "rebanho_bovino"])


def _station_metadata(stream: io.BufferedIOBase) -> dict[str, str]:
    lines = stream.read(1500).decode("latin-1", errors="ignore").splitlines()[:8]
    stream.seek(0)
    meta: dict[str, str] = {}
    for line in lines:
        parts = line.split(";", 1)
        if len(parts) == 2:
            meta[parts[0].strip()] = parts[1].strip()
    return meta


def _parse_dates(frame: pd.DataFrame) -> pd.Series:
    date = frame["data"].astype("string").str.strip()
    hour = (
        frame["hora"].astype("string").str.strip()
        .str.replace(" UTC", "", regex=False)
    )
    hour = hour.where(hour.str.contains(":"), hour.str[:2] + ":" + hour.str[2:])
    return pd.to_datetime(date + " " + hour, format="mixed", errors="coerce")


def process_year(year: int) -> pd.DataFrame:
    archive = RAW / f"{year}.zip"
    if not archive.exists():
        raise FileNotFoundError(f"Baixe o ZIP de {year}: python src/download.py")

    with zipfile.ZipFile(archive) as zf:
        members = [
            n for n in zf.namelist()
            if n.lower().endswith(".csv") and "varginha" in n.lower()
        ]
        if not members:
            raise ValueError(f"Estação de Varginha ausente em {year}")
        member = members[0]

        with zf.open(member) as stream:
            meta = _station_metadata(stream)
            raw = pd.read_csv(
                stream,
                sep=";",
                encoding="latin-1",
                skiprows=9,
                header=None,
                decimal=",",
                na_values=["", "-9999", "-"],
                low_memory=False,
            )

    if meta.get("CODIGO (WMO):") != ESTACAO_CODE:
        raise ValueError(f"Estação inesperada em {year}: {meta.get('CODIGO (WMO):')}")

    frame = raw.iloc[:, USECOLS].copy()
    frame.columns = NAMES
    for column in NAMES[2:]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["data_hora"] = _parse_dates(frame)
    frame = frame.dropna(subset=["data_hora"])

    daily = frame.groupby(
        [frame["data_hora"].dt.month, frame["data_hora"].dt.date]
    ).agg(
        precip=("precip", lambda s: s.sum(min_count=1)),
        temp=("temp", "mean"),
        tmax=("tmax", "max"),
        n=("temp", "count"),
    )
    daily = daily[daily["n"] >= 6]
    monthly = daily.groupby(level=0).agg(
        precip_mm=("precip", "sum"),
        temp_media=("temp", "mean"),
        tmax_media=("tmax", "mean"),
        dias_quentes=("tmax", lambda s: int((s > 35).sum())),
        dias_validos=("n", "sum"),
    ).reset_index(names="mes")
    monthly["ano"] = year
    print(f"[{year}] estação {ESTACAO_CODE}: {len(monthly)} meses, "
          f"{int(monthly['dias_validos'].sum())} dias válidos")
    return monthly


def _impute_monthly(mensal: pd.DataFrame) -> pd.DataFrame:
    mensal = mensal[mensal["dias_validos"] >= 15].copy()
    mensal["ano"] = mensal["ano"].astype(int)
    mensal = mensal.sort_values(["ano", "mes"]).reset_index(drop=True)

    zero = mensal["precip_mm"] <= 1.0
    run_id = (zero != zero.shift()).cumsum()
    run_len = zero.groupby(run_id).transform("sum")
    falha_sensor = zero & (run_len >= 3)
    mensal.loc[falha_sensor, "precip_mm"] = np.nan

    grade = pd.MultiIndex.from_product([YEARS, range(1, 13)], names=["ano", "mes"])
    mensal = mensal.set_index(["ano", "mes"]).reindex(grade).reset_index()
    mensal["precip_imputada"] = mensal["precip_mm"].isna()

    colunas = ["precip_mm", "temp_media", "tmax_media", "dias_quentes"]
    medianas = mensal.groupby("mes")[colunas].median()
    for coluna in colunas:
        mensal[coluna] = mensal[coluna].fillna(mensal["mes"].map(medianas[coluna]))
    return mensal


def build_monthly(force: bool = False) -> pd.DataFrame:
    if MONTHLY_FILE.exists() and not force:
        print(f"Reaproveitando {MONTHLY_FILE.relative_to(DATA)}")
        return pd.read_csv(MONTHLY_FILE)

    mensal = _impute_monthly(pd.concat([process_year(y) for y in YEARS], ignore_index=True))
    PROCESSED.mkdir(parents=True, exist_ok=True)
    mensal.to_csv(MONTHLY_FILE, index=False)
    return mensal


def _window(mensal: pd.DataFrame, ano: int, months: list[int], ano_anterior: bool,
            column: str, how: str) -> float:
    year = ano - 1 if ano_anterior else ano
    block = mensal[(mensal["ano"] == year) & (mensal["mes"].isin(months))][column]
    if block.empty:
        return np.nan
    return float(block.sum() if how == "sum" else block.mean())


def build_annual(force: bool = False) -> pd.DataFrame:
    if ANNUAL_FILE.exists() and not force:
        print(f"Reaproveitando {ANNUAL_FILE.relative_to(DATA)}")
        return pd.read_csv(ANNUAL_FILE)

    mensal = build_monthly(force=force)
    rows = []
    for ano in YEARS:
        atual = mensal[mensal["ano"] == ano]
        if atual.empty:
            continue
        rows.append({
            "ano": ano,
            "precip_anual": float(atual["precip_mm"].sum()),
            "temp_media": float(atual["temp_media"].mean()),
            "tmax_media": float(atual["tmax_media"].mean()),
            "dias_quentes": float(atual["dias_quentes"].sum()),
            "meses_validos": len(atual),
            "meses_imputados": int(atual["precip_imputada"].sum()),
            "meses_observados": int((~atual["precip_imputada"]).sum()),
            "precip_floracao": _window(mensal, ano, [9, 10, 11], True, "precip_mm", "sum"),
            "precip_frutificacao": (
                _window(mensal, ano, [12], True, "precip_mm", "sum")
                + _window(mensal, ano, [1, 2, 3], False, "precip_mm", "sum")
            ),
            "precip_colheita": _window(mensal, ano, [4, 5, 6, 7, 8], False, "precip_mm", "sum"),
            "temp_floracao": _window(mensal, ano, [9, 10, 11], True, "temp_media", "mean"),
            "dias_quentes_colheita": _window(
                mensal, ano, [4, 5, 6, 7, 8], False, "dias_quentes", "sum"
            ),
        })
    out = pd.DataFrame(rows)
    out.to_csv(ANNUAL_FILE, index=False)
    return out


def add_anomalies(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy().sort_values("ano").reset_index(drop=True)
    for source in [
        "precip_anual", "temp_media", "dias_quentes",
        "precip_floracao", "precip_frutificacao", "precip_colheita",
        "temp_floracao",
    ]:
        mean = out[source].mean()
        std = out[source].std(ddof=1)
        std = np.nan if pd.isna(std) or std == 0 else std
        out[source + "_anom"] = (out[source] - mean) / std
    return out


def winsorize(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = frame.copy()
    for column in columns:
        lower, upper = out[column].quantile([0.01, 0.99])
        out[column] = out[column].clip(lower, upper)
    return out


def build_panel(force: bool = False) -> pd.DataFrame:
    if PANEL_FILE.exists() and not force:
        print(f"Reaproveitando {PANEL_FILE.relative_to(DATA)}")
        return pd.read_csv(PANEL_FILE)

    print("Consultando SIDRA (PAM e PPM) para Varginha...")
    pam = fetch_pam()
    ppm = fetch_ppm()
    climate = build_annual(force=force)
    print(f"PAM: {len(pam)} | PPM: {len(ppm)} | clima anual: {len(climate)}")

    yields = pam.pivot_table(
        index="ano", columns="cultura", values="rendimento", aggfunc="mean"
    ).reset_index()
    yields.columns.name = None
    yields = yields.rename(columns={
        "cafe": "rend_cafe",
        "milho": "rend_milho",
        "soja": "rend_soja",
    })

    panel = climate.merge(yields, on="ano", how="left", validate="one_to_one")
    panel = panel.merge(ppm, on="ano", how="left", validate="one_to_one")
    panel = add_anomalies(panel)
    panel["rebanho_anom"] = (
        panel["rebanho_bovino"] - panel["rebanho_bovino"].mean()
    ) / panel["rebanho_bovino"].std(ddof=1)
    panel["rend_cafe_anom"] = (
        panel["rend_cafe"] - panel["rend_cafe"].mean()
    ) / panel["rend_cafe"].std(ddof=1)
    panel = winsorize(panel, ["rend_cafe", "rend_milho", "rend_soja", "rebanho_bovino"])

    PROCESSED.mkdir(parents=True, exist_ok=True)
    panel.to_csv(PANEL_FILE, index=False)
    print(f"Painel salvo: {panel.shape[0]} linhas, {panel.shape[1]} colunas")
    return panel


def get_geojson() -> Path:
    if GEOJSON_FILE.exists():
        return GEOJSON_FILE
    print("Baixando geojson municipal do IBGE...")
    response = requests.get(GEOJSON_URL, timeout=180)
    response.raise_for_status()
    GEOJSON_FILE.write_text(response.text, encoding="utf-8")
    return GEOJSON_FILE


if __name__ == "__main__":
    build_panel(force="--force" in sys.argv)
