from typing import Annotated
from operator import add
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Estado compartilhado entre todos os nós do grafo."""

    # Entrada original do usuário
    request: str = ""

    # Modo "focal": caminho absoluto do arquivo a ser analisado em profundidade
    # Vazio no modo geral (context_loader + engineering_worker)
    target_file: str = ""

    # Contexto reunido pelo nó de contexto (Obsidian, arquivos, etc.)
    context: str = ""

    # Resultado produzido pelo nó de execução
    result: str = ""

    # Caminho do relatório gerado
    report_path: str = ""

    # Resumo registrado pelo auditor ao final do run
    audit_summary: str = ""

    # Indica se a memória foi gravada com sucesso
    memory_saved: bool = False

    # Logs acumulados ao longo do fluxo (cada nó anexa à lista)
    logs: Annotated[list[str], add] = Field(default_factory=list)
