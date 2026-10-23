import asyncio
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException, Request, UploadFile

import vectorstore as rag
from channels import CHANNELS
from channels.base import IncomingMessage
from config import ADMIN_API_KEY
from message_buffer import buffer_message


MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def require_admin(x_api_key: str = Header(default='')):
    if not ADMIN_API_KEY:
        raise HTTPException(status_code=503, detail='ADMIN_API_KEY não configurada')
    if not secrets.compare_digest(x_api_key, ADMIN_API_KEY):
        raise HTTPException(status_code=401, detail='API key inválida')


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


@app.post('/rag/ingest', dependencies=[Depends(require_admin)])
async def rag_ingest(file: UploadFile = File(...)):
    name = Path(file.filename or '').name
    if Path(name).suffix.lower() not in rag.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail='Use arquivos .pdf, .txt ou .md')

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail='Arquivo maior que 10 MB')

    result = await asyncio.to_thread(rag.ingest_upload, name, content)
    if result['status'] == 'error':
        raise HTTPException(status_code=422, detail=result)
    return result


@app.post('/rag/reindex', dependencies=[Depends(require_admin)])
async def rag_reindex():
    return await asyncio.to_thread(rag.reindex)