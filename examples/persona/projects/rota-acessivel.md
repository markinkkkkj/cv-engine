---
type: project
id: rota-acessivel
name: Rota Acessível
tagline:
  pt: App que sugere rotas de ônibus com veículos adaptados
  en: App that suggests bus routes served by accessible vehicles
context:
  pt: Trabalho de conclusão de curso, equipe de 3
  en: Capstone project, team of 3
role:
  pt: Responsável pelo backend e pela integração com dados de GTFS
  en: Owned the backend and the GTFS data integration
start: 2026-02
end: null
links:
  repo: github.com/beatriz-lima-example/rota-acessivel
hands_on: true
tags: [backend, python, fastapi, gtfs, data]
status: reviewed
bullets:
  - id: rota-gtfs
    text:
      pt: "Importei os dados GTFS do transporte público da cidade para PostgreSQL e expus a busca de rotas acessíveis numa API FastAPI."
      en: "Imported the city's public transit GTFS data into PostgreSQL and exposed accessible route search through a FastAPI API."
    tags: [backend, python, fastapi, postgresql, gtfs]
    metric: null
    evidence: [repo]
    status: reviewed
  - id: rota-usuarios
    text:
      pt: "Conduzi testes de usabilidade com 8 pessoas usuárias de cadeira de rodas."
      en: "Ran usability tests with 8 wheelchair users."
    tags: [ux, research]
    metric: "8 pessoas"
    evidence: []
    status: draft
    note: "aguarda o relatório final dos testes"
---
