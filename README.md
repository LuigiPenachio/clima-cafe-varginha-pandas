# Clima e cafeicultura em Varginha/MG (2015–2025)

Análise de dados aplicada com Python e Pandas cruzando dados meteorológicos do INMET com estatísticas agropecuárias municipais do IBGE (PAM e PPM), com foco na cafeicultura do Sul de Minas.

**Repositório:** https://github.com/LuigiPenachio/clima-cafe-varginha-pandas

## Perguntas de pesquisa

- P1: anomalias de precipitação e temperatura explicam variações anuais do rendimento do café em Varginha?
- P2: existem janelas fenológicas (floração, frutificação, colheita) mais sensíveis ao clima?
- P3: o rebanho bovino municipal responde à precipitação do ano anterior?

## Bases e chave de junção

| Base | Origem | Unidade observada | Variáveis |
|---|---|---|---|
| INMET BDMEP (estação automática **A515 — Varginha**) | `portal.inmet.gov.br/uploads/dadoshistoricos/{ano}.zip` | hora → dia → mês → ano | precipitação, temperatura média/máx./mín., dias com Tmáx > 35 °C |
| IBGE PAM (tabela SIDRA **5457**, produto **Café em grão — total**, código 40139; milho 40122; soja 40124) | API SIDRA, nível municipal **3170701** | município/ano | rendimento médio (kg/ha) |
| IBGE PPM (tabela SIDRA **3939**, rebanho bovino, código 2670) | API SIDRA, nível municipal **3170701** | município/ano | efetivo de bovinos (cabeças em 31/12) |

**Chave de junção: `ano`.** Justificativa: a estação A515 está localizada no próprio município de Varginha (meta-dados do INMET: latitude −21,5664, longitude −45,4042), e PAM/PPM são levantadas na unidade municipal. Com apenas uma estação e um município, `ano` é a chave natural e garante o alinhamento temporal entre clima e safra. As janelas fenológicas usam o ano anterior quando necessário (ex.: floração do café em set–nov do ano que antecede a colheita).

## Estrutura

```
src/
  config.py      parâmetros (anos, códigos SIDRA, caminhos)
  download.py    download dos ZIPs anuais do INMET (paralelo, com cache)
  etl.py         extração, limpeza, agregação e junção
  analysis.py    estatística descritiva, correlação, OLS, Mann-Whitney
  plots.py       10 visualizações
  main.py        orquestrador
data/raw/        ZIPs do INMET e geojson municipal (cache)
data/processed/  painel e tabelas intermediárias
output/figures/  figuras PNG
output/tables/   resultados estatísticos CSV/TXT
```

`data/processed/` também guarda `clima_uf_ano.csv` e `painel_uf_ano.csv` (294 linhas cada, 27 UFs × 11 anos), resquícios de uma análise exploratória por estado feita antes de o recorte ser fixado em Varginha. Não entram no resultado final.

## Como executar

```bash
python -m pip install -r requirements.txt
python src/download.py       # uma vez; ~1,1 GB, agora 11 anos (2015–2025)
python src/main.py           # ETL + estatística + figuras
```

Para refazer tudo do zero: `python src/main.py --force`.
Para alterar o período: defina `ANALYSIS_YEARS=2015-2025` (ou `INMET_YEARS` no download).

O download do INMET é o único passo pesado; as etapas seguintes usam cache em `data/processed` e terminam em segundos. O geojson municipal é baixado automaticamente na primeira execução das figuras.

## Pipeline de ETL

1. **Extract:** 11 ZIPs anuais do INMET + 2 consultas à API SIDRA.
2. **Limpeza:** leitura dos CSVs Latin-1 com 9 linhas de metadados, conversão de decimais e datas dos dois layouts (até 2018: `AAAA-MM-DD HH:MM` e `-9999`; desde 2019: `AAAA/MM/DD HHMM UTC` e campo vazio), remoção de `-9999`/vazios, dias com menos de 6 horas válidas descartados, meses com menos de 15 dias válidos descartados.
3. **Agregação:** média/max/soma horária → diária → mensal → anual; cálculo de anomalias z por variável (baseline 2015–2025) e de janelas fenológicas do café.
4. **Tratamento de outliers:** winsorização nos percentis 1%/99% das variáveis de produção.
5. **Tratamento de falha de sensor:** a estação A515 registrou 0 mm por sequências de ≥3 meses (mai–jul/2019, mai–jul/2022, mai–dez/2023 e jan–mar/2024), incompatíveis com a climatologia local. Esses meses e os meses ausentes (ago/2016, dez/2025) foram imputados pela mediana mensal do período e sinalizados em `precip_imputada`/`meses_imputados` (19 meses imputados no total).
6. **Load:** `data/processed/painel_varginha.csv` (11 linhas × 26 colunas).

## Resultados principais

- Rendimento médio do café: **1.567 kg/ha** (1.038–2.122 kg/ha); precipitação anual média pós-imputação: **1.048 mm** (728–1.476 mm).
- Correlação de Spearman entre chuva anual e rendimento do café: **ρ = 0,27 (p = 0,42)** — não significativa. Melhor janela exploratória: chuva de janeiro, ρ = 0,45 (p = 0,17).
- Calor na floração: **ρ = −0,42 (p = 0,23)** — direção esperada, mas não significativa com n = 10.
- Mann-Whitney entre anos secos e chuvosos: **U = 5,5; p = 1,00**.
- Rebanho bovino vs. chuva do ano anterior: **β = 0,03; R² = 0,001; p = 0,94** — sem associação (o resultado significativo anterior era artefato dos zeros espúrios).
- Sensibilidade excluindo anos com falha longa (n = 7): chuva anual ρ = 0,23 (p = 0,61); temperatura na floração ρ = −0,89 (p = 0,019), resultado exploratório sujeito a viés de seleção e multiplicidade de testes.

## Artigo e direcionamento editorial

O artigo está em `artigo_sbc/artigo.tex`, usando o modelo oficial da SBC (`sbc-template.sty` e `sbc.bst` incluídos, obtidos do repositório do template). Autores e e-mails já preenchidos (Luigi, Rafael e, por último, os professores Eduardo e Marcelo). Para conferir a formatação no Overleaf, importe `artigo_sbc/artigo_sbc_overleaf.zip`; a versão RBCA correspondente está em `artigo_rbca/artigo_rbca_overleaf.zip`. Os PDFs antigos foram removidos para recompilação com os e-mails reais. A compilação local requer uma distribuição LaTeX com `pdflatex`.

A versão para submissão à revista está em `artigo_rbca/artigo_rbca.tex`, adaptada às normas da RBCA (resumo ≤200 palavras, três palavras-chave, citações ABNT numéricas com `abntex2cite`, página 19×29 cm). A classe `RBCA.cls` incluída é a oficial (v0.5, 13/08/2013), extraída do ZIP do modelo que está na raiz; o modelo original está em `artigo_rbca/modelo_oficial/`. O PDF `xggxhscsnvby.pdf` na raiz é só o guia compilado. Confira se existe versão mais recente no OJS antes de submeter. O OJS da RBCA informa 8–15 páginas e, em 24/11/2026, indicava que a revista não estava aceitando submissões — confira antes de enviar.

Periódico escolhido: **RBCA — Revista Brasileira de Computação Aplicada (UPF)**. Justificativa: o trabalho é aplicado, centrado em pipeline computacional, integração de bases abertas e análise estatística, o que se alinha ao escopo da RBCA (que cita explicitamente computação aplicada à agricultura); a RITA tem perfil mais teórico e não lista agricultura no escopo. A RBCA é mais fácil no aceite temático, porém mais exigente na formatação. Os comprovantes de submissão (CSBC e periódico) devem ser anexados pelo discente após o envio.

Como as submissões da RBCA estão suspensas desde 29/08/2026, preparou-se também a versão para a **RITA** em `artigo_rita/artigo_rita.tex` (mesmo conteúdo, com a seção obrigatória "Declaration of AI-Assisted Use in Writing" antes das referências). O link antigo do modelo LaTeX da RITA está indisponível (404), mas o `RITA.cls` oficial foi obtido do modelo baixado do Overleaf. O ZIP `artigo_rita/artigo_rita_overleaf.zip` reúne texto, referências, figuras, `RITA.cls` e os arquivos `abntex2` — basta importá-lo no Overleaf e compilar (`artigo_rita.tex` é o arquivo principal).

## Limitações

- Apenas 11 observações anuais: baixo poder estatístico; nenhuma regressão atingiu significância na amostra completa.
- 19 meses de precipitação imputados por falha de sensor; 2023 tem 8 meses imputados, portanto sua anomalia é incerta.
- Uma única estação não capta a heterogeneidade espacial do município.
- Ano civil do SIDRA vs. ciclo fenológico do café (colheita abril–agosto).
- Confusão não controlada: preço do café, área colhida, tecnologia, pragas, secas anteriores e mudanças de cultivar.
- Dados de 2025 são preliminares no SIDRA.
- Correlação observacional não implica causalidade; o teste de janelas mensais é exploratório e sofre com multiplicidade de comparações.
