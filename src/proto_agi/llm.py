"""
llm.py — Interface mínima para chamada ao LLM via OpenRouter.

OpenRouter expõe endpoint OpenAI-compatible; usamos o SDK openai apontando
para a base URL do OpenRouter.

Configuração (lida do .env)
---------------------------
    OPENROUTER_API_KEY   — obrigatória
    OPENROUTER_BASE_URL  — padrão: https://openrouter.ai/api/v1
    OPENROUTER_MODEL     — padrão: anthropic/claude-opus-4-6

Uso
---
    from .llm import call_llm
    resposta = call_llm(system="Você é...", user="Analise este código...")
"""

from __future__ import annotations

import os
from openai import OpenAI

# ---------------------------------------------------------------------------
# Configuração padrão
# ---------------------------------------------------------------------------

_DEFAULT_BASE_URL  = "https://openrouter.ai/api/v1"
_DEFAULT_MODEL     = "anthropic/claude-opus-4-6"
_DEFAULT_MAX_TOKENS = 8_000


# ---------------------------------------------------------------------------
# Interface pública
# ---------------------------------------------------------------------------

def call_llm(
    system: str,
    user: str,
    *,
    model: str | None = None,
    max_tokens: int = _DEFAULT_MAX_TOKENS,
) -> str:
    """
    Chama o LLM via OpenRouter e retorna o texto completo da resposta.

    Parâmetros
    ----------
    system     : prompt de sistema (instruções estáveis)
    user       : mensagem do usuário (contexto + pedido)
    model      : ID do modelo no OpenRouter — sobrescreve OPENROUTER_MODEL
    max_tokens : limite de tokens de saída

    Retorna
    -------
    str : texto da resposta do modelo

    Raises
    ------
    KeyError      : se OPENROUTER_API_KEY não estiver definida no ambiente
    openai.APIError : erros retornados pela API
    """
    api_key  = os.environ["OPENROUTER_API_KEY"]
    base_url = os.getenv("OPENROUTER_BASE_URL", _DEFAULT_BASE_URL)
    model    = model or os.getenv("OPENROUTER_MODEL", _DEFAULT_MODEL)

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
    )

    text = response.choices[0].message.content or ""

    usage = response.usage
    if usage:
        print(
            f"[llm] input={usage.prompt_tokens} output={usage.completion_tokens} "
            f"model={model}"
        )

    return text
