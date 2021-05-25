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
    if not activity.root:
        activity.init(id=update.effective_user.username)
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
            all_dirs = [os.path.join(activity.root, f) for f in all_files]
            for d in all_dirs:
                imgs.append(Image.open(d))
            for im in range(len(imgs)):
                imgs[im] = imgs[im].convert('RGB')
            name = str(uuid4()).split('-')[0] + '.pdf'
            pdf_dir = activity.add(name=name)
            imgs[0].save(f'{pdf_dir}', save_all=True, append_images=imgs)
            pdf_file = filter(lambda f: f.split('.')[1] == 'pdf', activity.log())[0]
            context.bot.send_message(chat_id=update.effective_chat.id, text=f'فایل pdf ات آماده شد بفرما ... \n {pdf_file}')
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(os.path.join(activity.root, pdf_file), 'rb'))
        

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