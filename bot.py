import logging
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from dotenv import load_dotenv
import os 
import Activity

from PIL import Image

load_dotenv()

activity = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update, context) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text='فایل یا فایل هاتو واسم بفرست ...')
    activity = Activity(id=update.effective_user.username)
    

def file_handler(update, context) -> None:
    fileDict = update.message.document or update.message.photo[-1]
    newFile = context.bot.get_file(fileDict.file_id)
    if newFile:
        file_dir = activity.add(name=fileDict.file_name or fileDict.file_id)
        newFile.download(file_dir)
        context.bot.send_message(chat_id=update.effective_chat.id, text='فایلتو گرفتم .')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='فایلت نیومده که ....!')
        

#def convert_pdf():


def run_bot() -> None:
    bot_token = os.getenv('bot_token')
    updater = Updater(token=bot_token, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo, file_handler))
#    updater.dispatcher.add_handler(CommandHandler('convert_pdf', convert_pdf))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run_bot()