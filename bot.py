import logging
import telebot
from telebot.apihelper import _make_request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
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



bot_token = os.getenv('bot_token')
bot = telebot.TeleBot(token=bot_token, parse_mode=None)


@bot.message_handler(commands=['start'])
def start(msg):
    cid = msg.chat.id
    user = msg.chat.username
    markup = ReplyKeyboardMarkup(row_width=2)
    btns = [
        KeyboardButton('تبدیل از PDF'),
        KeyboardButton('تبدیل به PDF')
    ]
    bot.send_message(cid, 'فایل یا فایل هاتو واسم بفرست ...' )
    activity.init(id=user)

@bot.message_handler(func = lambda msg: msg.document.mime_type.split('/')[1] in activity.accepted, content_types=['document', 'photo'])
def correct_file_handler(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not activity.root:
        activity.init(id=user)
    dict = msg.document or msg.photo[-1]
    file = bot.get_file(dict['file_id'])
    if file:
        name = str(uuid4()).split('-')[0] + '.jpeg'
        ext = 'jpeg'
        if msg.document:
            name = dict['file_name']
            ext = dict['mime_type'].split('/')[1]
        file_dir = activity.add(name=name)
        file.download(file_dir)
        if ext == 'pdf':
            markup = ReplyKeyboardMarkup(row_width=1)
            btns = [
                KeyboardButton('تبدیل از PDF به یه چی دیگه'),
                KeyboardButton('فایلو پاک کن'),
                KeyboardButton('نشونم بده فایل هامو')
            ]
            markup.add(btns)
            bot.send_message(cid, 'فایلتو گرفتم، چیکار کنم حالا ؟ ', reply_markup=markup)


@bot.message_handler(func = lambda msg: msg.document.mime_type.split('/')[1]  not in activity.accepted, content_types=['document'])
def wrong_file_handler(msg):
    ext = msg.document.mime_type
    bot.reply_to(msg, f'فرمت فایلی که فرستادی یعنی {ext} به کار من نمیاد')


bot.polling()