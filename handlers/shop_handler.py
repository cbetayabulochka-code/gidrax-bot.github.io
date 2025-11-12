from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from keyboards import get_shop_categories_keyboard, get_shop_actions_keyboard

class ShopHandler:
    def __init__(self, database):
        self.db = database
        self.user_carts = {}
    
    async def show_catalog(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        catalog_text = self._generate_catalog_text()
        await update.message.reply_text(
            catalog_text,
            reply_markup=get_shop_categories_keyboard()
        )
    
    def _generate_catalog_text(self):
        text = "🛍️ Каталог товаров:\n\n"
        
        text += "👑 Привилегии:\n"
        for key, item in Config.SHOP_ITEMS['privileges'].items():
            text += f"• {item['name']} - {item['price']}₽\n"
        
        text += "\n💰 Гемы:\n"
        for key, item in Config.SHOP_ITEMS['gems'].items():
            text += f"• {item['name']} - {item['price']}₽\n"
        
        text += "\n🎁 Кейсы:\n"
        for key, item in Config.SHOP_ITEMS['cases'].items():
            text += f"• {item['name']} - {item['price']}₽\n"
        
        text += "\nНапишите название товара для покупки:"
        return text
    
    async def handle_shop_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text
        
        if message == "👑 Привилегии":
            await self._show_privileges(update)
        elif message == "💰 Гемы":
            await self._show_gems(update)
        elif message == "🎁 Кейсы":
            await self._show_cases(update)
        elif message == "💳 Перейти к оплате":
            await self._checkout(update)
        else:
            # Обработка выбора товара
            await self._handle_product_selection(update, message)
    
    async def _show_privileges(self, update: Update):
        text = "👑 Привилегии:\n\n"
        for key, item in Config.SHOP_ITEMS['privileges'].items():
            text += f"• {item['name']} - {item['price']}₽\n"
        text += "\nНапишите название привилегии для добавления в корзину:"
        await update.message.reply_text(text)
    
    async def _show_gems(self, update: Update):
        text = "💰 Гемы:\n\n"
        for key, item in Config.SHOP_ITEMS['gems'].items():
            text += f"• {item['name']} - {item['price']}₽\n"
        text += "\nНапишите количество гемов для добавления в корзину:"
        await update.message.reply_text(text)
    
    async def _show_cases(self, update: Update):
        text = "🎁 Кейсы:\n\n"
        for key, item in Config.SHOP_ITEMS['cases'].items():
            text += f"• {item['name']} - {item['price']}₽\n"
        text += "\nНапишите название кейса для добавления в корзину:"
        await update.message.reply_text(text)
    
    async def _handle_product_selection(self, update: Update, product_name: str):
        # Поиск товара во всех категориях
        product = None
        category = None
        
        for cat, items in Config.SHOP_ITEMS.items():
            for key, item in items.items():
                if item['name'].lower() == product_name.lower():
                    product = item
                    category = cat
                    break
        
        if product:
            chat_id = update.effective_chat.id
            if chat_id not in self.user_carts:
                self.user_carts[chat_id] = []
            
            self.user_carts[chat_id].append(product)
            total = sum(item['price'] for item in self.user_carts[chat_id])
            
            await update.message.reply_text(
                f"✅ Товар '{product['name']}' добавлен в корзину!\n"
                f"📦 В корзине: {len(self.user_carts[chat_id])} товаров\n"
                f"💰 Общая сумма: {total}₽",
                reply_markup=get_shop_actions_keyboard()
            )
        else:
            await update.message.reply_text("❌ Товар не найден. Проверьте название.")
    
    async def _checkout(self, update: Update):
        chat_id = update.effective_chat.id
        cart = self.user_carts.get(chat_id, [])
        
        if not cart:
            await update.message.reply_text("❌ Корзина пуста!")
            return
        
        total = sum(item['price'] for item in cart)
        cart_text = "\n".join([f"• {item['name']} - {item['price']}₽" for item in cart])
        
        await update.message.reply_text(
            f"💳 Оформление заказа:\n\n"
            f"{cart_text}\n\n"
            f"💰 Итого: {total}₽\n\n"
            f"Осуществите перевод на карту 2202 2084 3980 4486\n"
            f"В комментарии укажите 'На подарок'\n"
            f"После оплаты отправьте скриншот чека."
        )
        
        # Очищаем корзину
        self.user_carts[chat_id] = []