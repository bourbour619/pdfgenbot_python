import logging
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from dotenv import load_dotenv
import os 
from modules import Activity


from PIL import Image
from uuid import uuid4

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
    if not activity.root:
        activity.init(id=update.effective_user.username)
    fileDict = update.message.document or update.message.photo[-1]
    newFile = context.bot.get_file(fileDict['file_id'])
    if newFile:
        name = str(uuid4()).split('-')[0] + '.jpeg'
        if update.message.document:
            name = fileDict['file_name']
        file_dir = activity.add(name=name)
        newFile.download(file_dir)
        context.bot.send_message(chat_id=update.effective_chat.id, text='فایلتو گرفتم .')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='فایلت نیومده که ....!')

    context.bot.send_message(chat_id=update.effective_chat.id, text='فایلهایی که تا الان واسم فرستادی ایناس  ...')
    all_files = activity.log()
    strcv = '\n'.join(all_files)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'تعداد فایلها: {len(all_files)} \n{strcv} \n اگه فایل ها اوکیه بریم که pdf اشو بسازیم ...' )
    context.bot.send_message(chat_id=update.effective_chat.id, text='واسه شروع تبدیل /convert_pdf رو بزن و واسه شروع از اول /start')

def convert_pdf(update, context) -> None:
    all_files = activity.log()
    exts = [f.split('.')[1] for f in all_files]
    print(exts)
    e = all_files[0].split('.')[1]
    if any( ext != e for ext in exts ):
        context.bot.send_message(chat_id=update.effective_chat.id, text='فرمت فایلهات یکی نیست و نمیشه ازینا pdf درست کرد یه بار دیگه امتحان کن از /start')
    else:
        if e != 'jpeg':
            context.bot.send_message(chat_id=update.effective_chat.id, text='فعلا فقط میتونی عکس رو به pdf تبدیل کنی باقی فرمت ها بعدا ایشالله :)')
        else:
            imgs = []
            for f in range(len(all_files)):
                imgs[f] = Image.open(all_files[f])
                imgs[f] = imgs[f].convert('RGB')

        

def run_bot() -> None:
    bot_token = os.getenv('bot_token')
    updater = Updater(token=bot_token, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo, file_handler))
    updater.dispatcher.add_handler(CommandHandler('convert_pdf', convert_pdf))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run_bot()