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
    markup.row(
        KeyboardButton('* به pdf'),
        KeyboardButton('pdf به *'),
    )
    markup.row(
        KeyboardButton('یکی کردن pdf'),
        KeyboardButton('لیست فایلها')
    )
    bot.send_message(cid, 'چیکار میخوای کنی ؟ :(', reply_markup=markup )
    activity.init(id=user)

@bot.message_handler(func= lambda msg: msg.text == '* به pdf')
def to_pdf(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not activity.root:
        activity.init(id=user)
    activity.type = '*topdf'
    bot.send_message(cid, 'فایلتو برام بفرست ... ')
    
@bot.message_handler(func= lambda msg: msg.text == 'pdf به *')
def to_pdf(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not activity.root:
        activity.init(id=user)
    activity.type = 'pdfto*'
    bot.send_message(cid, 'فایلتو برام بفرست ... ')

@bot.message_handler(func= lambda msg: msg.text == 'یکی کردن pdf')
def to_pdf(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not activity.root:
        activity.init(id=user)
    activity.type = 'mergepdfs'
    bot.send_message(cid, 'فایلتو برام بفرست ... ')

@bot.message_handler(func= lambda msg: msg.text == 'لیست فایلها')
def to_pdf(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not activity.root:
        activity.init(id=user)
    activity.type = 'listofoutputs'
    bot.send_message(cid, 'فایلتو برام بفرست ... ')





@bot.message_handler(content_types=['document', 'photo'])
def file_handler(msg):
    cid = msg.chat.id
    if not any(activity.type):
        bot.send_message(cid, 'لطفا برای استفاده از بات از /start شروع نمایید')
    fileObj = msg.document or msg.photo[-1]
    file_info = bot.get_file(fileObj.file_id)
    if file_info:
        name = str(uuid4()).split('-')[0] + '.jpeg'
        ext = 'jpeg'
        if msg.document:
            name = fileObj.file_name
            ext = fileObj.file_name.split('.')[1]
        if ext not in activity.known:
            bot.send_message(cid, 'فایلی که فرستادی به درد من نمیخوره :(')
        if activity.type == '*topdf':
            if ext == 'pdf':
                bot.send_message(cid, 'فایلی که فرستادی خودش pdf :)')
            else:
                save = activity.add(name=name)
                activity.current = save
                resp = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(bot_token, file_info.file_path))
                bot.send_chat_action(cid, 'typing')
                time.sleep(2)
                if resp.ok:
                    with open(save, 'wb') as f:
                        f.write(resp.content)
                    markup = InlineKeyboardMarkup(row_width=2)
                    markup.row(
                        InlineKeyboardButton(text='حذف', callback_data='delfile'),
                        InlineKeyboardButton(text='تبدیل ', callback_data='cvtopdf')
                    )
                    bot.send_message(cid, 'فایلتو گرفتم !', reply_markup=markup)
        if activity.type == 'pdfto*':
            if ext != 'pdf':
                bot.send_message(cid, 'فایلی که فرستادی pdf نیست :(')
            else:
                save = activity.add(name=name)
                activity.current = name
                resp = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(bot_token, file_info.file_path))
                bot.send_chat_action(cid, 'typing')
                time.sleep(2)
                if resp.ok:
                    with open(save, 'wb') as f:
                        f.write(resp.content)
                    markup = InlineKeyboardMarkup(row_width=2)
                    markup.row(
                        InlineKeyboardButton(text='حذف', callback_data='delfile'),
                        InlineKeyboardButton(text='تبدیل ', callback_data='cvfrompdf')
                    )
                    bot.send_message(cid, 'فایلتو گرفتم !', reply_markup=markup)



def delfile(cid):
    activity.remove()
    bot.send_message(cid, 'فایلت حذف شد ')




@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data:
        func = call.data
        cid = call.message.chat.id
        return func(cid)




bot.polling()
