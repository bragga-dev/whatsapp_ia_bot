import os

from dotenv import load_dotenv


load_dotenv()

LLM_CHAIN = os.getenv('LLM_CHAIN', '')
LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0'))
LLM_TIMEOUT = float(os.getenv('LLM_TIMEOUT', '30'))
LLM_REASONING_EFFORT = os.getenv('LLM_REASONING_EFFORT', '')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://host.docker.internal:11434/v1')
LLM_API_KEYS = {
    provider: os.getenv(f'{provider.upper()}_API_KEY')
    for provider in ('openai', 'groq', 'google', 'openrouter', 'mistral', 'cerebras')
}

AI_SYSTEM_PROMPT = os.getenv('AI_SYSTEM_PROMPT')

HISTORY_MESSAGES = int(os.getenv('HISTORY_MESSAGES', '10'))
RAG_TOP_K = int(os.getenv('RAG_TOP_K', '4'))
RAG_MIN_SCORE = float(os.getenv('RAG_MIN_SCORE', '0.25'))

VECTOR_STORE_PATH = os.getenv('VECTOR_STORE_PATH')
RAG_FILES_DIR = os.getenv('RAG_FILES_DIR')
EMBEDDINGS_MODEL = os.getenv(
    'EMBEDDINGS_MODEL',
    'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2',
)
EMBEDDINGS_CACHE_DIR = os.getenv('EMBEDDINGS_CACHE_DIR', 'models_cache')

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY')
WELCOME_MESSAGE = os.getenv('WELCOME_MESSAGE', 'Olá! Como posso ajudar?')

EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL')
EVOLUTION_INSTANCE_NAME = os.getenv('EVOLUTION_INSTANCE_NAME')
EVOLUTION_AUTHENTICATION_API_KEY = os.getenv('AUTHENTICATION_API_KEY')

REDIS_URL = os.getenv('CACHE_REDIS_URI')
BUFFER_KEY_SUFIX = os.getenv('BUFFER_KEY_SUFIX')
DEBOUNCE_SECONDS = os.getenv('DEBOUNCE_SECONDS')
BUFFER_TTL = os.getenv('BUFFER_TTL')