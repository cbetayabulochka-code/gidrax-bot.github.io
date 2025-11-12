import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

from config import Config
from database import DatabaseManager
from keyboards import get_main_menu_keyboard, remove_keyboard
from handlers.auth_handler import AuthHandler, WAITING_USERNAME, WAITING_PASSWORD
from handlers.shop_handler import ShopHandler
from handlers.support_handler import SupportHandler, CHOOSING_TYPE, REPORT_BUG, REPORT_PLAYER
from handlers.password_handler import PasswordHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class GidraXBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.auth_handler = AuthHandler(self.db)
        self.shop_handler = ShopHandler(self.db)
        self.support_handler = SupportHandler(self.db)
        self.password_handler = PasswordHandler(self.db)
        
        # Создаем Application
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Регистрируем обработчики
        self._setup_handlers()
    
    def _setup_handlers(self):
        # Команда /start
        self.application.add_handler(CommandHandler("start", self._start))
        
        # Команда /help
        self.application.add_handler(CommandHandler("help", self._help))
        
        # Обработчик авторизации (Conversation)
        auth_conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^(🔐 Авторизация|/auth)$"), self.auth_handler.start_auth)],
            states={
                WAITING_USERNAME: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.auth_handler.handle_username)
                ],
                WAITING_PASSWORD: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.auth_handler.handle_password)
                ],
            },
            fallbacks=[CommandHandler("cancel", self.auth_handler.cancel)]
        )
        self.application.add_handler(auth_conv_handler)
        
        # Обработчик поддержки (Conversation)
        support_conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^(🛠️ Техподдержка|/support)$"), self.support_handler.show_support_options)],
            states={
                CHOOSING_TYPE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.support_handler.handle_support_type)
                ],
                REPORT_BUG: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.support_handler.handle_bug_report)
                ],
                REPORT_PLAYER: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.support_handler.handle_player_report)
                ],
            },
            fallbacks=[CommandHandler("cancel", self.support_handler.cancel_support)]
        )
        self.application.add_handler(support_conv_handler)
        
        # Обработчики магазина
        self.application.add_handler(MessageHandler(filters.Regex("^(🛍️ Магазин|/shop)$"), self.shop_handler.show_catalog))
        self.application.add_handler(MessageHandler(filters.Regex("^(🔑 Сменить пароль|/password)$"), self.password_handler.start_password_change))
        
        # Обработчик кнопки "Назад"
        self.application.add_handler(MessageHandler(filters.Regex("^↩️ Назад$"), self._back_to_main))
        
        # Обработчик сообщений магазина
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & filters.Regex("^(👑 Привилегии|💰 Гемы|🎁 Кейсы|💳 Перейти к оплате|➕ Добавить ещё|↩️ Назад в каталог)$"),
            self.shop_handler.handle_shop_message
        ))
        
        # Обработчик всех остальных сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
    
    async def _start(self, update, context):
        await update.message.reply_text(
            "🤖 Добро пожаловать в GidraX Bot!\n\n"
            "Выберите действие из меню ниже:",
            reply_markup=get_main_menu_keyboard()
        )
    
    async def _help(self, update, context):
        await update.message.reply_text(
            "📋 Доступные команды:\n\n"
            "/start - начать работу\n"
            "/help - помощь\n"
            "/shop - магазин\n"
            "/support - техподдержка\n"
            "/password - сменить пароль"
        )
    
    async def _back_to_main(self, update, context):
        await update.message.reply_text(
            "🏠 Главное меню:",
            reply_markup=get_main_menu_keyboard()
        )
    
    async def _handle_message(self, update, context):
        # Обработка обычных сообщений
        message = update.message.text
        
        # Здесь можно добавить обработку других сообщений
        await update.message.reply_text(
            "❌ Неизвестная команда. Используйте меню или /help",
            reply_markup=get_main_menu_keyboard()
        )
    
    def run(self):
        logger.info("🚀 Starting GidraX Bot...")
        self.application.run_polling()

if __name__ == '__main__':
    bot = GidraXBot()
    bot.run()