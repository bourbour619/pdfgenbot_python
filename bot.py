from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler
from dotenv import load_dotenv
import os 

load_dotenv()

bot_token = os.getenv('bot_token')
updater = Updater(token=bot_token, use_context=True)
dispatcher = updater.dispatcher

import logging 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def start(update, context):
    # context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    keyboard = [
        InlineKeyboardButton('راه اندازی مجدد', callback_data='1'),
        InlineKeyboardButton('ویرایش قبلی', callback_data='2'),
        InlineKeyboardButton('بریم بعدی', callback_data='3'),
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('چیکار کنیم رفیق ؟ ', reply_markup=reply_markup)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()