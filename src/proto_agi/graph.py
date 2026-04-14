from langgraph.graph import StateGraph, END

from .state import AgentState


# ---------------------------------------------------------------------------
# Nós
# ---------------------------------------------------------------------------

def node_context(state: AgentState) -> dict:
    """Reúne contexto relevante para o pedido (Obsidian, arquivos, etc.)."""
    print(f"[context] pedido recebido: {state.request!r}")

    # TODO: ler vault do Obsidian, buscar no Neo4j, etc.
    context = f"Contexto simulado para: {state.request}"

    return {
        "context": context,
        "logs": [f"context: ok"],
    }


def node_execute(state: AgentState) -> dict:
    """Executa a tarefa principal com base no pedido e no contexto."""
    print(f"[execute] contexto disponível: {len(state.context)} chars")

    # TODO: chamar Claude / Gemini com o contexto reunido
    result = f"Resultado simulado para: {state.request}"

    return {
        "result": result,
        "logs": ["execute: ok"],
    }


def node_report(state: AgentState) -> dict:
    """Gera e salva o relatório da execução."""
    import datetime, pathlib

    reports_dir = pathlib.Path("reports")
    reports_dir.mkdir(exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = str(reports_dir / f"report_{timestamp}.md")

    content = f"# Relatório\n\n**Pedido:** {state.request}\n\n**Resultado:**\n{state.result}\n"
    pathlib.Path(report_path).write_text(content)

    print(f"[report] salvo em {report_path}")

    return {
        "report_path": report_path,
        "logs": [f"report: {report_path}"],
    }


def node_memory(state: AgentState) -> dict:
    """Persiste o registro da execução no Postgres e no Neo4j."""
    print(f"[memory] gravando execução...")

    # TODO: gravar no Postgres (tabela executions)
    # TODO: criar/atualizar nó no Neo4j

    return {
        "memory_saved": True,
        "logs": ["memory: ok"],
    }


# ---------------------------------------------------------------------------
# Grafo
# ---------------------------------------------------------------------------

def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("context", node_context)
    builder.add_node("execute", node_execute)
    builder.add_node("report", node_report)
    builder.add_node("memory", node_memory)

    builder.set_entry_point("context")
    builder.add_edge("context", "execute")
    builder.add_edge("execute", "report")
    builder.add_edge("report", "memory")
    builder.add_edge("memory", END)

    return builder.compile()
