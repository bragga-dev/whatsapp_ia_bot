from langchain_openai import ChatOpenAI

from config import (
    LLM_API_KEYS,
    LLM_CHAIN,
    LLM_TEMPERATURE,
    LLM_TIMEOUT,
    OLLAMA_BASE_URL,
)


BASE_URLS = {
    'openai': None,
    'groq': 'https://api.groq.com/openai/v1',
    'google': 'https://generativelanguage.googleapis.com/v1beta/openai/',
    'openrouter': 'https://openrouter.ai/api/v1',
    'mistral': 'https://api.mistral.ai/v1',
    'cerebras': 'https://api.cerebras.ai/v1',
    'ollama': OLLAMA_BASE_URL,
}


def log(*args):
    print('[LLM]', *args)


def _build(provider: str, model: str):
    if provider not in BASE_URLS:
        raise ValueError(f'Provedor desconhecido em LLM_CHAIN: {provider}')

    api_key = 'ollama' if provider == 'ollama' else LLM_API_KEYS.get(provider)
    if not api_key:
        log(f'Ignorando {provider}:{model} (sem API key)')
        return None

    return ChatOpenAI(
        model=model,
        base_url=BASE_URLS[provider],
        api_key=api_key,
        temperature=LLM_TEMPERATURE,
        timeout=LLM_TIMEOUT,
        max_retries=0,  
    )


def get_llm():
    models = []
    for item in (i.strip() for i in LLM_CHAIN.split(',')):
        if not item:
            continue
        provider, _, model = item.partition(':')
        llm = _build(provider.strip().lower(), model.strip())
        if llm:
            models.append(llm)

    if not models:
        raise RuntimeError('LLM_CHAIN vazio ou sem nenhuma API key válida')

    primary, *fallbacks = models
    return primary.with_fallbacks(fallbacks) if fallbacks else primary