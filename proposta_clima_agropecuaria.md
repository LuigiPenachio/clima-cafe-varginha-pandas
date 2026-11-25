# Proposta de pesquisa — Clima e cafeicultura em Varginha/MG (2015–2025)

**Tema:** Relação entre anomalias climáticas e o desempenho da agropecuária municipal de Varginha/MG, com ênfase na cafeicultura.

**Recorte espacial e temporal:** município de Varginha (código IBGE 3170701), Sul de Minas Gerais, anos de 2015 a 2025.

## 1. Bases de dados

| Base | Fonte | Variáveis de interesse | Recorte |
|---|---|---|---|
| **INMET — BDMEP** (base âncora), estação automática **A515 Varginha** | ZIPs anuais `portal.inmet.gov.br/uploads/dadoshistoricos/{ano}.zip` | Precipitação horária, temperatura do ar e máx./mín., umidade relativa | 2015–2025, agregada a dia, mês e ano |
| **IBGE — PAM** (Produção Agrícola Municipal), tabela SIDRA **5457**, classificação de produtos 782 | API SIDRA, nível municipal | **Rendimento médio do café em grão (kg/ha)** (cód. 40139); milho (40122) e soja (40124) como culturas de comparação | 2015–2025 |
| **IBGE — PPM** (Pesquisa da Pecuária Municipal), tabela SIDRA **3939** | API SIDRA, nível municipal | **Efetivo de bovinos** (cabeças em 31/12), categoria 2670 | 2015–2025 |

## 2. Chave de junção e justificativa

**Chave: `ano`**, com `estacao = A515` e `municipio = 3170701` como atributos fixos.

- A estação A515 pertence ao próprio município de Varginha (metadados do INMET: −21,5664°, −45,4042°), e o IBGE levanta PAM/PPM na unidade municipal. Não há, portanto, necessidade de junção espacial entre bases distintas.
- Usar `ano` garante que a safra de referência do IBGE (ano civil) seja pareada com o ano meteorológico completo da estação.
- Para variáveis fenológicas do café, a janela de floração (setembro–novembro) é calculada com o **ano anterior**, refletindo o ciclo da safra seguinte.
- Controles: verificação de anos completos (mínimo 10 meses válidos por ano), padronização dos dois layouts de CSV do INMET e conversão de `"-"`/`"..."` do SIDRA para valores faltantes.

## 3. Perguntas de pesquisa

- **P1:** Anomalias anuais de precipitação e temperatura explicam variações no rendimento do café em Varginha entre 2015 e 2025?
- **P2:** Janelas fenológicas específicas (floração, frutificação, colheita) apresentam associação mais forte que a média anual?
- **P3:** O rebanho bovino municipal responde com defasagem de um ano à precipitação?

## 4. Hipóteses iniciais

- **H1:** Anomalia positiva de precipitação correlaciona-se positivamente com o rendimento do café (ρ > 0).
- **H2:** Temperatura elevada na floração e maior frequência de dias com Tmáx > 35 °C correlacionam-se negativamente com o rendimento.
- **H3:** A relação com a precipitação é não linear (rendimento máximo em anomalia próxima de zero).
- **H4:** A chuva do ano anterior correlaciona-se positivamente com a variação do rebanho bovino no ano seguinte.

## 5. Pipeline ETL

1. Extrair 11 ZIPs do INMET e duas consultas SIDRA.
2. Limpar: layouts antigo (até 2018) e novo (desde 2019), `-9999`, valores vazios, dias com < 6 horas válidas e meses com < 15 dias válidos.
3. Agregar horário → diário → mensal → anual; calcular anomalias z (baseline 2015–2025) e janelas fenológicas.
4. Winsorizar variáveis de produção nos percentis 1%/99%.
5. Junta por `ano`, gerando `data/processed/painel_varginha.csv`.

## 6. Técnicas estatísticas

1. Correlação de Pearson e Spearman entre clima e rendimentos, com p-valores.
2. Regressão linear OLS (modelos com chuva anual, janelas fenológicas e termo quadrático), com R² ajustado e teste F.
3. Teste de Mann-Whitney comparando rendimento em anos secos, normais e chuvosos.
4. Regressão com defasagem de 1 ano para o rebanho bovino.

## 7. Visualizações (10)

Mapa de localização; climograma; série temporal clima × café; dispersão chuva × café; dispersão calor na floração × café; boxplot por classe de chuva; índice comparativo das culturas; heatmap de correlações; dispersão rebanho × chuva defasada; correlações mensais exploratórias.

## 8. Limitações esperadas

Amostra pequena (n = 11); uma única estação; descompasso entre ano civil e ciclo da safra; possíveis falhas de sensor com registros longos de chuva zero (detectadas e imputadas na etapa de limpeza); fatores de confusão (preços, área, tecnologia, pragas); último ano preliminar; multiplicidade de comparações nas janelas mensais; correlação não implica causalidade.

## 9. Fala para apresentação rápida (~40 s)

> Nosso tema é clima e agropecuária, mas focado em Varginha, no Sul de Minas, principal região cafeeira do país. Cruzamos os dados horários da estação A515 do INMET com o rendimento municipal do café, milho e soja da PAM e com o rebanho bovino da PPM do IBGE, de 2015 a 2025. Como a estação fica no próprio município, a chave de junção é o ano; para o café usamos também janelas fenológicas, como a floração no ano anterior. Vamos testar correlação, regressão e um teste de Mann-Whitney, com dez gráficos. O resultado vira artigo no formato SBC e código reproduzível no GitHub.
