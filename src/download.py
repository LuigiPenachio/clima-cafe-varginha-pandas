"""Download anual dos arquivos ZIP de estações automáticas do INMET (BDMEP)."""

from __future__ import annotations

import os
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
URL_TEMPLATE = "https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip"


def _years_from_env() -> list[int]:
    raw = os.getenv("INMET_YEARS", "2015-2025")
    if "-" in raw:
        start, end = (int(x) for x in raw.split("-"))
        return list(range(start, end + 1))
    return [int(x) for x in raw.split(",") if x.strip()]


def download_year(year: int, dest_dir: Path = RAW_DIR) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    final = dest_dir / f"{year}.zip"
    if final.exists() and zipfile.is_zipfile(final):
        print(f"[{year}] já presente, pulando")
        return final

    url = URL_TEMPLATE.format(year=year)
    tmp = dest_dir / f"{year}.zip.part"
    for attempt in range(1, 4):
        try:
            with requests.get(url, stream=True, timeout=(30, 300)) as response:
                response.raise_for_status()
                total = int(response.headers.get("Content-Length", 0))
                done = 0
                started = time.time()
                with tmp.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=1 << 20):
                        if chunk:
                            handle.write(chunk)
                            done += len(chunk)
            if not zipfile.is_zipfile(tmp):
                raise ValueError("arquivo baixado não é um ZIP válido")
            tmp.replace(final)
            print(f"[{year}] {done / 1e6:.1f} MB em {time.time() - started:.0f}s")
            return final
        except Exception as exc:
            print(f"[{year}] tentativa {attempt} falhou: {exc}")
            tmp.unlink(missing_ok=True)
            time.sleep(2 * attempt)
    raise RuntimeError(f"Não foi possível baixar {year}")


def main() -> None:
    years = _years_from_env()
    workers = int(os.getenv("INMET_DOWNLOAD_WORKERS", "6"))
    print(f"Baixando {len(years)} anos com {workers} workers")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(download_year, y): y for y in years}
        for future in as_completed(futures):
            year = futures[future]
            try:
                future.result()
            except Exception as exc:
                print(f"[{year}] ERRO: {exc}")


if __name__ == "__main__":
    main()
