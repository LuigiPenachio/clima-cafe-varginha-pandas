"""Visualizações: mapa, climograma, séries, dispersões e testes."""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats

sys.stdout.reconfigure(encoding="utf-8")

from config import FIGURES, LATITUDE, LONGITUDE, MUNICIPIO_CODE
from etl import get_geojson

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "processed" / "painel_varginha.csv"
MONTHLY = ROOT / "data" / "processed" / "clima_varginha_mensal.csv"
OUTPUT = FIGURES

sns.set_theme(style="whitegrid", context="paper", font_scale=1.1)
MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
         "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def save(fig: plt.Figure, name: str) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / name
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"Figura salva: {path.relative_to(ROOT)}")


def mapa_localizacao() -> None:
    geo = gpd.read_file(get_geojson())
    geo["id"] = geo["id"].astype(str)
    mg = geo[geo["id"].str.startswith("31")].copy()
    destaque = mg[mg["id"] == MUNICIPIO_CODE]

    fig, ax = plt.subplots(figsize=(7, 6))
    mg.plot(color="#e8eef2", edgecolor="#9aa7ae", linewidth=0.3, ax=ax)
    destaque.plot(color="#c0392b", edgecolor="#7b241c", linewidth=0.8, ax=ax)
    ax.scatter([LONGITUDE], [LATITUDE], color="white", edgecolor="#4a235a",
               s=70, zorder=5, label="Estação A515")
    ax.set_title("Varginha e a estação meteorológica A515 (MG)")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(loc="lower left", frameon=True)
    ax.set_xlim(mg.total_bounds[0] - 0.2, mg.total_bounds[2] + 0.2)
    ax.set_ylim(mg.total_bounds[1] - 0.2, mg.total_bounds[3] + 0.2)
    save(fig, "01_mapa_varginha.png")


def climograma(mensal: pd.DataFrame) -> None:
    clim = mensal.groupby("mes").agg(
        precip=("precip_mm", "mean"), temp=("temp_media", "mean")
    )
    fig, ax1 = plt.subplots(figsize=(8, 4.5))
    bars = ax1.bar(clim.index, clim["precip"], color="#5b9bd5", alpha=0.85, label="Precipitação")
    ax1.set_xticks(range(1, 13), MESES)
    ax1.set_ylabel("Precipitação média (mm)", color="#2f5597")
    ax1.set_xlabel("Mês")
    ax1.tick_params(axis="y", labelcolor="#2f5597")
    ax2 = ax1.twinx()
    ax2.plot(clim.index, clim["temp"], color="#c0392b", marker="o", linewidth=2,
             label="Temperatura")
    ax2.set_ylabel("Temperatura média (°C)", color="#c0392b")
    ax2.tick_params(axis="y", labelcolor="#c0392b")
    ax1.set_title("Climatologia mensal em Varginha (2015–2025)")
    for bar in bars:
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 8,
                 f"{bar.get_height():.0f}", ha="center", fontsize=7)
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    save(fig, "02_climograma.png")


def serie_temporal(panel: pd.DataFrame) -> None:
    fig, ax1 = plt.subplots(figsize=(9, 4.5))
    color = "#2e7d32"
    ax1.bar(panel["ano"], panel["rend_cafe"], color=color, alpha=0.8, label="Rendimento do café")
    ax1.set_ylabel("Rendimento do café (kg/ha)", color=color)
    ax1.tick_params(axis="y", labelcolor=color)
    ax1.set_xticks(panel["ano"])
    ax1.set_xlabel("Ano")
    ax2 = ax1.twinx()
    ax2.plot(panel["ano"], panel["precip_anual_anom"], color="#e67e22", marker="o",
             linewidth=2, label="Anomalia de precipitação")
    ax2.axhline(0, color="grey", linestyle="--", linewidth=1)
    ax2.set_ylabel("Anomalia de precipitação (z)", color="#e67e22")
    ax2.tick_params(axis="y", labelcolor="#e67e22")
    ax1.set_title("Rendimento do café e anomalia de chuva em Varginha")
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    save(fig, "03_serie_rendimento_clima.png")


def dispersao(panel: pd.DataFrame, x: str, y: str, nome: str, arquivo: str) -> None:
    data = panel[[x, y]].dropna()
    slope, intercept, r, p, _ = stats.linregress(data[x], data[y])
    grid = np.linspace(data[x].min(), data[x].max(), 50)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.scatter(data[x], data[y], s=70, color="#2c3e50", alpha=0.8, edgecolor="white")
    ax.plot(grid, intercept + slope * grid, color="#c0392b", linewidth=2,
            label=f"r={r:.2f}, p={p:.3f}")
    ax.axhline(0, color="grey", linewidth=0.8, linestyle=":")
    ax.axvline(0, color="grey", linewidth=0.8, linestyle=":")
    ax.set_xlabel(x.replace("_anom", " (anomalia z)"))
    ax.set_ylabel(y.replace("_anom", " (anomalia z)"))
    ax.set_title(nome)
    ax.legend(frameon=True)
    save(fig, arquivo)


def boxplot_grupos(panel: pd.DataFrame) -> None:
    def group(value: float) -> str:
        if value < -0.5:
            return "Seco"
        if value > 0.5:
            return "Chuvoso"
        return "Normal"

    data = panel.copy()
    data["grupo"] = data["precip_anual_anom"].map(group)
    order = ["Seco", "Normal", "Chuvoso"]
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    sns.boxplot(data=data, x="grupo", y="rend_cafe_anom", order=order,
                hue="grupo", palette="Set2", legend=False, ax=ax, width=0.5)
    sns.stripplot(data=data, x="grupo", y="rend_cafe_anom", order=order,
                  color="#34495e", size=6, ax=ax, jitter=True)
    ax.set_xlabel("Anomalia anual de precipitação")
    ax.set_ylabel("Anomalia do rendimento do café (z)")
    ax.set_title("Rendimento do café por classe de precipitação")
    save(fig, "06_boxplot_anos_secos.png")


def comparacao_culturas(panel: pd.DataFrame) -> None:
    columns = {
        "rend_cafe": "Café",
        "rend_milho": "Milho",
        "rend_soja": "Soja",
        "rebanho_bovino": "Rebanho bovino",
    }
    indexed = panel.set_index("ano")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    for column, label in columns.items():
        series = indexed[column] / indexed[column].iloc[0] * 100
        ax.plot(series.index, series.values, marker="o", linewidth=1.8, label=label)
    ax.axhline(100, color="grey", linestyle="--", linewidth=1)
    ax.set_xticks(indexed.index)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Índice (2015 = 100)")
    ax.set_title("Produção agropecuária municipal: índice por cultura")
    ax.legend(ncol=4, frameon=False)
    save(fig, "07_indice_culturas.png")


def heatmap(panel: pd.DataFrame) -> None:
    columns = [
        "precip_anual_anom", "precip_floracao_anom", "precip_frutificacao_anom",
        "temp_media_anom", "temp_floracao_anom", "dias_quentes_anom",
        "rend_cafe_anom", "rend_milho", "rend_soja", "rebanho_anom",
    ]
    corr = panel[columns].corr(method="spearman")
    labels = {
        "precip_anual_anom": "Chuva anual",
        "precip_floracao_anom": "Chuva floração",
        "precip_frutificacao_anom": "Chuva frutificação",
        "temp_media_anom": "Temp. média",
        "temp_floracao_anom": "Temp. floração",
        "dias_quentes_anom": "Dias quentes",
        "rend_cafe_anom": "Café",
        "rend_milho": "Milho",
        "rend_soja": "Soja",
        "rebanho_anom": "Rebanho",
    }
    corr = corr.rename(index=labels, columns=labels)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
                vmin=-1, vmax=1, square=True, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title("Correlação de Spearman entre clima e produção (Varginha)")
    save(fig, "08_heatmap_correlacoes.png")


def rebanho_lag(panel: pd.DataFrame) -> None:
    data = panel.copy()
    data["precip_lag1"] = data["precip_anual_anom"].shift(1)
    data = data.dropna(subset=["precip_lag1", "rebanho_anom"])
    slope, intercept, r, p, _ = stats.linregress(data["precip_lag1"], data["rebanho_anom"])
    grid = np.linspace(data["precip_lag1"].min(), data["precip_lag1"].max(), 50)
    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.scatter(data["precip_lag1"], data["rebanho_anom"], s=70, color="#6c3483",
               alpha=0.85, edgecolor="white")
    ax.plot(grid, intercept + slope * grid, color="#c0392b", linewidth=2,
            label=f"r={r:.2f}, p={p:.3f}, R²={r**2:.2f}")
    ax.set_xlabel("Anomalia de precipitação no ano anterior (z)")
    ax.set_ylabel("Anomalia do rebanho bovino (z)")
    ax.set_title("Rebanho bovino responde à chuva do ano anterior")
    ax.legend(frameon=True)
    save(fig, "09_rebanho_chuva_atrasada.png")


def janelas_mensais() -> None:
    mensal = pd.read_csv(MONTHLY)
    panel = pd.read_csv(PANEL)[["ano", "rend_cafe_anom"]]
    data = mensal.merge(panel, on="ano")
    values = []
    for mes, group in data.groupby("mes"):
        anomaly = (group["precip_mm"] - group["precip_mm"].mean()) / group["precip_mm"].std()
        values.append(stats.spearmanr(anomaly, group["rend_cafe_anom"]).statistic)
    colors = ["#c0392b" if v < 0 else "#2e7d32" for v in values]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(range(1, 13), values, color=colors, alpha=0.85)
    ax.axhline(0, color="grey", linewidth=1)
    ax.set_xticks(range(1, 13), MESES)
    ax.set_xlabel("Mês")
    ax.set_ylabel("ρ de Spearman")
    ax.set_title("Correlação exploratória: chuva mensal × rendimento do café")
    save(fig, "10_janelas_mensais.png")


def run() -> None:
    panel = pd.read_csv(PANEL)
    mensal = pd.read_csv(MONTHLY)
    mapa_localizacao()
    climograma(mensal)
    serie_temporal(panel)
    dispersao(
        panel, "precip_anual_anom", "rend_cafe_anom",
        "Chuva anual × rendimento do café", "04_dispersao_chuva_cafe.png",
    )
    dispersao(
        panel, "temp_floracao_anom", "rend_cafe_anom",
        "Calor na floração × rendimento do café", "05_dispersao_calor_cafe.png",
    )
    boxplot_grupos(panel)
    comparacao_culturas(panel)
    heatmap(panel)
    rebanho_lag(panel)
    janelas_mensais()


if __name__ == "__main__":
    run()
