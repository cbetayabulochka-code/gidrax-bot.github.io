import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram Bot
    BOT_TOKEN = os.getenv('BOT_TOKEN', '7861350899:AAHst0DfbXxv9KhBVg4xJvJBxsuKPKSjHog')
    ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '-1001234567890')
    
    # Database (BotHost предоставляет эти данные)
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'bot_host_db')
    DB_USER = os.getenv('DB_USERNAME', 'bot_host_user')
    DB_PASS = os.getenv('DB_PASSWORD', '')
    
    # Shop items
    SHOP_ITEMS = {
        'privileges': {
            'titan': {'name': 'Titan', 'price': 19},
            'hegceg': {'name': 'Hegceg', 'price': 49},
            'prince': {'name': 'Prince', 'price': 129},
            'shadow': {'name': 'Shadow', 'price': 179},
            'legenda': {'name': 'Legenda', 'price': 249},
            'magistor': {'name': 'Magistor', 'price': 449},
            'immortal': {'name': 'Immortal', 'price': 639},
            'overlord': {'name': 'Overlord', 'price': 879},
            'paladin': {'name': 'Paladin', 'price': 1099},
            'phantom': {'name': 'Phantom', 'price': 1499},
            'imperator': {'name': 'Imperator', 'price': 1999},
        },
        'gems': {
            '100': {'name': '100 Gems', 'price': 19},
            '500': {'name': '500 Gems', 'price': 89},
            '1000': {'name': '1000 Gems', 'price': 179},
            '5000': {'name': '5000 Gems', 'price': 739},
            '10000': {'name': '10000 Gems', 'price': 1599},
        },
        'cases': {
            '1_dk': {'name': '1 DK Case', 'price': 49},
            '3_dk': {'name': '3 DK Cases', 'price': 89},
            '5_dk': {'name': '5 DK Cases', 'price': 159},
            '10_dk': {'name': '10 DK Cases', 'price': 279},
        }
    }