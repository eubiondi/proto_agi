import datetime
from pathlib import Path

from ..config import REPORTS_ROOT, OBSIDIAN_4FRACTAL
from ..state import AgentState

VAULT_EXPORT_DIR = OBSIDIAN_4FRACTAL / "08_Claude_Exports"


def report_writer(state: AgentState) -> dict:
    """Salva o relatório localmente em reports/ e no vault Obsidian."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.md"
    content = state.result

    # Salva em reports/ (local)
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    local_path = REPORTS_ROOT / filename
    local_path.write_text(content, encoding="utf-8")

    # Salva em 07_Projeto_4Fractal/08_Claude_Exports/ (vault)
    VAULT_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    vault_path = VAULT_EXPORT_DIR / filename
    vault_path.write_text(content, encoding="utf-8")

    print(f"[report_writer] local:  {local_path}")
    print(f"[report_writer] vault:  {vault_path}")

    return {
        "report_path": str(local_path),
        "logs": [
            f"report_writer: local={local_path}",
            f"report_writer: vault={vault_path}",
        ],
    }
