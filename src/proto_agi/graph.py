from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes.context_loader import context_loader
from .nodes.engineering_worker import engineering_worker
from .nodes.report_writer import report_writer
from .nodes.auditor import auditor


def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("context_loader",      context_loader)
    builder.add_node("engineering_worker",  engineering_worker)
    builder.add_node("report_writer",       report_writer)
    builder.add_node("auditor",             auditor)

    builder.set_entry_point("context_loader")
    builder.add_edge("context_loader",     "engineering_worker")
    builder.add_edge("engineering_worker", "report_writer")
    builder.add_edge("report_writer",      "auditor")
    builder.add_edge("auditor",            END)

    return builder.compile()
