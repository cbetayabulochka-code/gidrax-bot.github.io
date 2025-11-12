from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards import get_support_type_keyboard

# States for support conversation
CHOOSING_TYPE, REPORT_BUG, REPORT_PLAYER = range(3)

class SupportHandler:
    def __init__(self, database):
        self.db = database
        self.support_sessions = {}
    
    async def show_support_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🛠️ Техподдержка\n\nВыберите тип обращения:",
            reply_markup=get_support_type_keyboard()
        )
        return CHOOSING_TYPE
    
    async def handle_support_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text
        chat_id = update.effective_chat.id
        
        if message == "🐞 Сообщить о баге":
            self.support_sessions[chat_id] = {'type': 'bug'}
            await update.message.reply_text(
                "🐞 Сообщение о баге\n\nОпишите баг который вы обнаружили:",
                reply_markup=remove_keyboard()
            )
            return REPORT_BUG
        
        elif message == "🚨 Пожаловаться на игрока":
            self.support_sessions[chat_id] = {'type': 'complaint'}
            await update.message.reply_text(
                "🚨 Жалоба на игрока\n\nВведите ник игрока на которого хотите пожаловаться:",
                reply_markup=remove_keyboard()
            )
            return REPORT_PLAYER
        
        elif message == "↩️ Назад":
            from keyboards import get_main_menu_keyboard
            await update.message.reply_text(
                "🏠 Главное меню:",
                reply_markup=get_main_menu_keyboard()
            )
            return ConversationHandler.END
    
    async def handle_bug_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        description = update.message.text
        session = self.support_sessions.get(chat_id)
        
        if session and session['type'] == 'bug':
            # Здесь можно сохранить в БД
            await update.message.reply_text(
                "✅ Спасибо за сообщение о баге!\n"
                "Администрация проверит его в ближайшее время."
            )
        
        self.support_sessions.pop(chat_id, None)
        from keyboards import get_main_menu_keyboard
        await update.message.reply_text(
            "🏠 Главное меню:",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END
    
    async def handle_player_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        target_player = update.message.text
        session = self.support_sessions.get(chat_id)
        
        if session and session['type'] == 'complaint':
            session['target_player'] = target_player
            await update.message.reply_text(
                f"👤 Игрок: {target_player}\n\n"
                f"Опишите какое правонарушение совершил игрок:"
            )
            return REPORT_BUG  # Переиспользуем состояние для описания
    
    async def cancel_support(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        self.support_sessions.pop(chat_id, None)
        
        from keyboards import get_main_menu_keyboard
        await update.message.reply_text(
            "❌ Обращение в поддержку отменено.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END