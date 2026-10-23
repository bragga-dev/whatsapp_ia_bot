from channels.telegram import TelegramChannel
from channels.whatsapp import WhatsAppChannel
from config import TELEGRAM_BOT_TOKEN


CHANNELS = {'whatsapp': WhatsAppChannel()}

if TELEGRAM_BOT_TOKEN:
    CHANNELS['telegram'] = TelegramChannel()