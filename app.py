import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from channels import CHANNELS
from channels.base import IncomingMessage
from message_buffer import buffer_message


@asynccontextmanager
async def lifespan(app: FastAPI):
    tasks = []
    telegram = CHANNELS.get('telegram')
    if telegram:
        tasks.append(asyncio.create_task(telegram.poll(buffer_message)))

    yield

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


app = FastAPI(lifespan=lifespan)


@app.post('/webhook')
async def webhook(request: Request):
    data = await request.json()
    payload = data.get('data') or {}
    key = payload.get('key') or {}
    content = payload.get('message') or {}

    chat_id = key.get('remoteJid')
    text = content.get('conversation') or (content.get('extendedTextMessage') or {}).get('text')

    if chat_id and text and not key.get('fromMe') and '@g.us' not in chat_id:
        await buffer_message(IncomingMessage(
            channel='whatsapp',
            chat_id=chat_id,
            text=text,
        ))

    return {'status': 'ok'}