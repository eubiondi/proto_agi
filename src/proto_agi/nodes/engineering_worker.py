import datetime

from ..state import AgentState


def engineering_worker(state: AgentState) -> dict:
    """
    Produz um diagnóstico textual com base no contexto carregado.

    Sprint 001: sem LLM — formata o contexto em um relatório estruturado.
    Sprint 002: substituir o corpo por uma chamada real ao Claude/Gemini.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    diagnosis = f"""# Diagnóstico — {state.request}

**Gerado em:** {timestamp}

---

## Contexto carregado do vault

{state.context}

---

## Situação atual (resumo automático)

- Contexto lido: **{len(state.context)} caracteres**
- Pedido recebido: `{state.request}`
- Arquivos de origem: `07_Projeto_4Fractal/00_Home/`

---

## Próximo passo sugerido

> Integrar chamada LLM no `engineering_worker` para análise real do contexto.
"""

    print(f"[engineering_worker] diagnóstico gerado — {len(diagnosis)} chars")

    return {
        "result": diagnosis,
        "logs": ["engineering_worker: diagnóstico gerado"],
    }
