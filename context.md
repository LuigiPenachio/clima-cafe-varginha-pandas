# context.md — contexto interno do projeto (somente para contextualizar IAs)

> **Aviso:** este arquivo é documentação interna, criada **exclusivamente para dar contexto a assistentes de inteligência artificial** que continuarem o trabalho. Ele **não** é parte do artigo científico, da apresentação nem da avaliação da disciplina. Foi versionado no Git apenas para que uma IA possa recuperar o histórico de decisões e valores corretos.

Este arquivo é a fonte de verdade sobre o projeto. **Leia antes de alterar qualquer coisa.** Ele registra o que já foi feito, as decisões tomadas, os valores corretos dos resultados e o que ainda falta.

## 1. Identidade do trabalho

- **Disciplina:** G08PCOM3.01 — Programação de Computadores III — T01 (2026.2), UFCIMG (Campus Varginha).
- **Tarefa:** Programação Matemática e Estatística com Pandas — Análise de dados aplicada.
- **Tema da dupla:** clima e agropecuária.
- **Recorte final:** município de **Varginha/MG** (Sul de Minas), **2015–2025**, com foco na **cafeicultura** (milho, soja e rebanho bovino como comparação).
- **Autores do artigo (ordem obrigatória):** Luigi Miranda Penachio, Rafael de Paiva Perim, Eduardo Gomes Carvalho, Marcelo Mussel. Os **dois últimos são os professores responsáveis** — exigência explícita da tarefa. Os e-mails no `.tex` já foram preenchidos: Luigi `luigimiranda2003@gmail.com`, Rafael `rafaelperim6@gmail.com`, Eduardo `eduardogomes@cefetmg.br`, Marcelo `marcelo.mussel@gmail.com`.
- **Etapa 1 (proposta):** já apresentada em sala pelo discente. **Não refazer.**
- Há também `entendendo_o_trabalho.md`, guia detalhado em linguagem simples (bases, código, resultados, limitações). **Não contém roteiro de slides** — o discente fará os slides depois.

## 2. Bases de dados e chaves

| Base | Fonte | Código/chave | Uso |
|---|---|---|---|
| INMET BDMEP, estação automática **A515 Varginha** (`-21,5664`, `-45,4042`) | `https://portal.inmet.gov.br/uploads/dadoshistoricos/{ano}.zip` | estação A515 | temperatura, precipitação, dias com Tmáx > 35 °C |
| IBGE **PAM**, tabela SIDRA **5457**, classificação **782** | API `https://apisidra.ibge.gov.br/values/` | município **3170701**; café total **40139**, milho **40122**, soja **40124** | rendimento médio (kg/ha) |
| IBGE **PPM**, tabela SIDRA **3939** | mesma API | município 3170701, bovinos **2670** | efetivo de bovinos em 31/12 |

**Chave de junção: `ano`.** Justificativa: a estação A515 está dentro do próprio município de Varginha; PAM/PPM são municipais; com uma estação e um município, o ano é a chave natural. Janelas de floração do café usam o **ano anterior** (set–nov), frutificação usa dez/ano anterior + jan–mar, colheita usa abr–ago.

**Atenção com a API SIDRA:** o cabeçalho do JSON às vezes vem com nomes legíveis e às vezes com códigos `D1N`, `D4N` etc. O código normaliza sempre para 13 colunas canônicas por posição. O ano da PAM está em `D4N`, não em `D3N`.

## 3. Estrutura de arquivos

```
raiz = C:\Users\User\Downloads\dados com pandas
proposta_clima_agropecuaria.md   proposta da Etapa 1 (já apresentada)
apresentacao.pdf                 10 slides da apresentação final
README.md                        instruções, resultados, justificativa da RBCA
requirements.txt                 dependências
src/config.py                    constantes, códigos, caminhos, anos
src/download.py                  download paralelo dos 11 ZIPs do INMET (cache)
src/etl.py                       extração/limpeza/agregação/imputação/junção
src/analysis.py                  descritiva, correlação, OLS, Mann-Whitney, sensibilidade
src/plots.py                     10 figuras
src/main.py                      orquestrador (ETL → análise → figuras)
data/raw/                        11 ZIPs (~1,1 GB) + geojson municipal (já baixados)
data/processed/                  painel e tabelas intermediárias
output/figures/                  10 PNGs
output/tables/                   resultados_estatisticos.txt, correlacoes.csv, etc.
artigo_sbc/                       versão SBC (disciplina)
  artigo.tex                      artigo no template oficial da SBC
  sbc-template.sty, sbc.bst       template oficial
  artigo_bib.bib                  referências
  figuras/                        4 figuras referenciadas (01, 02, 04, 09)
  artigo_sbc.pdf                  PDF final (7 páginas)
  artigo_sbc_overleaf.zip         ZIP para importar no Overleaf
artigo_rbca/                      segunda versão, formatada para a RBCA
  artigo_rbca.tex                 artigo adaptado às normas da RBCA
  RBCA.cls                        classe oficial (v0.5, 13/08/2013)
  abntex2*                        pacote/estilo ABNT numérico baixados do abnTeX2
  figuras/                        10 figuras usadas na versão RBCA
  modelo_oficial/                 modelo original da revista (ignorado pelo Git)
  artigo_rbca.pdf                 PDF final (12 páginas)
  artigo_rbca_overleaf.zip        ZIP para importar no Overleaf
artigo_rita/                      terceira versão, adaptada à RITA
  artigo_rita.tex                 artigo adaptado ao modelo da RITA
  RITA.cls, abntex2*              classe oficial e citações ABNT numéricas
  figuras/                        10 figuras usadas na versão RITA
  modelo_oficial/                 ZIP do modelo oficial da RITA (ignorado pelo Git)
  artigo_rita.pdf                 PDF final (13 páginas)
  artigo_rita_overleaf.zip        ZIP para importar no Overleaf
context.md                       este arquivo (versionado como nota interna para IAs)
entendendo_o_trabalho.md         guia detalhado em linguagem simples (ignorado pelo Git)
.gitignore                       exclui guia simples, PDFs/ZIPs, data/raw e pycache (context.md é versionado)
```

`data/processed/` também contém `clima_uf_ano.csv` e `painel_uf_ano.csv` (294 linhas cada = 27 UFs × 11 anos), resquícios de análise exploratória estadual anterior ao recorte em Varginha. Não são usados pelo código atual nem pelos artigos.

## 4. Como executar

```bash
cd "C:\Users\User\Downloads\dados com pandas"
python src/main.py            # usa cache, termina em segundos
python src/main.py --force    # refaz tudo do zero (relê os ZIPs)
python src/download.py        # só se faltar algum ZIP em data/raw
```

Ambiente: Python 3.11.9, Windows. Dependências já instaladas: pandas 2.3.0, numpy 2.4.6, matplotlib, seaborn, scipy, statsmodels, requests, geopandas 1.2.0. **Não há `pdflatex` instalado nesta máquina**, então o `.tex` foi validado apenas estaticamente.

### Apresentação final (nota interna — não vai no README nem no artigo)

O código é um pipeline de linha de comando, não um bot/aplicativo. Não executar tudo ao vivo na apresentação: mostrar figuras/tabelas já geradas e um slide com `python src/main.py` + estrutura do repo. Opcional: demo curta com cache (segundos) ou abrir `painel_varginha.csv`; `--force` demora minutos e não vale estar ao vivo. Foco: pergunta → método → resultados → limitações. Código é avaliado pelo repositório/README (2 pt), não por execução ao vivo.

## 5. Pipeline ETL — decisões importantes

1. Os CSVs do INMET têm **dois layouts**: até 2018 (`AAAA-MM-DD`, `HH:MM`, `-9999`); desde 2019 (`AAAA/MM/DD`, `HHMM UTC`, vazio). Ambos são normalizados. Há 9 linhas de metadados antes do cabeçalho.
2. Descartam-se dias com < 6 horas válidas e meses com < 15 dias válidos.
3. Agregação: horário → diário → mensal → anual. Anomalias z por variável (baseline 2015–2025).
4. **Problema crítico já corrigido:** a estação A515 registrou `0 mm` em sequências longas — mai–jul/2019, mai–jul/2022, mai–dez/2023 e jan–mar/2024 — incompatível com a climatologia (medianas mensais de 24,6 mm em maio, 27,1 mm em junho e 219,2 mm em dezembro). Isso era **falha de sensor**, não dado real. Esses meses e os meses ausentes (ago/2016, dez/2025) foram **imputados pela mediana mensal** e sinalizados em `precip_imputada` / `meses_imputados` (`data/processed/clima_varginha_mensal.csv`). Total: **19 meses imputados** (8 deles em 2023).
5. Winsorização dos rendimentos e do rebanho nos percentis 1%/99% **após** o cálculo das anomalias.
6. Saída: `data/processed/painel_varginha.csv` — **11 linhas × 26 colunas**.

**Nunca remova a imputação**: sem ela aparece uma correlação falsa entre chuva do ano anterior e rebanho bovino (R²=0,54, p=0,015), que foi identificada como artefato e já descartada.

## 6. Resultados corretos (após a imputação)

Fonte: `output/tables/resultados_estatisticos.txt`.

- Precipitação anual média: **1047,6 mm** (727,8–1476,2 mm); temperatura média: **20,47 °C**; rendimento médio do café: **1567,24 kg/ha** (1038–2121,6 kg/ha).
- Spearman chuva anual × café: **ρ = 0,273 (p = 0,4160)** — não significativo.
- Chuva na frutificação: ρ = 0,406 (p = 0,2443); chuva na floração: ρ = 0,224 (p = 0,5334); chuva na colheita: ρ = 0,187 (p = 0,5824).
- Temperatura na floração: **ρ = −0,418 (p = 0,2291)**; temperatura média: ρ ≈ −0,005; dias quentes: ρ = −0,048.
- Janelas mensais (exploratório): janeiro ρ = 0,446 (p = 0,169); dezembro ρ = −0,405 (p = 0,217).
- OLS: M1 (chuva anual) R²=0,043, p=0,5425; M2 (frutificação + calor floração) R²=0,205, p=0,4472; M3 (quadrático) R²=0,093, p=0,6778; M4 (chuva de janeiro) R²=0,078, p=0,4050.
- Mann–Whitney anos secos × chuvosos: **U = 5,5; p = 1,0000**.
- Rebanho bovino × chuva do ano anterior: **β = 0,029; R² = 0,001; p = 0,9395** — sem associação.
- Sensibilidade (excluindo anos com falha longa, n=7): chuva anual ρ=0,234 (p=0,6132); temperatura na floração ρ=−0,886 (p=0,0188, n=6) — resultado exploratório, não confirmatório.

**Conclusão científica:** com 11 anos de dados municipais, **não há evidência estatística significativa** de que o clima explique o rendimento anual do café ou o rebanho bovino em Varginha. Não transformar isso em "relação significativa".

## 7. Figuras (10)

`01_mapa_varginha.png`, `02_climograma.png`, `03_serie_rendimento_clima.png`, `04_dispersao_chuva_cafe.png`, `05_dispersao_calor_cafe.png`, `06_boxplot_anos_secos.png`, `07_indice_culturas.png`, `08_heatmap_correlacoes.png`, `09_rebanho_chuva_atrasada.png`, `10_janelas_mensais.png`.

As 4 referenciadas no artigo SBC (01, 02, 04 e 09) foram copiadas para `artigo_sbc/figuras/`. A figura 03, que não é usada no SBC, foi removida dessa pasta em 25/11/2026. Se `src/plots.py` for rerodado, recopiar apenas as 4 figuras para lá.

## 8. Estado do artigo

- `artigo_sbc/artigo.tex` usa o **template oficial da SBC** (`sbc-template.sty`, `sbc.bst`), com resumo + abstract, seções Introdução, Trabalhos Relacionados, Metodologia, Resultados, Discussão, Conclusão e referências.
- Autores e e-mails já preenchidos nos dois artigos: Luigi `luigimiranda2003@gmail.com`, Rafael `rafaelperim6@gmail.com`, Eduardo `eduardogomes@cefetmg.br`, Marcelo `marcelo.mussel@gmail.com` (professores por último). Os ZIPs na raiz já contêm essa atualização.
- Números do artigo já conferidos com `output/tables/resultados_estatisticos.txt`.
- **Compilado no Overleaf** (7 páginas); PDF final em `artigo_sbc/artigo_sbc.pdf`, com os e-mails reais e a afiliação UFCIMG. Para compilar localmente: dentro de `artigo_sbc/`, `pdflatex artigo.tex` (duas vezes) + `bibtex artigo` + mais duas vezes.
- Referências incluem INMET, IBGE PAM/PPM, Victorino (2015), Aparecido et al. (2016), Meireles & Japiassú (2009), Gomes et al. (2026), IPCC (2021) e pacotes Python.
- `artigo_rbca/artigo_rbca.tex` é a **segunda versão**, já adaptada às normas da RBCA: resumo em português com cerca de 150 palavras (≤200), abstract em inglês com cerca de 150, três palavras-chave em cada idioma, página 19×29 cm com área de impressão 16×23 cm, citações ABNT numéricas com `abntex2cite`, 4 tabelas e 10 figuras, seção de Agradecimentos e rodapé com revista/volume/número. Os números são os mesmos da versão SBC.
- A classe **oficial** `RBCA.cls` (v0.5, 13/08/2013, de Carlos Amaral Hölbig) foi obtida do ZIP `Revista_RBCA__instruções_para_preparação_de_artigos.zip`, guardado em `artigo_rbca/modelo_oficial/`, e já substituiu a reconstrução anterior em `artigo_rbca/RBCA.cls`. O modelo original completo (`.cls`, `.tex` de exemplo, `.bib`, `.eps` e PDF) está guardado em `artigo_rbca/modelo_oficial/` para consulta. O PDF `xggxhscsnvby.pdf` na raiz é apenas o guia compilado (4 páginas), sem a classe. Os arquivos `abntex2cite.sty`, `abntex2abrev.sty` e `abntex2-num.bst` são oficiais (baixados do repositório abnTeX2).
- **Compilação no Overleaf (24/11/2026):** o SBC compilou com **6 páginas** e a RBCA com **11 páginas** (ambas dentro dos limites). Em 25/11/2026 o discente recompilou os três artigos e enviou os PDFs finais, guardados como `artigo_sbc/artigo_sbc.pdf` (**7 páginas**), `artigo_rbca/artigo_rbca.pdf` (**12 páginas**) e `artigo_rita/artigo_rita.pdf` (**13 páginas**). Os nomes antigos (`Ana__9_.pdf`, `Analise_da_relac__4_.pdf`, `Analise_da_relac__6_.pdf`) foram renomeados. Após revisão linha a linha, corrigiram-se erros de acentuação nos três `.tex`: no SBC, 14× `{\c{c}}es` → `{\c{c}}{\~o}es` (ex.: "observaçes"→"observações") e 4× "estaço"→"estação"; na RBCA e na RITA, `trê`, `més` ×2, `confianção`, `questaõ`, `variaçções` **e 8× `\c{c}es`** → `\c{c}\~oes` ("correlaçes", "limitaçes", etc.). Os ZIPs já estão sincronizados e os três PDFs foram recompilados em 25/11/2026 e conferidos (nenhum erro de acentuação restante) — o que parecia artefato de extração de texto era erro real no LaTeX. A paginação mudou em relação aos testes iniciais por causa das correções de autores/afiliação e da atualização do template SBC. Correções aplicadas após os testes: no SBC, `\providecommand{\palavraschave}` (o `.sty` do repositório não define o comando; a definição usa `\par\noindent` para evitar "There's no line here to end"), `babel` com `brazilian`, título em três linhas, autores e e-mails em uma linha (o `\\` dentro do argumento de `\email` quebra o `tabular` e gera "Missing } inserted"); os placeholders originais dos e-mails usavam chaves literais `\{...\}` porque `\\` seguido de `[` gera "Missing number, treated as zero" (hoje os e-mails são reais). Após nova compilação em 25/11/2026, a linha dos e-mails estava longa e desalinhava o bloco de autores/instituição; corrigido chamando `\email{}` duas vezes (dois e-mails por linha), sem `\\` dentro do argumento. Avisos de `Overfull \hbox` no preâmbulo são cosméticos; na RBCA, `\headheight=13pt` e `-1pt` no `\topmargin` para eliminar o aviso do `fancyhdr`. Os ZIPs na raiz já estão atualizados. Avisos de `Underfull \hbox` na bibliografia são cosméticos. Em 25/11/2026, o `sbc-template.sty` local foi substituído pela versão vigente do ZIP oficial da SBC (`https://www.sbc.org.br/wp-content/uploads/2024/07/modelosparapublicaodeartigos.zip`, atualização de 12/2017: pacote `caption` no lugar de `caption2` e compatibilidade com `hyperref`); o `sbc.bst` já era idêntico ao oficial. O `\providecommand{\palavraschave}` continua necessário porque o `.sty` oficial também não define esse comando. A paginação pode mudar na recompilação.
- Validação estática final: chaves balanceadas, ambientes OK, citações/rótulos/figuras OK nos dois `.tex`.
- **Lembrete RITA:** se submeter à RITA, é obrigatório declarar uso de IA em seção específica antes das referências (“Declaration of AI-Assisted Use in Writing”). RBCA não mostrou exigência equivalente nas normas consultadas.

## 9. Periódicos — o que foi pesquisado

- **RBCA (UPF):** escopo declara explicitamente "computação aplicada à **agricultura**, saúde, engenharias". Ideal para este trabalho. Porém exige **template próprio** (não o da SBC), ABNT numérico com `abntex2cite`, página 19×29 cm, margens laterais 1,5 cm, resumo em português ≤200 palavras, 3 palavras-chave, rodapé com revista/volume/número, submissão inicial apenas em PDF via OJS (`https://ojs.upf.br/index.php/rbca`). O guia mais antigo pedia 10–15 páginas; a página atual do OJS informa **8–15 páginas** — conferir na submissão. **Atenção:** em 25/11/2026 a página do OJS informava "This journal is not accepting submissions at this time". O portal de periódicos da UPF esclarece que as submissões estão **suspensas desde 29/08/2026** para atualização do template e das diretrizes de uso de IA; as próximas edições são v.18 n.3 (nov/2026) e v.19 n.1 (abr/2027), sem data anunciada de reabertura. Conferir periodicamente ou escrever para `rbca@upf.br`. Se não reabrir a tempo, a alternativa prevista na tarefa é a **RITA**, que estava aceitando submissões via SEER (artigos de pesquisa de 12–25 páginas — a versão RBCA tem 12), embora exija template próprio e tenha escopo menos afim. Observação da Diadorim: a revista não aceita submissão de preprint já depositado em outra plataforma.
- **RITA (UFRGS):** escopo lista bioinformática, alto desempenho, gráfica, engenharia de software, métodos formais, medicina, IA, microeletrônica, nanotecnologia, otimização, redes, robótica, sistemas de informação, embarcados. **Agricultura/análise de dados não aparece explicitamente** — menor afinidade. Artigos de pesquisa sugeridos com 12–25 páginas, template LaTeX próprio, revisão duplo-cega, submissão via SEER. Estava aceitando submissões em 25/11/2026. **Exige** seção "Declaration of AI-Assisted Use in Writing" imediatamente antes das referências quando há uso de IA na redação. A versão adaptada está em `artigo_rita/artigo_rita.tex` (RBCA mantida intacta). O link oficial do modelo (`http://www.inf.ufrgs.br/revista/RITA2018.zip`) retorna 404; as normas dizem para usar o template, mas que na submissão inicial basta o PDF, sem exigência rigorosa de paginação — por segurança o `.tex` já usa `\documentclass{RITA}`. O `RITA.cls` oficial foi obtido do ZIP do modelo baixado do Overleaf (`Revista_de_Informática_Teórica_e_Aplicada___RITA.zip`, guardado em `artigo_rita/modelo_oficial/`) e está em `artigo_rita/` e no `artigo_rita/artigo_rita_overleaf.zip`, junto com `abntex2cite.sty`, `abntex2abrev.sty` e `abntex2-num.bst`. O preâmbulo e a ordem dos ambientes foram conferidos contra o `RITAexemplo.tex` oficial (classe v0.3, 19/05/2016): `\documentclass{RITA}`, `\englishtitle`, `\RITAvolume`/`\RITAnumber`/`\RITAyear`/`\RITApagerange`, `\usepackage[num]{abntex2cite}` e resumo → abstract → keywords → keywordsenglish.
- **Recomendação:** RBCA, pela afinidade temática direta com agricultura e computação aplicada. "Mais fácil" em termos de aceite temático; **não** em termos de formatação, porque exige adaptar o artigo para o modelo da revista e expandir para 10–15 páginas.

### O que significa "normas de formatação do periódico" (item 3 da lista do discente)

Significa que, além do template da SBC (exigido pela disciplina), o artigo enviado à revista precisa seguir o **guia de autores dela**: modelo próprio (Word/LaTeX), número de páginas, margens, fonte, estrutura do resumo/abstract, palavras-chave, estilo de citações e referências, sistema de submissão e eventuais declarações. A tarefa diz que descumprir **qualquer um dos dois** zera a nota de formatação. Na prática: manter `artigo_sbc/artigo.tex` (SBC) para a disciplina e produzir uma **segunda versão adaptada à RBCA** para a submissão real.

## 10. Status dos 18 pontos

| Item | Pontos | Situação |
|---|---|---|
| Proposta (18/09) | 1,5 | **Feita** pelo discente |
| ETL e junção das bases | 3,0 | **Feita e validada** |
| Análise exploratória e estatística | 4,0 | **Feita** (10 figuras, 4 técnicas) |
| Artigo científico (formato SBC) | 5,0 | **Pronto** (7 páginas); PDF final salvo |
| Versão RBCA (submissão) | — | **Pronta** em `artigo_rbca/`; conferir com o template oficial antes de enviar |
| Código e reprodutibilidade | 2,0 | **Feito**: código/README no GitHub, com commit/push e link no README |
| Apresentação final | 2,5 | **Feita**: 10 slides, PDF salvo na raiz como `apresentacao.pdf` |

## 11. Pendências exatas (e decisões do discente em 24/11/2026)

1. ~~Preencher os e-mails dos 4 autores~~ — **feito** nos dois artigos, com os e-mails reais informados pelo discente.
2. ~~Compilar os artigos no Overleaf~~ — **feito**: SBC, RBCA e RITA compilados e recompilados em 25/11/2026, com os e-mails reais, a afiliação UFCIMG e a correção da acentuação. PDFs finais salvos em `artigo_sbc/artigo_sbc.pdf` (7 p.), `artigo_rbca/artigo_rbca.pdf` (12 p.) e `artigo_rita/artigo_rita.pdf` (13 p.). Os nomes antigos foram renomeados.
3. ~~Produzir versão RBCA do artigo~~ — **feita** em `artigo_rbca/`, já com a `RBCA.cls` oficial. O discente vai **conferir no OJS** se a revista reabriu submissões e se existe template mais novo que o v0.5/2013; registrado como pendente dele.
4. **Enviar para RBCA (recomendado) e guardar o comprovante; enviar também ao CSBC 2027 e guardar o comprovante.** A tarefa exige os dois comprovantes. CSBC é congresso da SBC (usa o formato SBC); RBCA é periódico (usa o formato próprio da revista). São duas submissões distintas, com os respectivos artigos adaptados. Antes de enviar, conferir a política da RBCA sobre publicação prévia em anais de evento (escrever para `rbca@upf.br` se necessário). **Atualização 25/11/2026:** o prazo de entrega da disciplina é 04/12 e a RBCA continua fechada — o discente decidiu submeter à **RITA**, usando `artigo_rita/`. Quanto ao CSBC 2027, a chamada de artigos ainda não abriu; ele deve perguntar ao professor como proceder com o comprovante e se cadastrar no alerta "Fique por dentro" do site do congresso.
5. ~~Criar repositório GitHub, dar commit/push e colar o link no README~~ — **feito em 25/11/2026**: `https://github.com/LuigiPenachio/clima-cafe-varginha-pandas`, branch `main`, commit inicial `4988ae0`, link no README.
6. ~~Preparar e fazer a apresentação final~~ — **feita**: 10 slides gerados no Gamma, PDF salvo na raiz como `apresentacao.pdf`.

## 12. Armadilhas para a próxima IA

- Não reintroduzir o resultado antigo do rebanho (R²=0,54) — ele era artefato dos zeros espúrios.
- Não usar o código de município 3171204 (é Vespasiano); o correto é **3170701**.
- O ano da PAM vem em `D4N`; o da PPM também. O cabeçalho da API muda entre nomes legíveis e códigos.
- O template SBC tem um typo em `\palavraschave` ("Plavras-Chave") — isso vem do `.sty` oficial; não "corrigir" mexendo no template.
- Se alterar números em `src/`, rodar `python src/main.py --force`, recopiar as figuras para `artigo_sbc/figuras/` e `artigo_rbca/figuras/` e atualizar **README, ambos os artigos e este context.md** juntos.
- A `RBCA.cls` local é a oficial v0.5 (13/08/2013). Se o OJS da UPF disponibilizar uma versão mais recente (o link antigo cita `RBCATex_new.zip`, atualizado em 15/08/2017), confira a data antes de submeter.
- Os dados brutos não precisam ser baixados de novo; `data/raw/` já está completo.
- Limpeza feita em 24/11/2026: PDFs antigos (`Ana__5_.pdf`, `Analise_da_relac__1_.pdf`, `xggxhscsnvby.pdf`, `artigo_sbc/artigo.pdf`, `artigo_rbca/artigo_rbca.pdf`), arquivos de exemplo `artigo_sbc/sbc-template.tex`/`.bib` e `src/__pycache__` foram removidos. O ZIP oficial da RBCA e `artigo_rbca/modelo_oficial/` foram mantidos.
