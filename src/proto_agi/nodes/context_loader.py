from pathlib import Path

from ..config import OBSIDIAN_4FRACTAL, FOUR_FRACTAL_PROJECT_ROOT
from ..state import AgentState

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

# Notas do vault lidas em cada run
VAULT_FILES: list[Path] = [
    OBSIDIAN_4FRACTAL / "00_Home" / "4Fractal.md",
    OBSIDIAN_4FRACTAL / "00_Home" / "INDEX_Operacional.md",
]

# Arquivos de código lidos diretamente (conteúdo incluído no contexto)
CODE_FILES: list[Path] = [
    FOUR_FRACTAL_PROJECT_ROOT / "README.md",
    FOUR_FRACTAL_PROJECT_ROOT / "01_Source" / "ea" / "current" / "4FractalEA_v7.mq5",
    FOUR_FRACTAL_PROJECT_ROOT / "01_Source" / "include" / "Security.mqh",
    FOUR_FRACTAL_PROJECT_ROOT / "01_Source" / "indicator" / "4Fractal_v6.mq5",
    FOUR_FRACTAL_PROJECT_ROOT / "01_Source" / "tools" / "QuantAnalyzer.mq5",
]

# Arquivos que só aparecem como referência de existência (sem parse)
BINARY_EXTENSIONS = {".docx", ".xlsx", ".pdf"}

# Limite de linhas para arquivos de código longos (README lido completo)
CODE_PREVIEW_LINES = 120


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_read(path: Path, max_lines: int = 0) -> str:
    """Lê arquivo com fallback de encoding. Trunca em max_lines se necessário."""
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            text = path.read_text(encoding=enc)
            if max_lines > 0:
                lines = text.splitlines()
                if len(lines) > max_lines:
                    omitted = len(lines) - max_lines
                    text = "\n".join(lines[:max_lines]) + f"\n... [{omitted} linhas omitidas]"
            return text
        except (UnicodeDecodeError, UnicodeError):
            continue
    return "[erro: não foi possível ler o arquivo]"


def _dir_tree(root: Path, max_depth: int = 3) -> str:
    """Gera representação textual da estrutura de pastas."""
    lines: list[str] = []

    def _walk(path: Path, depth: int) -> None:
        if depth > max_depth:
            return
        for entry in sorted(path.iterdir()):
            if entry.name.startswith("."):
                continue
            indent = "  " * depth
            if entry.is_dir():
                lines.append(f"{indent}{entry.name}/")
                _walk(entry, depth + 1)
            else:
                size = entry.stat().st_size
                size_str = f"{size // 1024}KB" if size >= 1024 else f"{size}B"
                lines.append(f"{indent}{entry.name}  [{size_str}]")

    _walk(root, 0)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Nó
# ---------------------------------------------------------------------------

def context_loader(state: AgentState) -> dict:
    """
    Monta o contexto a partir de duas fontes:
    1. Notas do vault Obsidian (planejamento e status)
    2. Projeto real 4Fractal (código e estrutura)
    """
    sections: list[str] = []

    # --- 1. Vault Obsidian ---
    vault_parts: list[str] = []
    for path in VAULT_FILES:
        if path.exists():
            body = path.read_text(encoding="utf-8").strip()
        else:
            body = f"[não encontrado: {path}]"
        vault_parts.append(f"#### {path.name}\n\n{body}")

    sections.append("## VAULT OBSIDIAN\n\n" + "\n\n---\n\n".join(vault_parts))

    # --- 2. Estrutura de pastas do projeto real ---
    if FOUR_FRACTAL_PROJECT_ROOT.exists():
        tree = _dir_tree(FOUR_FRACTAL_PROJECT_ROOT)
        sections.append(f"## ESTRUTURA DO PROJETO\n\n```\n{tree}\n```")
    else:
        sections.append(
            f"## ESTRUTURA DO PROJETO\n\n[diretório não encontrado: {FOUR_FRACTAL_PROJECT_ROOT}]"
        )

    # --- 3. Arquivos de código/texto ---
    code_parts: list[str] = []
    for path in CODE_FILES:
        if not path.exists():
            code_parts.append(f"#### {path.name}\n\n[não encontrado]")
            continue

        ext = path.suffix.lower()
        if ext in BINARY_EXTENSIONS:
            size_kb = path.stat().st_size // 1024
            code_parts.append(f"#### {path.name}\n\n[arquivo binário — {size_kb}KB]")
        else:
            # README lido completo; código-fonte truncado
            max_lines = 0 if ext == ".md" else CODE_PREVIEW_LINES
            body = _safe_read(path, max_lines=max_lines)
            lang = ext.lstrip(".")
            code_parts.append(f"#### {path.name}\n\n```{lang}\n{body}\n```")

    sections.append("## CÓDIGO-FONTE\n\n" + "\n\n---\n\n".join(code_parts))

    # --- 4. Arquivos binários de referência ---
    binary_refs: list[str] = []
    for path in sorted(FOUR_FRACTAL_PROJECT_ROOT.rglob("*")):
        if path.suffix.lower() in BINARY_EXTENSIONS and path.is_file():
            size_kb = path.stat().st_size // 1024
            rel = path.relative_to(FOUR_FRACTAL_PROJECT_ROOT)
            binary_refs.append(f"- `{rel}`  [{size_kb}KB]")
    if binary_refs:
        sections.append("## ARQUIVOS DE REFERÊNCIA (binários)\n\n" + "\n".join(binary_refs))

    context = "\n\n---\n\n".join(sections)
    print(f"[context_loader] {len(sections)} seções — {len(context)} chars")

    return {
        "context": context,
        "logs": [f"context_loader: {len(sections)} seções, {len(context)} chars"],
    }
