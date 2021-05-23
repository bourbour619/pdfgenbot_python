from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from dotenv import load_dotenv
import os 

load_dotenv()

import logging 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


def start(update: Update, _: CallbackContext) -> None:
    # context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    keyboard = [
        InlineKeyboardButton('راه اندازی مجدد', callback_data='1'),
        InlineKeyboardButton('ویرایش قبلی', callback_data='2'),
        InlineKeyboardButton('بریم بعدی', callback_data='3'),
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('چیکار کنیم رفیق ؟ ', reply_markup=reply_markup)


def run_bot() -> None:
    bot_token = os.getenv('bot_token')
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run_bot()