import asyncio
import redis.asyncio as redis

from channels import CHANNELS
from channels.base import IncomingMessage
from chains import get_conversational_rag_chain
from config import REDIS_URL, BUFFER_KEY_SUFIX, DEBOUNCE_SECONDS, BUFFER_TTL


redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
conversational_rag_chain = get_conversational_rag_chain()
debounce_tasks: dict[str, asyncio.Task] = {}

def log(*args):
    print('[BUFFER]', *args)


async def buffer_message(message: IncomingMessage):
    session_id = message.session_id
    buffer_key = f'{session_id}{BUFFER_KEY_SUFIX}'

    await redis_client.rpush(buffer_key, message.text)
    await redis_client.expire(buffer_key, BUFFER_TTL)

    log(f'Mensagem adicionada ao buffer de {session_id}: {message.text}')

    task = debounce_tasks.get(session_id)
    if task and not task.done():
        task.cancel()
        log(f'Debounce resetado para {session_id}')

    debounce_tasks[session_id] = asyncio.create_task(handle_debounce(message))


async def handle_debounce(message: IncomingMessage):
    session_id = message.session_id
    buffer_key = f'{session_id}{BUFFER_KEY_SUFIX}'

    try:
        log(f'Iniciando debounce para {session_id}')
        await asyncio.sleep(float(DEBOUNCE_SECONDS))

        messages = await redis_client.lrange(buffer_key, 0, -1)
        full_message = ' '.join(messages).strip()

        if full_message:
            log(f'Enviando mensagem agrupada para {session_id}: {full_message}')
            result = await conversational_rag_chain.ainvoke(
                input={'input': full_message},
                config={'configurable': {'session_id': session_id}},
            )
            sources = sorted({d.metadata.get('source', '?') for d in result.get('context', [])})
            log(f'Fontes do RAG para {session_id}: {sources}')
            await CHANNELS[message.channel].send(message.chat_id, result['answer'])

        await redis_client.delete(buffer_key)

    except asyncio.CancelledError:
        log(f'Debounce cancelado para {session_id}')
    except Exception as error:
        log(f'Erro ao processar {session_id}: {error!r}')
        await redis_client.delete(buffer_key)