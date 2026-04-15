"""
engineering_worker.py — Nó de análise técnica do proto_agi.

Fases explícitas
----------------
  1. Preparação do contexto  — extrai métricas e valida o state
  2. Construção do prompt    — monta system + user com os 8 campos do diagnóstico
  3. Chamada ao modelo       — delega para llm.call_llm (OpenRouter)
  4. Pós-processamento       — envolve a resposta num header com metadados

Sprint 002: análise real via LLM (OpenRouter → anthropic/claude-opus-4-6).
"""

from __future__ import annotations

import datetime

from ..state import AgentState
from ..llm import call_llm


# ===========================================================================
# 1. Preparação do contexto
# ===========================================================================

def _prepare_context(state: AgentState) -> dict:
    """
    Valida e extrai metadados do state para uso nas fases seguintes.
    Retorna um dict com os campos necessários para a construção do prompt.
    """
    ctx = state.context
    if not ctx:
        raise ValueError("engineering_worker: state.context está vazio — rode context_loader primeiro.")

    return {
        "request":       state.request or "Análise técnica geral do projeto.",
        "context":       ctx,
        "context_chars": len(ctx),
        "timestamp":     datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


# ===========================================================================
# 2. Construção do prompt
# ===========================================================================

SYSTEM_PROMPT = """\
Você é um engenheiro de software sênior e analista de sistemas quantitativos.
Sua tarefa é analisar o contexto completo de um projeto técnico e produzir um \
diagnóstico técnico estruturado em português brasileiro.

O diagnóstico deve conter exatamente estas 8 seções em Markdown:

## 1. Resumo Executivo
Síntese de 3 a 5 frases sobre o projeto e seu estado atual.

## 2. O que o Projeto Parece Ser
Propósito, domínio, usuário-alvo e natureza do sistema \
(ex: robô de trading, biblioteca, ferramenta de análise, etc.).

## 3. Arquitetura Observada
Linguagens utilizadas, componentes principais, padrões de design \
identificáveis, pontos de integração e dependências externas visíveis.

## 4. Papel dos Arquivos Principais
Para cada arquivo presente no contexto, uma linha descrevendo sua \
responsabilidade dentro do sistema.

## 5. Parâmetros Críticos
Variáveis, constantes, configurações ou valores que governam o comportamento \
do sistema. Liste com: nome, valor observado (se visível) e impacto.

## 6. Riscos Técnicos e Operacionais
Vulnerabilidades, pontos de falha únicos, dependências frágeis, \
debt técnico observável, problemas de manutenibilidade ou robustez.

## 7. Dúvidas em Aberto
Perguntas que surgem da leitura do código e das notas, e que não podem \
ser respondidas sem informação adicional.

## 8. Próximos Passos
De 3 a 5 ações concretas, priorizadas, para avançar o projeto na \
direção do pedido original.

Regras de qualidade:
- Escreva em português brasileiro.
- Seja direto e técnico. Evite frases genéricas de preenchimento.
- Se um arquivo estiver truncado no contexto, indique isso na análise.
- Se uma seção não se aplicar, escreva: "_Não aplicável neste contexto._"
"""


def _build_user_prompt(prep: dict) -> str:
    """
    Monta a mensagem do usuário como string única.

    Estrutura:
      - Cabeçalho com o pedido original
      - Contexto completo do projeto (vault + código)
      - Instrução final de análise
    """
    return (
        f"**Pedido de análise:** {prep['request']}\n\n"
        f"**Contexto carregado:** {prep['context_chars']:,} chars\n\n"
        "---\n\n"
        "# Contexto Completo do Projeto\n\n"
        f"{prep['context']}\n\n"
        "---\n\n"
        "Com base no contexto acima, produza o diagnóstico técnico estruturado "
        "seguindo exatamente as 8 seções definidas."
    )


# ===========================================================================
# 3. Chamada ao modelo  →  ver llm.py
# ===========================================================================

# (delegada para call_llm via OpenRouter)


# ===========================================================================
# 4. Pós-processamento
# ===========================================================================

def _format_result(raw: str, prep: dict) -> str:
    """
    Envolve a resposta bruta do LLM num header com metadados do run.
    """
    header = (
        f"# Diagnóstico Técnico 4Fractal — {prep['timestamp']}\n\n"
        f"**Pedido:** {prep['request']}  \n"
        f"**Contexto analisado:** {prep['context_chars']:,} chars\n\n"
        "---\n\n"
    )
    return header + raw.strip()


# ===========================================================================
# Nó LangGraph
# ===========================================================================

def engineering_worker(state: AgentState) -> dict:
    """
    Nó de análise técnica.

    Fases:
      1. Preparação do contexto
      2. Construção do prompt (system + user com 8 seções)
      3. Chamada ao modelo via OpenRouter (call_llm)
      4. Pós-processamento (header com metadados + resposta LLM)
    """
    # --- 1. Preparação ---
    prep = _prepare_context(state)
    print(f"[engineering_worker] contexto={prep['context_chars']:,} chars | pedido='{prep['request'][:60]}...'")

    # --- 2. Prompt ---
    user_prompt = _build_user_prompt(prep)

    # --- 3. Chamada LLM ---
    raw = call_llm(system=SYSTEM_PROMPT, user=user_prompt)

    # --- 4. Pós-processamento ---
    result = _format_result(raw, prep)

    print(f"[engineering_worker] diagnóstico gerado: {len(result):,} chars")

    return {
        "result": result,
        "logs":   [f"engineering_worker: diagnóstico gerado ({len(result)} chars)"],
    }
