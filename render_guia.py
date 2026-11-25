"""Renderiza entendendo_o_trabalho.md em HTML e PDF (para leitura/impressão).

Uso:
    python render_guia.py

Dependência: pip install markdown
O PDF é gerado com o Chrome/Edge instalado (modo headless).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "entendendo_o_trabalho.md"
HTML = ROOT / "entendendo_o_trabalho.html"
PDF = ROOT / "entendendo_o_trabalho.pdf"

BROWSERS = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
]

CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body {
  margin: 0;
  background: #eef1f5;
  color: #1f2933;
  font-family: "Segoe UI", "Microsoft YaHei", Tahoma, sans-serif;
  font-size: 16px;
  line-height: 1.65;
}
.wrap {
  max-width: 1040px;
  margin: 28px auto;
  padding: 36px 48px 64px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 18px rgba(0,0,0,.09);
}
h1 { font-size: 2em; color: #123; border-bottom: 3px solid #2f6f9f; padding-bottom: .3em; }
h2 { font-size: 1.5em; color: #14364f; border-bottom: 1px solid #ccd6de; padding-bottom: .2em; margin-top: 2em; }
h3 { font-size: 1.2em; color: #1c4f70; margin-top: 1.8em; }
h4 { font-size: 1.05em; color: #2c3e50; margin-top: 1.4em; }
p, li { text-align: justify; }
a { color: #1b5e9e; text-decoration: none; }
a:hover { text-decoration: underline; }
code {
  font-family: Consolas, "Courier New", monospace;
  font-size: .9em;
  background: #f1f4f7;
  padding: .1em .35em;
  border-radius: 4px;
}
pre {
  background: #17212b;
  color: #e6edf3;
  padding: 16px 18px;
  border-radius: 8px;
  overflow-x: auto;
  line-height: 1.45;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
pre code { background: none; color: inherit; padding: 0; font-size: .88em; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 1.2em 0;
  font-size: .92em;
  page-break-inside: avoid;
}
th, td { border: 1px solid #cbd5df; padding: 7px 10px; vertical-align: top; text-align: left; }
th { background: #dce9f3; color: #123; position: sticky; top: 0; }
tbody tr:nth-child(even) { background: #f7f9fb; }
blockquote {
  margin: 1.2em 0;
  padding: .6em 1.2em;
  border-left: 4px solid #2f6f9f;
  background: #f2f7fb;
}
details { background: #f7f9fb; border: 1px solid #d7e0e8; border-radius: 8px; padding: 10px 16px; }
summary { cursor: pointer; font-weight: 600; color: #14364f; }
details ul { columns: 2; column-gap: 32px; margin-bottom: .4em; }
details li { break-inside: avoid; }
hr { border: 0; border-top: 1px solid #d7e0e8; margin: 2em 0; }
.header-note { color: #637282; font-size: .85em; text-align: right; margin-bottom: 1.5em; }

@media print {
  body { background: #fff; font-size: 10.5pt; }
  .wrap { margin: 0; padding: 0; box-shadow: none; max-width: none; }
  .header-note { display: none; }
  details { display: none; }
  h1, h2, h3, h4 { break-after: avoid; }
  pre, table, blockquote { break-inside: avoid; }
  tr, img { break-inside: avoid; }
  @page { size: A4; margin: 18mm 16mm; }
}
"""


def build_html() -> str:
    source = SOURCE.read_text(encoding="utf-8")
    converter = markdown.Markdown(
        extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"],
        extension_configs={"toc": {"permalink": False}},
    )
    body = converter.convert(source)
    toc = converter.toc
    return (
        "<!DOCTYPE html>\n<html lang=\"pt-BR\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<title>Guia completo do trabalho — Varginha/MG</title>\n"
        "<style>" + CSS + "</style>\n"
        "</head>\n<body>\n<div class=\"wrap\">\n"
        "<div class=\"header-note\">Gerado a partir de entendendo_o_trabalho.md</div>\n"
        "<details><summary>Índice (clique para abrir)</summary>" + toc + "</details>\n"
        + body + "\n</div>\n</body>\n</html>\n"
    )


def find_browser() -> Path | None:
    return next((p for p in BROWSERS if p.exists()), None)


def main() -> None:
    HTML.write_text(build_html(), encoding="utf-8")
    print(f"HTML pronto: {HTML.name}")

    browser = find_browser()
    if browser is None:
        print("Navegador não encontrado; PDF não gerado. Abra o HTML no navegador e use Imprimir > Salvar como PDF.")
        return

    profile = ROOT / ".render_guia_profile"
    command = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={profile}",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF}",
        HTML.resolve().as_uri(),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    if profile.exists():
        import shutil

        shutil.rmtree(profile, ignore_errors=True)
    if PDF.exists() and PDF.stat().st_size > 1000:
        print(f"PDF pronto: {PDF.name} ({PDF.stat().st_size / 1e6:.1f} MB)")
    else:
        print("Falha ao gerar PDF.", result.stderr[-800:])
        sys.exit(1)


if __name__ == "__main__":
    main()
