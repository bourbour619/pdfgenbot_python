import logging
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from dotenv import load_dotenv
import os 
from modules import Activity

from PIL import Image

load_dotenv()

activity = Activity()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def start(update, context) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text='فایل یا فایل هاتو واسم بفرست ...')
    activity.init(id=update.effective_user.username)
    

def file_handler(update, context) -> None:
    fileDict = update.message.document or update.message.photo[-1]
    newFile = context.bot.get_file(fileDict.file_id)
    if newFile:
        name = fileDict['file_name'] if fileDict['file_name'] else fileDict['file_id']
        file_dir = activity.add(name=name)
        newFile.download(file_dir)
        context.bot.send_message(chat_id=update.effective_chat.id, text='فایلتو گرفتم .')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='فایلت نیومده که ....!')

    context.bot.send_message(chat_id=update.effective_chat.id, text='فایلهایی که تا الان واسم فرستادی ایناس  ...')
    all_files = activity.log()
    strcv = '\n'.join(all_files)
    context.bot.send_message(chat_id=update.effective_chat.id, text=strcv)
        

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