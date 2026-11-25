"""Análise estatística: correlação, regressão OLS e teste de hipótese."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "processed" / "painel_varginha.csv"
TABLES = Path(__file__).resolve().parents[1] / "output" / "tables"

CLIMATE_ANOM = [
    "precip_anual_anom", "temp_media_anom", "dias_quentes_anom",
    "precip_floracao_anom", "precip_frutificacao_anom",
    "precip_colheita_anom", "temp_floracao_anom",
]


def _text(line: str = "") -> None:
    print(line)


def descriptive(panel: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "precip_anual", "temp_media", "dias_quentes", "rend_cafe",
        "rend_milho", "rend_soja", "rebanho_bovino",
    ]
    desc = panel[columns].agg(["mean", "std", "min", "max"]).T
    return desc.round(2)


def correlations(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in CLIMATE_ANOM:
        pair = panel[[column, "rend_cafe_anom"]].dropna()
        pearson_r, pearson_p = stats.pearsonr(pair[column], pair["rend_cafe_anom"])
        spearman_r, spearman_p = stats.spearmanr(pair[column], pair["rend_cafe_anom"])
        rows.append({
            "variavel": column,
            "n": len(pair),
            "pearson_r": round(pearson_r, 3),
            "pearson_p": round(pearson_p, 4),
            "spearman_rho": round(spearman_r, 3),
            "spearman_p": round(spearman_p, 4),
        })
    return pd.DataFrame(rows).sort_values("spearman_rho", ascending=False)


def regressions(panel: pd.DataFrame) -> list[tuple[str, object]]:
    models = [
        ("M1: anomalia de chuva anual", "rend_cafe_anom ~ precip_anual_anom"),
        ("M2: chuva na frutificacao + calor na floracao",
         "rend_cafe_anom ~ precip_frutificacao_anom + temp_floracao_anom"),
        ("M3: termo quadratico da chuva anual",
         "rend_cafe_anom ~ precip_anual_anom + I(precip_anual_anom ** 2)"),
        ("M4: chuva de janeiro (janela exploratoria)",
         "rend_cafe_anom ~ precip_jan_anom"),
    ]
    return [(name, smf.ols(formula, data=panel).fit()) for name, formula in models]


def mann_whitney(panel: pd.DataFrame) -> tuple[float, float, dict]:
    seco = panel.loc[panel["precip_anual_anom"] < -0.5, "rend_cafe_anom"]
    chuvoso = panel.loc[panel["precip_anual_anom"] > 0.5, "rend_cafe_anom"]
    normal = panel.loc[panel["precip_anual_anom"].between(-0.5, 0.5), "rend_cafe_anom"]
    statistic, pvalue = stats.mannwhitneyu(seco, chuvoso, alternative="two-sided")
    return statistic, pvalue, {
        "seco": list(seco.round(3)), "normal": list(normal.round(3)),
        "chuvoso": list(chuvoso.round(3)),
    }


def cattle_lag(panel: pd.DataFrame) -> object:
    data = panel.copy()
    data["precip_lag1"] = data["precip_anual_anom"].shift(1)
    data = data.dropna(subset=["precip_lag1", "rebanho_anom"])
    return smf.ols("rebanho_anom ~ precip_lag1", data=data).fit()


def sensitivity(panel: pd.DataFrame) -> tuple[list[int], list[str]]:
    clean = panel[panel["meses_imputados"] < 3]
    lines = [f"Anos sem falha longa de precipitação (n={len(clean)}): "
             f"{', '.join(str(a) for a in clean['ano'])}"]
    for column in ["precip_anual_anom", "temp_floracao_anom"]:
        pair = clean[[column, "rend_cafe_anom"]].dropna()
        rho, pvalue = stats.spearmanr(pair[column], pair["rend_cafe_anom"])
        lines.append(f"  {column}: rho={rho:.3f}, p={pvalue:.4f}, n={len(pair)}")
    return list(clean["ano"]), lines


def monthly_windows() -> pd.DataFrame:
    monthly = pd.read_csv(
        Path(__file__).resolve().parents[1] / "data" / "processed"
        / "clima_varginha_mensal.csv"
    )
    panel = pd.read_csv(PANEL)[["ano", "rend_cafe_anom"]]
    monthly = monthly.merge(panel, on="ano")
    rows = []
    for mes, group in monthly.groupby("mes"):
        anomaly = (group["precip_mm"] - group["precip_mm"].mean()) / group["precip_mm"].std()
        rho, p = stats.spearmanr(anomaly, group["rend_cafe_anom"])
        rows.append({"mes": mes, "spearman_rho": round(rho, 3), "p": round(p, 4)})
    return pd.DataFrame(rows)


def run() -> None:
    panel = pd.read_csv(PANEL)
    jan = pd.read_csv(
        Path(__file__).resolve().parents[1] / "data" / "processed"
        / "clima_varginha_mensal.csv"
    )
    jan = jan[jan["mes"] == 1][["ano", "precip_mm"]].rename(
        columns={"precip_mm": "precip_jan"}
    )
    panel = panel.merge(jan, on="ano", how="left")
    panel["precip_jan_anom"] = (
        (panel["precip_jan"] - panel["precip_jan"].mean())
        / panel["precip_jan"].std(ddof=1)
    )

    TABLES.mkdir(parents=True, exist_ok=True)
    desc = descriptive(panel)
    corr = correlations(panel)
    corr.to_csv(TABLES / "correlacoes.csv", index=False)
    desc.to_csv(TABLES / "estatistica_descritiva.csv")

    lines: list[str] = []
    lines.append("=== ESTATÍSTICA DESCRITIVA (Varginha, 2015-2025) ===")
    lines.append(desc.to_string())
    lines.append("")
    lines.append("=== CORRELAÇÃO COM O RENDIMENTO DO CAFÉ ===")
    lines.append(corr.to_string(index=False))
    lines.append("")

    lines.append("=== JANELAS MENSAIS DE PRECIPITAÇÃO (exploratório) ===")
    windows = monthly_windows()
    lines.append(windows.to_string(index=False))
    lines.append("")

    lines.append("=== REGRESSÕES OLS ===")
    for name, model in regressions(panel):
        lines.append(f"\n{name}")
        lines.append(f"  R2={model.rsquared:.3f}  R2_adj={model.rsquared_adj:.3f}  "
                     f"F_p={model.f_pvalue:.4f}  n={int(model.nobs)}")
        for variable, beta in model.params.items():
            lines.append(f"  {variable}: beta={beta:.3f}, p={model.pvalues[variable]:.4f}")

    lines.append("\n=== TESTE DE MANN-WHITNEY (anos secos x chuvosos) ===")
    u, p, groups = mann_whitney(panel)
    lines.append(f"U={u:.1f}, p={p:.4f}")
    lines.append(f"  secos={groups['seco']}  normais={groups['normal']}  chuvosos={groups['chuvoso']}")

    lines.append("\n=== REBANHO BOVINO x CHUVA DO ANO ANTERIOR ===")
    cattle = cattle_lag(panel)
    lines.append(f"R2={cattle.rsquared:.3f}  beta={cattle.params['precip_lag1']:.3f}  "
                 f"p={cattle.pvalues['precip_lag1']:.4f}  n={int(cattle.nobs)}")

    lines.append("\n=== ANÁLISE DE SENSIBILIDADE (sem anos com falha longa) ===")
    _, sens = sensitivity(panel)
    lines.extend(sens)

    text = "\n".join(lines)
    (TABLES / "resultados_estatisticos.txt").write_text(text, encoding="utf-8")
    _text(text)


if __name__ == "__main__":
    run()
