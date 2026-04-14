from pathlib import Path

from ..config import OBSIDIAN_4FRACTAL
from ..state import AgentState

# Arquivos lidos em cada execução do Sprint 001
SOURCE_FILES: list[Path] = [
    OBSIDIAN_4FRACTAL / "00_Home" / "4Fractal.md",
    OBSIDIAN_4FRACTAL / "00_Home" / "INDEX_Operacional.md",
]


def context_loader(state: AgentState) -> dict:
    """Lê notas do vault Obsidian e monta o contexto do estado."""
    sections: list[str] = []

    for path in SOURCE_FILES:
        if path.exists():
            body = path.read_text(encoding="utf-8").strip()
            sections.append(f"### {path.name}\n\n{body}")
        else:
            sections.append(f"### {path.name}\n\n[arquivo não encontrado: {path}]")

    context = "\n\n---\n\n".join(sections)

    print(f"[context_loader] {len(sections)} arquivos lidos — {len(context)} chars")

    return {
        "context": context,
        "logs": [f"context_loader: {len(sections)} arquivos, {len(context)} chars"],
    }
