import httpx

from config import (
    EVOLUTION_API_URL,
    EVOLUTION_AUTHENTICATION_API_KEY,
    EVOLUTION_INSTANCE_NAME,
)


class WhatsAppChannel:
    name = 'whatsapp'

    def __init__(self):
        self._client = httpx.AsyncClient(
            timeout=30,
            headers={'apikey': EVOLUTION_AUTHENTICATION_API_KEY},
        )

    async def send(self, chat_id: str, text: str) -> None:
        response = await self._client.post(
            f'{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE_NAME}',
            json={'number': chat_id, 'text': text},
        )
        response.raise_for_status()