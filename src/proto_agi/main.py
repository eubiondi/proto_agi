import sys
from pathlib import Path
from dotenv import load_dotenv

from .graph import build_graph, build_focal_graph
from .state import AgentState

load_dotenv()


# ---------------------------------------------------------------------------
# API programática
# ---------------------------------------------------------------------------

def run(request: str) -> AgentState:
    """Modo geral: diagnóstico completo do projeto 4Fractal."""
    graph = build_graph()
    final_state = graph.invoke(AgentState(request=request))
    return AgentState(**final_state)


def run_focal(request: str, target_file: str) -> AgentState:
    """Modo focal: análise profunda de um arquivo específico."""
    graph = build_focal_graph()
    final_state = graph.invoke(AgentState(request=request, target_file=target_file))
    return AgentState(**final_state)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_FOCAL_FLAG = "--focal"

_USAGE = """\
Uso:
  python -m proto_agi                                      # diagnóstico geral
  python -m proto_agi "pedido"                             # diagnóstico geral com pedido
  python -m proto_agi --focal /caminho/arquivo.mq5         # análise focal (pedido padrão)
  python -m proto_agi --focal /caminho/arquivo.mq5 "pedido"  # análise focal com pedido
"""


def main():
    args = sys.argv[1:]

    # --- Modo focal ---
    if _FOCAL_FLAG in args:
        idx = args.index(_FOCAL_FLAG)
        if idx + 1 >= len(args):
            print(f"Erro: {_FOCAL_FLAG} requer o caminho do arquivo como próximo argumento.\n")
            print(_USAGE)
            sys.exit(1)

        target_file = args[idx + 1]
        remaining   = args[:idx] + args[idx + 2:]
        request     = " ".join(remaining) or f"Análise técnica focal de {Path(target_file).name}"

        print(f"\n>>> [focal] {target_file}")
        print(f">>> {request}\n")
        final = run_focal(request, target_file)

    # --- Modo geral ---
    else:
        request = " ".join(args) or "Analisar status do projeto 4Fractal"
        print(f"\n>>> {request}\n")
        final = run(request)

    # --- Saída ---
    print("\n--- resultado ---")
    print(final.result)
    print(f"\nrelatório : {final.report_path}")
    print(f"auditoria : {final.audit_summary}")
    print(f"logs      : {final.logs}")


if __name__ == "__main__":
    main()
