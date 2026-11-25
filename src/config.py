"""Configurações centrais do projeto (recorte: Varginha/MG)."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"
FIGURES = ROOT / "output" / "figures"
TABLES = ROOT / "output" / "tables"

YEARS = [int(y) for y in os.getenv("ANALYSIS_YEARS", "2015-2025").split("-")]
if len(YEARS) == 2 and YEARS[0] <= YEARS[1]:
    YEARS = list(range(YEARS[0], YEARS[1] + 1))
elif len(YEARS) != 1:
    YEARS = [int(y) for y in os.getenv("ANALYSIS_YEARS", "2015").split(",")]

MUNICIPIO = "Varginha"
MUNICIPIO_CODE = "3170701"
UF = "MG"
ESTACAO_CODE = "A515"
LATITUDE = -21.56638888
LONGITUDE = -45.40416666

SIDRA_BASE = "https://apisidra.ibge.gov.br/values/"
PAM_TABLE = 5457
PAM_CLASS = 782
PRODUCT_CODES = {
    "cafe": 40139,
    "milho": 40122,
    "soja": 40124,
}
PPM_TABLE = 3939
PPM_CLASS = 79
BOVINO_CODE = 2670

GEOJSON_URL = (
    "https://raw.githubusercontent.com/tbrugz/geodata-br/master/"
    "geojson/geojs-100-mun.json"
)
