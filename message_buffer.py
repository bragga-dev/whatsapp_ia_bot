import asyncio
import time

import redis.asyncio as redis

from channels import CHANNELS
from channels.base import IncomingMessage
from chains import answer
from config import REDIS_URL, BUFFER_KEY_SUFIX, DEBOUNCE_SECONDS, BUFFER_TTL


redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
debounce_tasks: dict[str, asyncio.Task] = {}

def log(*args):
    print('[BUFFER]', *args)


async def _keep_typing(channel, chat_id: str):
    typing = getattr(channel, 'typing', None)
    if not typing:
        return
    while True:
        try:
            await typing(chat_id)
        except Exception:
            pass
        await asyncio.sleep(4)


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
        await asyncio.sleep(float(DEBOUNCE_SECONDS))

        messages = await redis_client.lrange(buffer_key, 0, -1)
        full_message = ' '.join(messages).strip()

        if full_message:
            log(f'Processando {session_id}: {full_message}')
            channel = CHANNELS[message.channel]

            typing_task = asyncio.create_task(_keep_typing(channel, message.chat_id))
            started = time.monotonic()
            try:
                result = await answer(session_id, full_message)
            finally:
                typing_task.cancel()

            log(
                f'Resposta em {time.monotonic() - started:.1f}s | '
                f'fontes: {result["sources"]} | scores: {result["scores"]}'
            )
            await channel.send(message.chat_id, result['answer'])

        await redis_client.delete(buffer_key)

    except asyncio.CancelledError:
        log(f'Debounce cancelado para {session_id}')
    except Exception as error:
        log(f'Erro ao processar {session_id}: {error!r}')
        await redis_client.delete(buffer_key)