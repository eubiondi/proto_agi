import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

OBSIDIAN_VAULT_ROOT = Path(os.environ["OBSIDIAN_VAULT_ROOT"])
REPORTS_ROOT        = Path(os.getenv("REPORTS_ROOT", "reports"))

# Atalhos para as seções do vault usadas pelo proto_agi
OBSIDIAN_4FRACTAL  = OBSIDIAN_VAULT_ROOT / "07_Projeto_4Fractal"
OBSIDIAN_PROTO_AGI = OBSIDIAN_VAULT_ROOT / "08_Proto_AGI"
