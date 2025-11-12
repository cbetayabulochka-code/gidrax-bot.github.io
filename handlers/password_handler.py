from telegram import Update
from telegram.ext import ContextTypes

class PasswordHandler:
    def __init__(self, database):
        self.db = database
    
    async def start_password_change(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🔑 Смена пароля\n\n"
            "Введите новый пароль и его подтверждение через пробел:\n"
            "Пример: новыйпароль повторпароля"
        )
    
    async def handle_password_change(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text
        parts = message.split()
        
        if len(parts) == 2 and parts[0] == parts[1]:
            await update.message.reply_text("✅ Пароль успешно изменен!")
        else:
            await update.message.reply_text("❌ Пароли не совпадают!")