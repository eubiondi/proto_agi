import datetime

from ..state import AgentState


def engineering_worker(state: AgentState) -> dict:
    """
    Produz um diagnóstico estruturado com base no contexto carregado.

    Sprint 001: formata o contexto em relatório sem LLM.
    Sprint 002: substituir o corpo por chamada real ao Claude/Gemini.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Estatísticas básicas do contexto
    ctx = state.context
    vault_section   = ctx[ctx.find("## VAULT"):ctx.find("## ESTRUTURA")] if "## ESTRUTURA" in ctx else ""
    struct_section  = ctx[ctx.find("## ESTRUTURA"):ctx.find("## CÓDIGO")] if "## CÓDIGO" in ctx else ""
    code_section    = ctx[ctx.find("## CÓDIGO"):ctx.find("## ARQUIVOS DE REFERÊNCIA")] if "## ARQUIVOS DE REFERÊNCIA" in ctx else ctx[ctx.find("## CÓDIGO"):]
    binary_section  = ctx[ctx.find("## ARQUIVOS DE REFERÊNCIA"):] if "## ARQUIVOS DE REFERÊNCIA" in ctx else ""

    diagnosis = f"""# Diagnóstico 4Fractal — {timestamp}

**Pedido:** {state.request}

---

## 1. Status operacional (vault)

{vault_section.strip()}

---

## 2. Estrutura do projeto

{struct_section.strip()}

---

## 3. Código-fonte carregado

{code_section.strip()}

---

## 4. Arquivos de referência

{binary_section.strip() if binary_section else "_Nenhum arquivo binário encontrado._"}

---

## 5. Métricas do contexto

| Fonte | Chars |
|---|---|
| Vault Obsidian | {len(vault_section)} |
| Estrutura | {len(struct_section)} |
| Código-fonte | {len(code_section)} |
| Total | {len(ctx)} |

---

## 6. Próximo passo

> Integrar chamada LLM no `engineering_worker` para produzir análise real
> do código e das notas em vez de só reformatar o contexto.
"""

    print(f"[engineering_worker] diagnóstico: {len(diagnosis)} chars")

    return {
        "result": diagnosis,
        "logs": ["engineering_worker: ok"],
    }
