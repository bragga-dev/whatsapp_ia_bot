from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class IncomingMessage:
    channel: str
    chat_id: str
    text: str

    @property
    def session_id(self) -> str:
        return f'{self.channel}:{self.chat_id}'


class Channel(Protocol):
    name: str

    async def send(self, chat_id: str, text: str) -> None: ...