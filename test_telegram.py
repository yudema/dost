import os
import django
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'transport.settings')
django.setup()

from transport.telegram_bot import telegram_notifier

def test_bot():
    print("Testing Telegram bot connection...")
    if telegram_notifier.test_connection():
        print("✅ Bot connection successful!")
    else:
        print("❌ Bot connection failed!")
        print("\nPlease check:")
        print("1. Bot token in .env file")
        print("2. Chat ID in .env file")
        print("3. Internet connection")
        print("4. Bot is added to the chat")

if __name__ == '__main__':
    test_bot() 