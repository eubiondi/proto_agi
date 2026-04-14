import sys
from dotenv import load_dotenv

from .graph import build_graph
from .state import AgentState

load_dotenv()


def run(request: str) -> AgentState:
    graph = build_graph()
    initial_state = AgentState(request=request)
    final_state = graph.invoke(initial_state)
    return AgentState(**final_state)


def main():
    request = " ".join(sys.argv[1:]) or "Analisar status do projeto 4Fractal"

    print(f"\n>>> {request}\n")
    final = run(request)

    print("\n--- resultado ---")
    print(final.result)
    print(f"\nrelatório: {final.report_path}")
    print(f"auditoria: {final.audit_summary}")
    print(f"logs:      {final.logs}")


if __name__ == "__main__":
    main()
