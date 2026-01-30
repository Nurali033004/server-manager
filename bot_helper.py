# Bu skript yordamida botingizga "Web App" tugmachasini qo'shishingiz mumkin
# pyTelegramBotAPI (telebot) kutubxonasi ishlatilgan

import telebot
from telebot import types

BOT_TOKEN = "SIZNING_BOT_TOKENINGIZ"
WEB_APP_URL = "SIZNING_CLOUDFLARE_URLINGIZ" # System Manager'dan olingan URL

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Web App tugmachasini yaratish
    web_app = types.WebAppInfo(WEB_APP_URL)
    btn = types.KeyboardButton("💻 Cloud IDE (4 Bo'lim)", web_app=web_app)
    markup.add(btn)
    
    bot.send_message(message.chat.id, "Salom! Cloud IDE boshqaruv panelini ochish uchun pastdagi tugmani bosing.", reply_markup=markup)

print("Bot ishga tushdi...")
bot.infinity_polling()
