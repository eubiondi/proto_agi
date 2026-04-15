"""
file_analyst.py — Análise focal de um arquivo específico via chunk-and-consolidate.

Estratégia
----------
  1. Lê o arquivo inteiro (com fallback de encoding para UTF-16/latin-1)
  2. Divide em blocos de CHUNK_SIZE linhas com OVERLAP de sobreposição
  3. Analisa cada bloco individualmente com o LLM (chamadas leves, max 1 000 tokens)
  4. Consolida todos os resumos em uma análise final de 7 seções (max 6 000 tokens)
  5. Formata resultado com header de metadados do run

Arquivos-alvo típicos: .mq5, .mqh (MQL5)
Chunk: 150 linhas | Overlap: 20 linhas | Step: 130 linhas
"""

from __future__ import annotations

import datetime
from pathlib import Path

from ..state import AgentState
from ..llm import call_llm

# ---------------------------------------------------------------------------
# Configuração de chunking
# ---------------------------------------------------------------------------

CHUNK_SIZE = 150    # linhas por bloco
OVERLAP    = 20     # sobreposição entre blocos consecutivos
STEP       = CHUNK_SIZE - OVERLAP   # = 130


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

_CHUNK_SYSTEM = """\
Você é um engenheiro de sistemas quantitativos analisando código MQL5.
Leia o bloco de código a seguir e extraia de forma concisa:

1. **O que este bloco faz** — propósito e responsabilidade
2. **Elementos importantes** — variáveis, funções, parâmetros definidos ou usados
3. **Observações** — anomalias, riscos, padrões notáveis (ou "Nenhuma" se vazio)

Seja breve e técnico. Responda em português brasileiro. Máximo 300 palavras.
"""

_CONSOLIDATION_SYSTEM = """\
Você é um engenheiro de software sênior e analista de sistemas quantitativos.
Você recebeu resumos de todos os blocos de código de um único arquivo MQL5.
Consolide esses resumos em um diagnóstico técnico estruturado em português brasileiro
com exatamente estas 7 seções:

## 1. Função do Arquivo
Propósito e responsabilidade do arquivo dentro do sistema.

## 2. Arquitetura Observada
Estrutura geral, componentes principais, padrões de design, dependências visíveis.

## 3. Lógica Principal Identificada
Fluxo de execução principal, algoritmos centrais, mecanismo de tomada de decisão.

## 4. Parâmetros Críticos
Parâmetros de entrada, constantes e configurações que governam o comportamento.
Formato: nome — valor observado (se visível) — impacto.

## 5. Riscos
Vulnerabilidades, pontos de falha únicos, debt técnico, fragilidades operacionais.

## 6. Dúvidas em Aberto
Perguntas que não podem ser respondidas sem mais contexto, dados ou testes.

## 7. Próximos Passos
De 3 a 5 ações concretas, priorizadas, para avançar o projeto na direção do pedido.

Regras: direto, técnico, sem frases genéricas de preenchimento.
Se uma seção não se aplicar, escreva: "_Não aplicável neste contexto._"
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_file(path: Path) -> list[str]:
    """Lê o arquivo com fallback de encoding. Retorna lista de linhas."""
    for enc in ("utf-8", "utf-16", "latin-1"):
        try:
            return path.read_text(encoding=enc).splitlines()
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"file_analyst: não foi possível ler {path}")


def _split_chunks(lines: list[str]) -> list[tuple[int, int, list[str]]]:
    """
    Divide linhas em blocos com sobreposição.

    Retorna lista de (start_line_1indexed, end_line_1indexed, linhas).
    """
    chunks: list[tuple[int, int, list[str]]] = []
    total = len(lines)
    start = 0
    while start < total:
        end = min(start + CHUNK_SIZE, total)
        chunks.append((start + 1, end, lines[start:end]))
        if end >= total:
            break
        start += STEP
    return chunks


def _analyze_chunk(
    chunk_lines: list[str],
    chunk_idx: int,
    total_chunks: int,
    filename: str,
    start_line: int,
    end_line: int,
) -> str:
    """Chama LLM para analisar um bloco de código. Retorna resumo conciso."""
    code = "\n".join(chunk_lines)
    user = (
        f"**Arquivo:** `{filename}`  \n"
        f"**Bloco {chunk_idx}/{total_chunks}** (linhas {start_line}–{end_line})\n\n"
        f"```mql5\n{code}\n```"
    )
    print(
        f"[file_analyst] bloco {chunk_idx}/{total_chunks} "
        f"(L{start_line}–L{end_line}, {len(chunk_lines)} linhas)..."
    )
    return call_llm(system=_CHUNK_SYSTEM, user=user, max_tokens=1_000)


def _consolidate(
    chunk_analyses: list[str],
    filename: str,
    request: str,
) -> str:
    """Consolida os resumos de todos os blocos em diagnóstico final de 7 seções."""
    summaries = "\n\n---\n\n".join(
        f"### Bloco {i + 1}\n\n{text}"
        for i, text in enumerate(chunk_analyses)
    )
    user = (
        f"**Arquivo analisado:** `{filename}`  \n"
        f"**Pedido original:** {request}\n\n"
        "---\n\n"
        "# Resumos por Bloco\n\n"
        f"{summaries}\n\n"
        "---\n\n"
        "Com base nos resumos acima, produza o diagnóstico técnico consolidado "
        "com as 7 seções definidas."
    )
    print(f"[file_analyst] consolidando {len(chunk_analyses)} blocos em análise final...")
    return call_llm(system=_CONSOLIDATION_SYSTEM, user=user, max_tokens=6_000)


# ---------------------------------------------------------------------------
# Nó LangGraph
# ---------------------------------------------------------------------------

def file_analyst(state: AgentState) -> dict:
    """
    Nó de análise focal de arquivo (chunk-and-consolidate).

    Fases:
      1. Leitura completa do arquivo-alvo
      2. Divisão em chunks (CHUNK_SIZE linhas, OVERLAP sobreposição)
      3. Análise LLM por chunk (chamadas leves)
      4. Consolidação LLM final (7 seções)
      5. Header com metadados do run
    """
    target = state.target_file
    if not target:
        raise ValueError("file_analyst: state.target_file está vazio.")

    path = Path(target)
    if not path.exists():
        raise FileNotFoundError(f"file_analyst: arquivo não encontrado: {path}")

    filename  = path.name
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # --- 1. Leitura ---
    lines = _read_file(path)
    print(f"[file_analyst] {filename}: {len(lines)} linhas")

    # --- 2. Chunking ---
    chunks = _split_chunks(lines)
    print(f"[file_analyst] {len(chunks)} blocos × {CHUNK_SIZE} linhas (overlap={OVERLAP})")

    # --- 3. Análise por chunk ---
    chunk_analyses: list[str] = []
    for idx, (start, end, chunk_lines) in enumerate(chunks, 1):
        analysis = _analyze_chunk(chunk_lines, idx, len(chunks), filename, start, end)
        chunk_analyses.append(analysis)

    # --- 4. Consolidação ---
    raw = _consolidate(chunk_analyses, filename, state.request)

    # --- 5. Header ---
    result = (
        f"# Análise Focal: `{filename}` — {timestamp}\n\n"
        f"**Pedido:** {state.request}  \n"
        f"**Arquivo:** `{target}`  \n"
        f"**Linhas:** {len(lines)}  \n"
        f"**Blocos analisados:** {len(chunks)}\n\n"
        "---\n\n"
        + raw.strip()
    )

    print(f"[file_analyst] análise concluída: {len(result):,} chars")

    return {
        "result": result,
        "logs": [
            f"file_analyst: {filename} — {len(lines)} linhas, "
            f"{len(chunks)} blocos, {len(result)} chars"
        ],
    }
