---
type: project
id: feira-livre
name: Feira Livre
tagline:
  pt: API de pedidos para uma cooperativa de feirantes
  en: Ordering API for a farmers' market cooperative
context:
  pt: Projeto pessoal com usuários reais
  en: Personal project with real users
role:
  pt: Desenvolvedora (projeto individual)
  en: Developer (solo project)
start: 2025-09
end: null
links:
  repo: github.com/beatriz-lima-example/feira-livre
  demo: feira.example.com
demo_online: true
hands_on: true
sole_contributor: true
tags: [backend, python, fastapi, postgresql, docker, rest-api]
status: reviewed
bullets:
  - id: feira-api
    text:
      pt: "Desenvolvi uma API REST em FastAPI e PostgreSQL que recebe os pedidos semanais de 12 feirantes de uma cooperativa."
      en: "Built a FastAPI and PostgreSQL REST API that takes weekly orders for a cooperative of 12 market vendors."
    tags: [backend, python, fastapi, postgresql, rest-api]
    metric: "12 feirantes"
    evidence: [repo]
    status: reviewed
  - id: feira-deploy
    text:
      pt: "Publiquei a API com Docker Compose numa VPS, com backup diário do banco e restauração testada."
      en: "Deployed the API with Docker Compose on a VPS, with daily database backups and a tested restore."
    tags: [docker, devops, backup]
    metric: null
    evidence: [repo]
    status: reviewed
---
