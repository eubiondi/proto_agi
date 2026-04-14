import datetime

from ..state import AgentState


def auditor(state: AgentState) -> dict:
    """Registra um resumo imutável do run ao final do fluxo."""
    summary = (
        f"{datetime.datetime.now().isoformat(timespec='seconds')} | "
        f"pedido={state.request!r} | "
        f"contexto={len(state.context)}c | "
        f"diagnóstico={len(state.result)}c | "
        f"relatório={state.report_path}"
    )

    print(f"[auditor] {summary}")

    return {
        "audit_summary": summary,
        "logs": ["auditor: ok"],
    }
