import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import random

logger = logging.getLogger(__name__)

# States for conversation
WAITING_USERNAME, WAITING_PASSWORD = range(2)

class AuthHandler:
    def __init__(self, database):
        self.db = database
        self.auth_sessions = {}
    
    async def start_auth(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        await update.message.reply_text(
            "👋 Добро пожаловать в GidraX Bot!\n\nНапишите свой никнейм с сервера Minecraft:",
            reply_markup=remove_keyboard()
        )
        self.auth_sessions[chat_id] = {'state': WAITING_USERNAME}
        return WAITING_USERNAME
    
    async def handle_username(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        username = update.message.text
        
        if self.db.user_exists(username):
            self.auth_sessions[chat_id] = {
                'state': WAITING_PASSWORD,
                'username': username
            }
            await update.message.reply_text("🔐 Теперь введите ваш пароль:")
            return WAITING_PASSWORD
        else:
            await update.message.reply_text(
                "❌ Этого аккаунта не существует.\n\n"
                "Зайдите на сервер и зарегистрируйтесь через команду:\n"
                "/reg [пароль] [повтор пароля]"
            )
            self.auth_sessions.pop(chat_id, None)
            return ConversationHandler.END
    
    async def handle_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        password = update.message.text
        session = self.auth_sessions.get(chat_id)
        
        if not session:
            await update.message.reply_text("❌ Сессия авторизации устарела. Начните заново /start")
            return ConversationHandler.END
        
        username = session['username']
        
        if self.db.verify_password(username, password):
            self.db.update_telegram_chat_id(username, str(chat_id))
            await update.message.reply_text("✅ Вы успешно авторизовались!")
            
            if self.db.is_twofa_enabled(username):
                code = self.generate_2fa_code()
                self.db.save_2fa_code(username, code)
                await update.message.reply_text(
                    f"🔒 Включена двухэтапная аутентификация.\n\n"
                    f"Введите в чат Minecraft команду:\n/link {code}"
                )
            else:
                from keyboards import get_main_menu_keyboard
                await update.message.reply_text(
                    "🎮 Ваш аккаунт зашел на сервер!",
                    reply_markup=get_main_menu_keyboard()
                )
        else:
            await update.message.reply_text("❌ Вы ввели неправильный пароль")
        
        self.auth_sessions.pop(chat_id, None)
        return ConversationHandler.END
    
    def generate_2fa_code(self):
        return str(random.randint(100000, 999999))
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        self.auth_sessions.pop(chat_id, None)
        await update.message.reply_text("❌ Авторизация отменена.")
        return ConversationHandler.END