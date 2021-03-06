import logging
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import os  
from os import path
import time
from classes import Activity, ImageToPdf, PdfToImage, WordToPdf, merge_pdfs_func
import requests


from uuid import uuid4

load_dotenv()

ac = Activity()

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot_token = os.getenv('bot_token')
bot = telebot.TeleBot(token=bot_token, parse_mode=None)



def bot_markup_step(step: int):
    markup = ReplyKeyboardMarkup(row_width=2)
    if step == 1:    
        markup.add(
            KeyboardButton('کار جدید'),
        )
        markup.add(
            KeyboardButton('راهنمایی'),
        )
    if step > 1:
        markup.row(
            KeyboardButton('پی دی اف به بقیه'),
            KeyboardButton('بقیه به پی دی اف'),
        )
        markup.row(
            KeyboardButton('لیست فایلها'),
            KeyboardButton('یکی کردن پی دی اف ها'),
        )
        markup.row(
            KeyboardButton('مرحله قبلی')
        )
    return markup

@bot.message_handler(commands=['start'])
def start(msg):
    if ac:
        ac.reset(mode='hard')
    cid = msg.chat.id
    user = msg.chat.username
    ac.init(id=user)
    markup = bot_markup_step(step=ac.step)
    bot.send_message(cid, f'سلام {user}', reply_markup=markup )

@bot.message_handler(func= lambda msg: msg.text == 'کار جدید')
def new_job(msg):
    if ac:
        ac.reset(mode='soft')
    user = msg.chat.username
    cid = msg.chat.id
    if not ac.root:
        ac.init(id=user)
    ac.step += 1
    markup = bot_markup_step(step=ac.step)
    bot.send_message(cid, 'میخوای چیکار کنی ؟ :)', reply_markup= markup)


@bot.message_handler(func= lambda msg: msg.text == 'پی دی اف به بقیه')
def from_pdf(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not ac.root:
        ac.init(id=user)
    ac.type = 'pdfto*'
    bot.send_message(cid, 'فایلتو برام بفرست ... ')
    
@bot.message_handler(func= lambda msg: msg.text == 'بقیه به پی دی اف')
def to_pdf(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not ac.root:
        ac.init(id=user)
    ac.type = '*topdf'
    bot.send_message(cid, 'فایلتو برام بفرست ... ')

@bot.message_handler(func= lambda msg: msg.text == 'یکی کردن پی دی اف ها')
def merge_pdfs(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not ac.root:
        ac.init(id=user)
    ac.type = 'mergepdfs'
    ac.step += 1
    bot.send_message(cid, 'فایل هاتو برام بفرست ... ')

@bot.message_handler(func= lambda msg: msg.text == 'لیست فایلها')
def list_files(msg):
    user = msg.chat.username
    cid = msg.chat.id
    if not ac.root:
        ac.init(id=user)
    log = '\n'.join(ac.log())
    bot.send_message(cid, f'فایلهایی که واسم فرستادی : \n {log} \n\t\t تعداد فایلها : {len(ac.log())}')
    

@bot.message_handler(func= lambda msg: msg.text == 'مرحله قبلی')
def prev_step(msg):
    cid = msg.chat.id
    markup = bot_markup_step(step=ac.step - 1)
    if ac.step <= 0:
        markup = bot_markup_step(step=1)
    ac.step -= 1
    bot.send_message(cid, f'مرحله {ac.step}', reply_markup=markup )

@bot.message_handler(func = lambda msg: msg.text == 'پی دی اف اش کن')
def make_it_pdf(msg):
    cid = msg.chat.id
    files = ac.log()
    exts = [f.split('.')[1] for f in files]
    imageExts = ['jpg', 'jpeg', 'png']
    docExts = ['doc', 'docx']
    ext = exts[0] 
    cond = len(exts) > 1 and any(e != ext for e in exts) and ext in imageExts
    if cond : 
        bot.send_message(cid, 'فرمت عکسهایی که میخوای تبدیل کنی یکی نیست :)')
    else:
        converted = ''
        f = path.join(ac.root, ac.current)
        if ext in imageExts:
            itp = ImageToPdf()
            converted = itp.convert(f) if len(exts) == 1 else itp.convert(f, no= len(exts))
        if ext in docExts:
            wtp = WordToPdf()
            converted = wtp.convert(f)
        doc = open(converted, 'rb')
        bot.send_chat_action(cid, 'upload_document')
        time.sleep(2)
        bot.send_document(cid, doc)

@bot.message_handler(func = lambda msg: msg.text == 'عکس اش کن')
def make_it_image(msg):
    cid = msg.chat.id
    f = path.join(ac.root, ac.current)
    pti = PdfToImage()
    images = pti.convert(f)
    images = images.split('-')
    if images:
        bot.send_chat_action(cid, 'upload_document')
        time.sleep(2)
        for img in images:
            doc = open(img, 'rb')
            bot.send_document(cid, doc)

    
    

@bot.message_handler(content_types=['document', 'photo'])
def file_handler(msg):
    cid = msg.chat.id
    if not any(ac.type):
        bot.send_message(cid, 'لطفا برای استفاده از بات از /start شروع نمایید')
    fileObj = msg.document or msg.photo[-1]
    file_info = bot.get_file(fileObj.file_id)
    if file_info:
        name = str(uuid4()).split('-')[0] + '.jpeg'
        ext = 'jpeg'
        if msg.document:
            name = fileObj.file_name
            ext = fileObj.file_name.split('.')[1]
        if ext not in ac.known:
            bot.send_message(cid, 'فایلی که فرستادی به درد من نمیخوره :)')
        if ac.type == '*topdf':
            if ext == 'pdf':
                bot.send_message(cid, 'فایلی که فرستادی خودش pdf :)')
            else:
                save = ac.add(name=name)
                resp = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(bot_token, file_info.file_path))
                if resp.ok:
                    with open(save, 'wb') as f:
                        f.write(resp.content)
                    bot.send_chat_action(cid, 'typing')
                    time.sleep(2)
                    markup = InlineKeyboardMarkup(row_width=2)
                    if ext == 'jpg' or ext == 'jpeg':
                        markup.row(
                                InlineKeyboardButton(text='حذف', callback_data='delfile'),
                                InlineKeyboardButton(text='اضافه', callback_data='addfile'),
                                InlineKeyboardButton(text='تبدیل ', callback_data='cvtopdf')
                        )
                    else:
                        markup.row(
                            InlineKeyboardButton(text='حذف', callback_data='delfile'),
                            InlineKeyboardButton(text='تبدیل ', callback_data='cvtopdf')
                        )
                    bot.send_message(cid, 'فایلتو گرفتم !', reply_markup=markup)
        if ac.type == 'pdfto*':
            if ext != 'pdf':
                bot.send_message(cid, 'فایلی که فرستادی pdf نیست :)')
            else:
                save = ac.add(name=name)
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
        if ac.type == 'mergepdfs':
            if ext != 'pdf':
                bot.send_message(cid, 'فایلی که فرستادی pdf نیست :)')
            else:
                save = ac.add(name=name)
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
                        bot.send_message(cid, 'فایلتو گرفتم !', reply_markup=markup)
                    



def delfile(cid):
    ac.remove()
    bot.send_message(cid, 'فایلت حذف شد')

def addfile(cid):
    log = '\n'.join(ac.log())
    bot.send_message(cid, f'فعلا اینا رو فرستادی : \n {log} \n\t تعداد فایلها: {len(ac.log())}')
    bot.send_message(cid, 'فایل بعدی رو بفرست ...')

def cvtopdf(cid):
    src_exts = ['docx', 'doc', 'jpg', 'jpeg']
    ext = ac.current.split('.')[1]
    if ext not in src_exts:
        bot.send_message(cid, f'فرمت {ext} رو فعلا نمی تونم کاری کنم براش واسه همین حذفش کردم :)')
        ac.remove()
    else:
        markup = ReplyKeyboardMarkup(row_width=2)
        markup.add(
            KeyboardButton('پی دی اف اش کن'),
        )
        markup.add(
            KeyboardButton('مرحله قبلی')
        )
        bot.send_message(cid, 'اینجا رو چیکار کنم ؟ :)', reply_markup=markup)
        ac.step += 1

def cvfrompdf(cid):
        markup = ReplyKeyboardMarkup(row_width=2)
        markup.add(
            KeyboardButton('ورد اش کن'),
            KeyboardButton('عکس اش کن'),
            KeyboardButton('مرحله قبلی')
        )
        bot.send_message(cid, 'اینجا رو چیکار کنم ؟ :)', reply_markup=markup)
        ac.step += 1

def mergepdf(cid):
    if len(ac.queue) < 2:
        bot.send_message(cid, 'فایل هات واسه یکی کردن یه دونه بیشتر نی بیکاری :)')
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(text='اضافه', callback_data='addfile')
        )
        bot.send_message(cid, 'یه فایل دیگه باید اضافه کنی', reply_markup = markup)
    else:
        qf = [path.join(ac.root, q) for q in ac.queue ]
        merged = merge_pdfs_func(qf)
        doc = open(merged, 'rb')
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
