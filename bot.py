import logging
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os 
import time
from classes import Activity, merge_pdfs_func
import requests


from uuid import uuid4

load_dotenv()

activity = Activity()

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot_token = os.getenv('bot_token')
bot = telebot.TeleBot(token=bot_token, parse_mode=None)




@bot.message_handler(commands=['start'])
def start(msg):
    if activity:
        activity.flush()
    cid = msg.chat.id
    user = msg.chat.username
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.row(
        KeyboardButton('پی دی اف به بقیه'),
        KeyboardButton('بقیه به پی دی اف'),
    )
    markup.row(
        KeyboardButton('لیست فایلها'),
        KeyboardButton('یکی کردن پی دی اف ها')
    )
    bot.send_message(cid, 'چیکار میخوای کنی ؟ :)', reply_markup=markup )
    activity.init(id=user)

@bot.message_handler(func= lambda msg: msg.text == 'پی دی اف به بقیه')
def from_pdf(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not activity.root:
        activity.init(id=user)
    activity.type = 'pdfto*'
    bot.send_message(cid, 'فایلتو برام بفرست ... ')
    
@bot.message_handler(func= lambda msg: msg.text == 'بقیه به پی دی اف')
def to_pdf(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not activity.root:
        activity.init(id=user)
    activity.type = '*topdf'
    bot.send_message(cid, 'فایلتو برام بفرست ... ')

@bot.message_handler(func= lambda msg: msg.text == 'یکی کردن پی دی اف ها')
def merge_pdfs(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not activity.root:
        activity.init(id=user)
    activity.type = 'mergepdfs'
    bot.send_message(cid, 'فایل هاتو برام بفرست ... ')

@bot.message_handler(func= lambda msg: msg.text == 'لیست فایلها')
def list_files(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not activity.root:
        activity.init(id=user)
    log = '\n'.join(activity.log())
    bot.send_message(cid, f'فایلهایی که واسم فرستادی : {log} \n\t\t تعداد فایلها : {len(activity.log())}')
    

@bot.message_handler(func= lambda msg: msg.text == 'مرحله قبلی')
def prev_step(msg):
    cid = msg.chat.id
    bot.send_message(cid, 'فایلتو برام بفرست ... ')
    markup = ReplyKeyboardMarkup(row_width=2)
    markup.row(
        KeyboardButton('پی دی اف به بقیه'),
        KeyboardButton('بقیه به پی دی اف'),
    )
    markup.row(
        KeyboardButton('لیست فایلها'),
        KeyboardButton('یکی کردن پی دی اف ها')
    )
    bot.send_message(cid, 'چیکار میخوای کنی ؟ :)', reply_markup=markup )



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
            bot.send_message(cid, 'فایلی که فرستادی به درد من نمیخوره :)')
        if activity.type == '*topdf':
            if ext == 'pdf':
                bot.send_message(cid, 'فایلی که فرستادی خودش pdf :)')
            else:
                save = activity.add(name=name)
                resp = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(bot_token, file_info.file_path))
                if resp.ok:
                    with open(save, 'wb') as f:
                        f.write(resp.content)
                    bot.send_chat_action(cid, 'typing')
                    time.sleep(1)
                    markup = InlineKeyboardMarkup(row_width=2)
                    markup.row(
                        InlineKeyboardButton(text='حذف', callback_data='delfile'),
                        InlineKeyboardButton(text='تبدیل ', callback_data='cvtopdf')
                    )
                    bot.send_message(cid, 'فایلتو گرفتم !', reply_markup=markup)
        if activity.type == 'pdfto*':
            if ext != 'pdf':
                bot.send_message(cid, 'فایلی که فرستادی pdf نیست :)')
            else:
                save = activity.add(name=name)
                resp = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(bot_token, file_info.file_path))
                if resp.ok:
                    with open(save, 'wb') as f:
                        f.write(resp.content)
                    bot.send_chat_action(cid, 'typing')
                    time.sleep(1)
                    markup = InlineKeyboardMarkup(row_width=2)
                    markup.row(
                        InlineKeyboardButton(text='حذف', callback_data='delfile'),
                        InlineKeyboardButton(text='تبدیل ', callback_data='cvfrompdf')
                    )
                    bot.send_message(cid, 'فایلتو گرفتم !', reply_markup=markup)
        if activity.type == 'mergepdfs':
            if ext != 'pdf':
                bot.send_message(cid, 'فایلی که فرستادی pdf نیست :)')
            else:
                save = activity.add(name=name)
                resp = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(bot_token, file_info.file_path))
                time.sleep(2)
                if resp.ok:
                    with open(save, 'wb') as f:
                        f.write(resp.content)
                        bot.send_chat_action(cid, 'typing')
                        time.sleep(1)
                        markup = InlineKeyboardMarkup(row_width=2)
                        markup.row(
                            InlineKeyboardButton(text='حذف', callback_data='delfile'),
                            InlineKeyboardButton(text='اضافه', callback_data='addfile'),
                            InlineKeyboardButton(text='یکی کردن', callback_data='mergepdf')
                        )
                    



def delfile(cid):
    activity.remove()
    bot.send_message(cid, 'فایلت حذف شد')

def addfile(cid):
    log = '\n'.join(activity.queue)
    bot.send_message(cid, f'فعلا اینا رو فرستادی: {log} \n\t\t تعداد فایلها: {len(activity.input)}')
    bot.send_message(cid, 'فایل بعدی رو بفرست ...')

def cvtopdf(cid):
    src_exts = ['docx', 'doc', 'jpg']
    ext = activity.current.split('.')[1]
    if ext not in src_exts:
        bot.send_message(cid, f'فرمت {ext} رو فعلا نمی تونم کاری کنم براش واسه همین حذفش کردم :)')
        activity.remove()
    else:
        markup = ReplyKeyboardMarkup(row_width=2)
        markup.add(
            KeyboardButton('پی دی اف اش کن'),
            KeyboardButton('مرحله قبلی')
        )
        bot.send_message(cid, 'اینجا رو چیکار کنم ؟ :)', reply_markup=markup)


def cvfrompdf(cid):
        markup = ReplyKeyboardMarkup(row_width=2)
        markup.add(
            KeyboardButton('ورد اش کن'),
            KeyboardButton('عکس اش کن'),
            KeyboardButton('مرحله قبلی')
        )
        bot.send_message(cid, 'اینجا رو چیکار کنم ؟ :)', reply_markup=markup)

def mergepdf(cid):
    if len(activity.input) < 2:
        bot.send_message(cid, 'فایل هات واسه یکی کردن یه دونه بیشتر نی بیکاری :)')
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(text='اضافه', callback_data='addfile')
        )
        bot.send_message(cid, 'یه فایل دیگه باید اضافه کنی', reply_markup = markup)
    else:
        merged = merge_pdfs_func(activity.input)
        doc = open(merged)
        bot.send_chat_action(cid, 'upload_document')
        time.sleep(2)
        bot.send_document(cid, doc)

callback_funcs = {
    'delfile': delfile,
    'addfile': addfile,
    'cvtopdf': cvtopdf,
    'cvfrompdf': cvfrompdf,
    'mergepdf': mergepdf
}


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data:
        func = callback_funcs.get(call.data)
        cid = call.message.chat.id
        return func(cid)




bot.polling()
