import asyncio
import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from config import AI_SYSTEM_PROMPT, HISTORY_MESSAGES, RAG_MIN_SCORE, RAG_TOP_K
from llm import get_llm
from memory import get_session_history
from vectorstore import get_vectorstore, search


llm = get_llm()
get_vectorstore()  # pré-carrega modelo e índice no startup

CONTEXT_HEADER = (
    'Informações de apoio (use apenas se forem relevantes para a pergunta; '
    'nunca cite "documento", "contexto" ou "base de conhecimento"):\n'
)


def _system_prompt(context: str) -> str:
    block = f'{CONTEXT_HEADER}{context}' if context else ''
    prompt = AI_SYSTEM_PROMPT or ''
    if '{context}' in prompt:
        return prompt.replace('{context}', block).strip()
    return f'{prompt}\n\n{block}'.strip()


def _search_query(past: list, text: str) -> str:
    # mensagem curta ("e o preço?") perde o assunto: junta com a pergunta anterior
    if len(text.split()) >= 6:
        return text
    last_human = next((m.content for m in reversed(past) if isinstance(m, HumanMessage)), '')
    return f'{last_human} {text}'.strip()


def _clean(text) -> str:
    if not isinstance(text, str):
        text = ''.join(part.get('text', '') if isinstance(part, dict) else str(part) for part in text)
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


async def answer(session_id: str, text: str) -> dict:
    history = get_session_history(session_id)

    past = (await asyncio.to_thread(lambda: history.messages))[-HISTORY_MESSAGES:]
    while past and isinstance(past[0], AIMessage):
        past = past[1:]

    hits = await asyncio.to_thread(search, _search_query(past, text), RAG_TOP_K)
    relevant = [(doc, score) for doc, score in hits if score >= RAG_MIN_SCORE]
    context = '\n\n'.join(doc.page_content for doc, _ in relevant)

    response = await llm.ainvoke([
        SystemMessage(_system_prompt(context)),
        *past,
        HumanMessage(text),
    ])
    reply = _clean(response.content) or 'Desculpe, não consegui responder agora. Pode repetir?'

    await asyncio.to_thread(history.add_messages, [HumanMessage(text), AIMessage(reply)])

    return {
        'answer': reply,
        'sources': sorted({doc.metadata.get('source', '?') for doc, _ in relevant}),
        'scores': [round(score, 2) for _, score in hits],
    }