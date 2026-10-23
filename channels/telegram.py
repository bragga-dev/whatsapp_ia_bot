import asyncio

import httpx

from channels.base import IncomingMessage
from config import TELEGRAM_BOT_TOKEN, WELCOME_MESSAGE


class TelegramChannel:
    name = 'telegram'

    def __init__(self):
        self._api = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'
        self._client = httpx.AsyncClient(timeout=70)

    async def send(self, chat_id: str, text: str) -> None:
        response = await self._client.post(
            f'{self._api}/sendMessage',
            json={'chat_id': chat_id, 'text': text[:4096]},
        )
        response.raise_for_status()

    async def typing(self, chat_id: str) -> None:
        await self._client.post(
            f'{self._api}/sendChatAction',
            json={'chat_id': chat_id, 'action': 'typing'},
        )

    async def poll(self, on_message) -> None:
        offset = None
        while True:
            try:
                params = {'timeout': 50, 'allowed_updates': '["message"]'}
                if offset is not None:
                    params['offset'] = offset

                response = await self._client.get(f'{self._api}/getUpdates', params=params)
                response.raise_for_status()

                for update in response.json().get('result', []):
                    offset = update['update_id'] + 1
                    message = update.get('message') or {}
                    chat = message.get('chat') or {}
                    text = message.get('text')

                    if text and chat.get('type') == 'private':
                        if text.strip() == '/start':
                            await self.send(str(chat['id']), WELCOME_MESSAGE)
                            continue

                        await on_message(IncomingMessage(
                            channel=self.name,
                            chat_id=str(chat['id']),
                            text=text,
                        ))
            except asyncio.CancelledError:
                raise
            except Exception as error:
                # não logar str(error): a URL do httpx contém o token do bot
                print('[TELEGRAM] Erro no polling:', type(error).__name__)
                await asyncio.sleep(5)