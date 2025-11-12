from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

def get_main_menu_keyboard():
    keyboard = [
        ['🛍️ Магазин', '🔐 Авторизация'],
        ['🛠️ Техподдержка', '🔑 Сменить пароль']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_support_type_keyboard():
    keyboard = [
        ['🐞 Сообщить о баге', '🚨 Пожаловаться на игрока'],
        ['↩️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_shop_categories_keyboard():
    keyboard = [
        ['👑 Привилегии', '💰 Гемы'],
        ['🎁 Кейсы'],
        ['↩️ Назад']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def get_shop_actions_keyboard():
    keyboard = [
        ['➕ Добавить ещё', '💳 Перейти к оплате'],
        ['↩️ Назад в каталог']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

def remove_keyboard():
    return ReplyKeyboardRemove()