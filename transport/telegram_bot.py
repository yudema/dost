import os
import logging
import asyncio
from telegram.ext import ApplicationBuilder
from telegram.error import TelegramError
from django.conf import settings

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.app = None
        
        if self.bot_token and self.chat_id:
            try:
                self.app = ApplicationBuilder().token(self.bot_token).build()
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
    
    async def _send_message(self, text, parse_mode=None):
        """
        Вспомогательный метод для отправки сообщений
        """
        if not self.app or not self.chat_id:
            logger.warning("Telegram bot not configured properly")
            return False
            
        try:
            await self.app.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=parse_mode
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def test_connection(self):
        """
        Тестирует подключение к Telegram API
        """
        try:
            async def test():
                return await self._send_message(
                    "🔔 Тестовое сообщение\n\nЕсли вы видите это сообщение, значит бот настроен правильно!"
                )
            return asyncio.run(test())
        except Exception as e:
            logger.error(f"Test connection failed: {e}")
            return False
    
    def send_ticket_notification(self, ticket):
        """
        Отправляет уведомление о новом тикете в Telegram
        """
        try:
            message = (
                f"🔔 Новый тикет!\n\n"
                f"📧 Email: {ticket.email}\n"
                f"📝 Тема: {ticket.subject}\n"
                f"🆔 ID: {ticket.id}\n"
                f"⏰ Создан: {ticket.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            )
            
            if ticket.transport:
                message += f"🚚 Транспорт: {ticket.transport.number}\n"
            
            async def send():
                return await self._send_message(message, parse_mode='HTML')
            return asyncio.run(send())
            
        except Exception as e:
            logger.error(f"Failed to send ticket notification: {e}")
            return False

# Создаем глобальный экземпляр для использования во всем приложении
telegram_notifier = TelegramNotifier() 