import logging
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os 
import time
from classes import Activity
import requests



from PIL import Image
from uuid import uuid4

load_dotenv()

activity = Activity()

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot_token = os.getenv('bot_token')
bot = telebot.TeleBot(token=bot_token, parse_mode=None)




@bot.message_handler(commands=['start'])
def start(msg):
    cid = msg.chat.id
    user = msg.chat.username
    markup = ReplyKeyboardMarkup(row_width=2)
    btns = [
        KeyboardButton('* به pdf'),
        KeyboardButton('pdf به *'),
        KeyboardButton('یکی کردن pdf'),
        KeyboardButton('لیست فایلها')
    ]
    for btn in btns:
        markup.add(btn)
    bot.send_message(cid, 'چیکار میخوای کنی ؟ :(', reply_markup=markup )
    activity.init(id=user)

@bot.message_handler(func= lambda msg: msg.text == '* به pdf')
def to_pdf(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not activity.root:
        activity.init(id=user)
    activity.current = '*topdf'
    bot.send_message(cid, 'فایلتو برام بفرست ... ')


@bot.message_handler(func = lambda msg: msg.document.mime_type.split('/')[1] in activity.accepted, content_types=['document', 'photo'])
def correct_file_handler(msg):
    cid = msg.chat.id
    if not any(activity.current):
        bot.send_message(cid, 'لطفا برای استفاده از بات از /start شروع نمایید')
    fileObj = msg.document or msg.photo[-1]
    file_info = bot.get_file(fileObj.file_id)
    if file_info:
        name = str(uuid4()).split('-')[0] + '.jpeg'
        ext = 'jpeg'
        if msg.document:
            name = fileObj.file_name
            ext = fileObj.mime_type.split('/')[1]
        if activity.current == '*topdf' and ext == 'pdf':
            bot.send_message(cid, 'فایلی که فرستادی خودش pdf :)')
        else:
            save = activity.add(name=name)
            resp = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(bot_token, file_info.file_path))
            bot.send_chat_action(cid, 'typing')
            time.sleep(2)
            if resp.ok:
                with open(save, 'w') as f:
                    f.write(resp.content)
                markup = InlineKeyboardMarkup(row_width=2)
                btns = [
                    InlineKeyboardButton(text='حذف فایل', callback_data='delete_file'),
                    InlineKeyboardButton(text='حذف فایل', callback_data='convert_file')
                ]
                for btn in btns:
                    markup.add(btn)
                bot.send_message(cid, 'فایلتو گرفتم !', reply_markup=markup)
                
            
                



@bot.message_handler(func = lambda msg: msg.document.mime_type.split('/')[1]  not in activity.accepted, content_types=['document'])
def wrong_file_handler(msg):
    ext = msg.document.mime_type
    bot.reply_to(msg, f'فرمت فایلی که فرستادی یعنی {ext} به کار من نمیاد')


bot.polling()