import logging
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from dotenv import load_dotenv
import os 

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update, context) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text='فایل یا فایل هاتو واسم بفرست ...')


def file_handler(update, context) -> None:
    file_id = update.message.document.file_id
    newFile = context.bot.get_file(file_id)
    if newFile:
        newFile.download()
        context.bot.send_message(chat_id=update.effective_chat.id, text='.فایلتو گرفتم')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='فایلت نیومده که ....!')
        

def run_bot() -> None:
    bot_token = os.getenv('bot_token')
    updater = Updater(token=bot_token, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo, file_handler))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run_bot()