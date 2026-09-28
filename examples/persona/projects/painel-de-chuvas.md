---
type: project
id: painel-de-chuvas
name:
  pt: Painel de Chuvas
  en: Rainfall Dashboard
tagline:
  pt: Pipeline de dados públicos de chuva com relatório semanal
  en: Public rainfall data pipeline with a weekly report
start: 2025-03
end: 2025-06
links:
  repo: github.com/beatriz-lima-example/painel-de-chuvas
hands_on: true
tags: [data, python, duckdb, pandas, etl]
status: reviewed
bullets:
  - id: chuvas-pipeline
    text:
      pt: "Construí um pipeline em Python e DuckDB que baixa, limpa e consolida 10 anos de medições de 30 estações pluviométricas."
      en: "Built a Python and DuckDB pipeline that downloads, cleans and consolidates 10 years of readings from 30 rain gauges."
    tags: [data, python, duckdb, etl]
    metric: "30 estações, 10 anos"
    evidence: [repo]
    status: reviewed
  - id: chuvas-relatorio
    text:
      pt: "Gerei um relatório semanal com pandas que destaca os bairros com chuva acima da média histórica."
      en: "Produced a weekly pandas report highlighting neighborhoods with rainfall above the historical average."
    tags: [data, pandas, reporting]
    metric: null
    evidence: [repo]
    status: reviewed
---
