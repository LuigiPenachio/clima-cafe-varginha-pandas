"""Executa ETL, análise estatística e visualizações em sequência."""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8")

import analysis
import etl
import plots


def main() -> None:
    force = "--force" in sys.argv
    print("=== 1/3 ETL ===")
    etl.build_panel(force=force)
    print("\n=== 2/3 ANÁLISE ESTATÍSTICA ===")
    analysis.run()
    print("\n=== 3/3 VISUALIZAÇÕES ===")
    plots.run()
    print("\nConcluído. Resultados em data/processed e output/.")


if __name__ == "__main__":
    main()
