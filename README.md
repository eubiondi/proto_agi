# proto_agi

Sistema pessoal de IA operacional, construído em ondas incrementais.
Fase atual: **Onda 1 — Base Operacional v0.1**

---

## Missão

Criar um agente capaz de receber pedidos, reunir contexto, executar tarefas, gerar relatórios e consolidar memória — acelerando principalmente o projeto **4Fractal**.

---

## Stack — Onda 1

| Camada | Tecnologia |
|---|---|
| Orquestração | LangGraph |
| Memória relacional | PostgreSQL 16 |
| Memória semântica/grafo | Neo4j 5 |
| Base de conhecimento | Obsidian |
| Execução / IDE | Claude Code |
| LLM auxiliar | Gemini |

---

## Objetivo da Semana 1

Completar o fluxo ponta a ponta:

```
pedido → contexto → execução → relatório → memória
```

Entrada: prompt de texto livre  
Saída: relatório salvo em `reports/` e registro persistido no Postgres e Neo4j

---

## Estrutura de Pastas

```
proto_agi/
├── apps/
│   ├── chat_gateway/     # entrada de pedidos
│   └── scheduler/        # agendamento de tarefas
├── data/
│   └── artifacts/        # arquivos gerados durante execução
├── reports/              # relatórios finais por execução
├── scripts/              # utilitários e automações avulsas
├── src/proto_agi/
│   ├── graph.py          # grafo LangGraph principal
│   ├── state.py          # estado compartilhado entre nós
│   ├── config.py         # carregamento de variáveis de ambiente
│   ├── nodes/            # nós do grafo (contexto, execução, memória…)
│   ├── memory/           # adaptadores Postgres e Neo4j
│   └── tools/            # ferramentas chamadas pelos nós
├── tests/
├── docker-compose.yml    # Postgres + Neo4j
├── .env                  # variáveis locais (não versionar)
└── requirements.txt
```

---

## Definition of Done — Semana 1

- [ ] Grafo LangGraph executa o fluxo completo sem erros
- [ ] Contexto do 4Fractal é lido do Obsidian e injetado no estado
- [ ] Execução produz ao menos um artefato em `data/artifacts/`
- [ ] Relatório é salvo em `reports/` com timestamp
- [ ] Registro da execução é gravado no Postgres
- [ ] Nó de memória cria ou atualiza entidade no Neo4j
- [ ] `.env` preenchido, containers sobem com `docker compose up -d`
- [ ] Fluxo completo roda com um único comando (`python -m proto_agi`)
