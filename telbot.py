import telebot
import re
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, KeyboardButton
import jdatetime
import pandas as pd
import os
import time
from datetime import datetime, timedelta
from database import get_name, show_info, change
import Bot_modes
from chos_mode import handle_quarrel, check_quarrels, handle_chosing
import instaloader
import random
import string
import base64
import sqlite3
from Currency import send_currency_to_Bot, wich_currency
from base_instagramdown import download_and_send_reel
from yt_dlp import YoutubeDL
from datetime import datetime
from zoneinfo import ZoneInfo
from telebot.types import InputMediaPhoto

IdAli = 8021347462
Tori_id = 7830801486
ThekidascryptID = -1002876585043

hiddenDB = 'hiddenDB.db'

create_table_query = '''
    CREATE TABLE IF NOT EXISTS users(
    UserID INTEGER PRIMARY KEY,
    Name TEXT,
    RandomKey TEXT,
    channel_id TEXT
    )
'''
with sqlite3.connect(hiddenDB) as connection:
    cursor = connection.cursor()
    cursor.execute(create_table_query)

def load_db():
    with sqlite3.connect(hiddenDB) as conn:
        return pd.read_sql_query("SELECT UserID, Name, RandomKey, channel_id FROM users", conn)




def generate_random_key(length=8):
    """یک رندوم کی به طول مشخص می‌سازد"""
    chars = string.ascii_letters + string.digits  # حروف و اعداد
    key = ''.join(random.choices(chars, k=length))
    return key

def encode_user_id(user_id):
    return base64.urlsafe_b64encode(str(user_id).encode()).decode()

def decode_user_id(encoded: str):
    return int(base64.urlsafe_b64decode(encoded.encode()).decode())

def safe_filename(name):
    if not name:
        return "Unknown_Group"

    # حذف کاراکترهای غیرمجاز
    name = re.sub(r'[\\/*?:"<>|[\]]', "", str(name))
    # جایگزینی فاصله‌ها با آندرلاین
    name = re.sub(r'\s+', "_", name.strip())
    # محدود کردن طول
    return name[:50]


def iran_time():
    now = datetime.now(ZoneInfo('Asia/Tehran'))
    timetext = now.strftime("%H:%M:%S")
    return timetext


# تابع برای تشخیص نوع پیام ناشناس
def send_any_message(to_chat_id, message, caption='', reply_markup=None, time='', sender=None):
    """ارسال هر نوع پیام (متن، عکس، گیف، ویدیو) به یک چت"""
    try:

        if message.text:
            Bot.send_message(to_chat_id,
            f'''{caption}\n\n━━━━━━━━━━━━━━\n{message.text}\n━━━━━━━━━━━━━━\n{time}''',
             reply_markup=reply_markup)

        elif message.photo:
            Bot.send_photo(to_chat_id, message.photo[-1].file_id, caption=caption, reply_markup=reply_markup)
        elif message.animation:
            Bot.send_animation(to_chat_id, message.animation.file_id, caption=caption, reply_markup=reply_markup)
        elif message.video:
            Bot.send_video(to_chat_id, message.video.file_id, caption=caption, reply_markup=reply_markup)
        elif message.audio:
            Bot.send_audio(to_chat_id, message.audio.file_id, caption=caption, reply_markup=reply_markup)
        elif message.sticker:
            Bot.send_message(to_chat_id, caption)
            Bot.send_sticker(to_chat_id, message.sticker.file_id, reply_markup=reply_markup)
        elif message.voice:
            Bot.send_voice(to_chat_id, message.voice.file_id, caption=caption, reply_markup=reply_markup)
        else:
            Bot.send_message(to_chat_id, "پیام از نوع پشتیبانی نشده", reply_markup=reply_markup)
            Bot.send_message(sender, 'بات از این نوع پیام پشتیبانی نمیکنه!')
    except Exception as e:
        print(f"Error in send_any_message: {e}")


def save_db(df):
    with sqlite3.connect(hiddenDB) as conn:
        cursor = conn.cursor()

        # پاک‌سازی جدول (نه فایل)
        cursor.execute("DELETE FROM users")

        # تبدیل NaN به None برای sqlite
        clean_df = df[['UserID', 'Name', 'RandomKey', 'channel_id']].where(pd.notnull(df), None)

        values = clean_df.values.tolist()

        cursor.executemany(
            "INSERT INTO users (UserID, Name, RandomKey, channel_id) VALUES (?, ?, ?, ?)",
            values
        )

        conn.commit()


def is_chat_private(message):
    if message.chat.type in ['private']:
        return True
    else:
        return False

# فقط اگر علی بود، عمل انجام بشه
def Only_if_is_Ali(func):
    def infs(message):
        if not message.from_user.id == IdAli:
            return
        return func(message)
    return infs


def wrong (message, e, line = None):
    try:
        Bot.reply_to(message, f'EROR: Something went wrong ❌!\n{e}')
        Bot.send_message(IdAli, f'An Eror happend in message {message.chat.id}: {e}\nline {line}')
    except Exception as err:
        Bot.send_message(IdAli, f'خطا در ارسال گزارش:\n {err}\nline: {line}')



'''def make_progress_hook(chat_id, msg_id):
    def progress_hook(d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded_bytes = d.get('downloaded_bytes', 0)
            if total_bytes:
                percent = downloaded_bytes / total_bytes * 100
                try:
                    Bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=msg_id,
                        text=f"دانلود: {percent:.1f}%"
                    )
                except Exception as e:
                    print("Progress update failed:", e)
    return progress_hook
'''



Guide = '''من میتونم: \n
1.تاریخ رو بهت بگم (تاریخ)\n
2.پیامت رو توی گپ پین کنم (پین)\n
3.هرکی گفتیو میوت کنم (میوتش کن)\n
4.هرکی گفتیو آنمیوت کنم (آنمیوت)\n
5.پیام هارو برات پاک کنم (پاکش کن)\n
6.تاس بریزم (تاس)\n
7.هرچی گفتیو تکرار کنم. روی پیامم ریپلای کن و بنویس: بگو ...\n
8.به یه نفر دیگه، هرچی که گفتیو از طرف خودم بگم. \n
روی پیامش ریپلای کن و دستور بده: الویر بگو ...\n
9.دستور (لینک ناشناس من)\n
10.قرعه کشی: کیا گاون؟\n
الویر بصورت رندوم دو نفر از اعضای گپ رو انتخاب میکنه \n
11.چس مود \n
اگه میخوای عمل روی شخص خاصی انجام بشه، روش ریپلای بزن و دستور بده 🫶'''


chos = '''با این قابلیت، میتونی اجازه ریپلای زدن کاربرها روی پیام های خودت رو ازشون بگیری.\n
میتونی بگی: من با [اسمش] چسم 🦦 \n 
اینجوری من تمام پیام هایی که از سمت اون شخص روی تو ریپلای میشن رو پاک میکنم\n
(حتما باید همون اسمی رو بگی که روی بات ازش سیو شده) \n
برای برگردوندنش به حالت عادی هم کافیه روی پیامش ریپلای کنی و بنویسی: آشتی'''


private_channel = '''
باید بات رو توی چنلت ادمین کنی، و بعد یکی از پیام های پنل رو برای بات ارسال کنی:
'''

#Date
today = jdatetime.date.today()

# ساخت دیتابیس درصورت عدم وجود 
File_name = 'Users.db'

create_table_query = '''
    CREATE TABLE IF NOT EXISTS users(
        Name text,
        ID integer primary key
    )
'''
with sqlite3.connect(File_name) as connection:
    cursor = connection.cursor()
    cursor.execute(create_table_query)


Bot = telebot.TeleBot('8222922601:AAFNMcO-J2z72CLf44ANYYpv91YIYGPNN7g')
Bot_id = Bot.get_me().id

def reply_to_bot_only(func):
    def wrapper(message):
        if not message.reply_to_message or not message.reply_to_message.from_user.is_bot:
            return
        return func(message)
    return wrapper


keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
Button = KeyboardButton(text='ناشناس به تری')
Button2 = KeyboardButton(text='ناشناس به علی')
Button3 = KeyboardButton(text='لینک ناشناس من')
keyboard.add(Button, Button2, Button3)


keyboardG = InlineKeyboardMarkup(row_width=1)
bttn1 = InlineKeyboardButton('چس مود چیه؟', callback_data= 'chos mode')
keyboardG.add(bttn1)

keyboardchanel = InlineKeyboardMarkup(row_width=1)
ButtonC = InlineKeyboardButton('ناشناس مستقیم به علی', callback_data= 'Private')
ButtonC2 = InlineKeyboardButton('بره تو چنل', callback_data= 'Public')
keyboardchanel.add(ButtonC, ButtonC2)


downkeyboard = InlineKeyboardMarkup(row_width=1)
Dbttn1 = InlineKeyboardButton('Instagram', callback_data='mp4')
Dbttn2 = InlineKeyboardButton('Soundcloud', callback_data='mp3')
downkeyboard.add(Dbttn1)


premessionKeyboard = InlineKeyboardMarkup(row_width=1)
Pbttn1 = InlineKeyboardButton('ارسال به چنل', callback_data='send')
premessionKeyboard.add(Pbttn1)




channeltypekeyboard = InlineKeyboardMarkup(row_width=1)
CHbttn1 = InlineKeyboardButton('Private', callback_data='private')
CHbttn2 = InlineKeyboardButton('Public', callback_data='public')
channeltypekeyboard.add(CHbttn1, CHbttn2)


addchannelkeyboard = InlineKeyboardMarkup(row_width=1)
addbttn1 = InlineKeyboardButton('اضافه کردن چنل', callback_data='add channel')
addbttn2 = InlineKeyboardButton('ساخت لینک جدید', callback_data='new')
addchannelkeyboard.add(addbttn1, addbttn2)


new_linkKeyboard = InlineKeyboardMarkup(row_width=1)
NLbttn1 = InlineKeyboardButton('ساخت لینک ناشناس', callback_data='new')
new_linkKeyboard.add(NLbttn1)


# lattary
@Bot.message_handler(regexp=r'^کیا\s*(.+)$')
def Arpeat(message):
    match = re.match(r'^کیا\s*(.+)$', message.text)
    if match:
        txt = match.group(1).strip()

    if txt.endswith("؟") or txt.endswith("?"):
        txt = txt[:-1].strip()


    chat = message.chat.title
    GF_name = f'{safe_filename(chat)}.db'
    # اتصال به دیتابیس
    with sqlite3.connect(GF_name) as conn:
        cursor = conn.cursor()

        # گرفتن تمام اسم‌ها
        cursor.execute("SELECT Name FROM users")
        names = [row[0] for row in cursor.fetchall()]

    if len(names) < 2:
        Bot.reply_to(message, 'تعداد اعضا کمتر از دو نفرن دلقک')
        return

    # انتخاب رندوم دو نفر
    selected = random.sample(names, 2)

    Badbakht1, Badbakht2 = selected
    Bot.reply_to(message, f'{Badbakht1} و {Badbakht2} {txt} 🙂')

# lattary 2
@Bot.message_handler(regexp=r'^کی \s*(.+)$')
def Arpeat(message):
    match = re.match(r'^کی\s*(.+)$', message.text)
    if match:
        txt = match.group(1).strip()

    if txt.endswith("؟") or txt.endswith("?"):
        txt = txt[:-1].strip()

    
    chat = message.chat.title
    GF_name = f'{safe_filename(chat)}.db'

    # اتصال به دیتابیس
    with sqlite3.connect(GF_name) as conn:
        cursor = conn.cursor()

        # گرفتن تمام اسم‌ها
        cursor.execute("SELECT Name FROM users")
        names = [row[0] for row in cursor.fetchall()]

    if len(names) < 1:
        Bot.reply_to(message, 'هیچ عضوی توی لیست نیس')
        return

    Badbakht1 = random.sample(names, 1)
    Bot.reply_to(message, f'{Badbakht1} {txt} 🙂')

# Filter
Bot_modes.register_handlers(Bot)


# start
@Bot.message_handler(commands=['start'])
def welcome(messege):
    args = messege.text.split()
    if len(args) == 1:
        if is_chat_private(messege):
            Bot.send_message (messege.chat.id, 'سلام زیبارو', reply_markup=keyboard)
            return
        else:
            Bot.send_message (messege.chat.id, 'سلام زیبارو')

    else:
        if is_chat_private(messege):
            try:
                payload = args[1]
                random_key, encoded_userid = payload.split('_')

                with sqlite3.connect(hiddenDB) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT Name FROM users WHERE RandomKey = ?", (random_key,))
                    result = cursor.fetchone()
                    name = result[0]

                owner_id = decode_user_id(encoded_userid)
                Bot.reply_to(messege, f'درحال ارسال ناشناس به {name} هستی 🦦\n ')
                Bot.register_next_step_handler(messege, forward_hidden, owner_id)

            except Exception as e:
                Bot.send_message(messege.chat.id, 'یه مشکل پیش اومده') 
                Bot.send_message(IdAli, e)
        else:
            Bot.reply_to(messege, 'امکان ارسال ناشناس فقط توی شخصی بات فعاله!')

# ارسال به صاحب لینک
def forward_hidden(message, owner_id):

    df = load_db()
    row = df[df['UserID'] == owner_id]

    if row.empty:
        return Bot.send_message(owner_id, "لینکت مشکل داره ❌")
    idx = row.index[0]

    channelID = df.loc[idx, 'channel_id']

    callback = str(message.chat.id)
    kb = InlineKeyboardMarkup(row_width=1)
    Hbttn1 = InlineKeyboardButton('پاسخ', callback_data=f'R_{callback}')
    Pbttn1 = InlineKeyboardButton('ارسال به چنل', callback_data=str(f'channel_{owner_id}'))
    kb.add(Hbttn1)

    if pd.notna(channelID):
        kb.add(Pbttn1)
    send_any_message(owner_id, message, caption='📩 پیام ناشناس دریافت شد', reply_markup=kb, time=f'🕛: {iran_time()}', sender=message.from_user.id)
    Bot.reply_to(message, 'ارسال شد ✅')
    
@Bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('R_'))
def reply(call):
    target_id = int(call.data.split("_")[1])
    msg = Bot.send_message(call.from_user.id, 'پاسخت رو بزار. براش ارسال میکنم 👇')
    Bot.register_next_step_handler(msg, ans, target_id)

def ans(message, target_id):
    name = message.from_user.first_name

    callback = str(message.chat.id)
    kbanser_to_answer = InlineKeyboardMarkup(row_width=1)
    Hbttn1 = InlineKeyboardButton('پاسخ', callback_data=f'an_{callback}')
    kbanser_to_answer.add(Hbttn1)
    send_any_message(target_id, message, caption=f'{name} به پیامت پاسخ داد 📩', reply_markup=kbanser_to_answer, time=f'🕛: {iran_time()}', sender=message.from_user.id)

    Bot.reply_to(message, 'پاسخت ارسال شد 🤍')


# ارسال به چنل شخصی
@Bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('channel_'))
def send_channel(call):

    owner = int(call.data.split("_")[1])

    df = load_db()
    idx = df.index[df['UserID'] == owner][0]
    channelID = df.loc[idx, 'channel_id']
    if call.message.text:
        Bot.send_message(channelID, call.message.text)
    else:
        send_any_message(channelID, call.message, caption='📩 پیام ناشناس دریافت شد')
    Bot.reply_to(call.message, 'رفت تو چنلت')



# ساخت ناشناس
@Bot.message_handler(func=lambda message: message.text == 'لینک ناشناس من')
def cheklink(message):

    userid = message.from_user.id
    df = load_db()

    if userid in df['UserID'].values:
        row = df[df['UserID'] == userid].iloc[0]

        random_key = row['RandomKey']
        encoded = encode_user_id(userid)
        link = f"https://t.me/ThekidAsbot?start={random_key}_{encoded}"

        Bot.reply_to(message, f'لینکت:\n{link}', reply_markup=addchannelkeyboard)
    else:
        Bot.reply_to(message, 'هنوز لینک نداری. برای ساختن لینک کلیک کن 👇', reply_markup=new_linkKeyboard)
        


@Bot.callback_query_handler(func=lambda call: call.data == 'new')
def create_link(call):
    userid = call.from_user.id
    channel_username = None

    rendom_key = generate_random_key()
    encoded_userid = encode_user_id(userid)
    User_name = call.from_user.first_name

    # خواندن دیتابیس
    df = load_db()
    print(df.columns)

    if userid not in df['UserID'].values:
        # کاربر جدید
        link = f"https://t.me/ThekidAsbot?start={rendom_key}_{encoded_userid}"

        new_row = pd.DataFrame([[userid, User_name, rendom_key, channel_username]], columns=['UserID','Name', 'RandomKey', 'channel_id'])
        df = pd.concat([df, new_row], ignore_index=True)
        Bot.reply_to(call.message, f'لینکت آماده شد: \n\n{link}', reply_markup=addchannelkeyboard)
    else:
        # کاربر قبلاً ثبت شده
        idx = df.index[df['UserID'] == userid][0]
        df.loc[idx, 'RandomKey'] = rendom_key
        df.loc[idx, 'channel_id'] = channel_username
        link = f"https://t.me/ThekidAsbot?start={rendom_key}_{encoded_userid}"
        Bot.reply_to(call.message, f'لینکت آماده شد: \n\n{link}', reply_markup=addchannelkeyboard)


    # ذخیره دیتابیس
    print(df.columns)
    save_db(df)
    df = load_db()
    print(df.columns)
    

    

@Bot.callback_query_handler(func=lambda call: call.data == 'add channel')
def add_channel(call):
    msg = Bot.reply_to(call.message, 'نوع چنلتو انتخاب کن', reply_markup = channeltypekeyboard)

@Bot.callback_query_handler(func=lambda call: call.data == 'public')
def public_channel(call):
    userid = call.from_user.id
    msg = Bot.send_message(call.message.chat.id, 'لینک چنلتو بده 🦦')
    Bot.register_next_step_handler(msg, save_channel, userid)

def save_channel(message, userid):
    df = load_db()
    df['channel_id'] = df['channel_id'].astype('string')


    channel = message.text
    match = re.search(r"(?:https?://)?t\.me/(@?\w+)", channel)
    if match:
        channel_username = match.group(1)  # خروجی: 'ThekidAscrypt' یا '@ThekidAscrypt'
        if not channel_username.startswith("@"):
            channel_username = "@" + channel_username
    idx = df.index[df['UserID'] == userid][0]
    df.loc[idx, 'channel_id'] = channel_username
    save_db(df)
    Bot.send_message(message.chat.id, 'چنلت ثبت شد 💟\nاز الان میتونم ناشناس هاتو از طرف خودم به چنلت ارسال کنم.')



@Bot.callback_query_handler(func=lambda call: call.data == 'private')
def private_channel(call):
    userid = call.from_user.id
    msg = Bot.send_message(call.message.chat.id, 'باید اول الویر رو تو چنلت ادمین کنی، بعد یکی از پیام های چنلتو براش فوروارد کنی تا بشناستش\nمنتظر پیام فوروارد شده ام 😶‍🌫️')
    Bot.register_next_step_handler(msg, whats_channelid, userid)

def whats_channelid(message, userid):

    df = load_db()
    if message.forward_from or message.forward_from_chat:
        channel_username = message.forward_from_chat.id
        idx = df.index[df['UserID'] == userid][0]
        df.loc[idx, 'channel_id'] = channel_username
        save_db(df)
        Bot.reply_to(message, 'آیدی چنلت ثبت شد 🙂‍↔️')
    else:
        Bot.send_message(userid, 'این پیام فوروارد نیست!')



# ناشناس علیو تری
def nashenas(message, Bot, send_to):
    try:
        msg = Bot.send_message(
            message.chat.id,
            'پیامتو بزار 🦦 قول میدم نگم از طرف توعه'
        )
        Bot.register_next_step_handler(msg, send_text_to_ali_or_tori, send_to)
    except Exception as e:
        wrong(message, e, line='389')

@Bot.message_handler(func=lambda m: m.text and m.text.startswith('ناشناس به'))
def choose(message):
    if is_chat_private(message):
        if message.text == 'ناشناس به علی':
            send_to = IdAli
            nashenas(message, Bot, send_to)
        elif message.text == 'ناشناس به تری':
            send_to = Tori_id
            nashenas(message, Bot, send_to)
        else:
            pass
    else:
        Bot.reply_to(message, 'امکان ارسال ناشناس فقط توی شخصی بات فعاله!')


def send_text_to_ali_or_tori(message, send_to):

    callback = str(message.chat.id)
    kb = InlineKeyboardMarkup(row_width=1)
    Hbttn1 = InlineKeyboardButton('پاسخ', callback_data=f'rep_{callback}_{send_to}')
    Pbttn1 = InlineKeyboardButton('ارسال به چنل', callback_data='send')
    kb.add(Pbttn1)
    kb.add(Hbttn1)

    try:
        send_any_message(send_to, message, caption='📩 پیام ناشناس دریافت شد', reply_markup=kb, time=f'🕛: {iran_time()}', sender=message.from_user.id)
        Bot.reply_to(message, 'پیامت ارسال شد 🤍')

    except Exception as e:
        wrong(message, e, line='406')

@Bot.callback_query_handler(func=lambda call: call.data == 'send')
def send_to_channel(call):
    try:
        if call.message.text:
            Bot.send_message(ThekidascryptID, call.message.text)
        else:
            send_any_message(ThekidascryptID, call.message, caption='📩 پیام ناشناس دریافت شد')
        Bot.reply_to(call.message, 'رفت تو چنل 🙂‍↔️')
    except Exception as e:
        wrong(call.message, e, line='567')

@Bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('rep_'))
def answer(call):
    target_id = int(call.data.split("_")[1])
    responder = int(call.data.split("_")[2])
    if responder == IdAli:
        responder = 'علی'
    else:
        responder = 'تری'
    msg = Bot.send_message(call.from_user.id, 'پاسخت رو بزار. براش ارسال میکنم 👇')
    Bot.register_next_step_handler(msg, send_reaction, target_id, responder)

def send_reaction(message, target_id, responder):
    send_any_message(target_id, message, caption=f'{responder} به پیامت پاسخ داد 📩', time=f'🕛: {iran_time()}', sender=message.from_user.id)
    Bot.reply_to(message, 'پاسخت ارسال شد 🤍')



help = ''
@Bot.message_handler(commands=['help'])
def helo(message):
    global help
    help = Bot.reply_to(message, Guide, reply_markup=keyboardG)

@Bot.callback_query_handler(func=lambda call: call.data == 'chos mode')
def call_handler(call):
    global help
    keyboard = InlineKeyboardMarkup(row_width=1)
    bttn1 = InlineKeyboardButton('برگشت', callback_data= 'back')
    keyboard.add(bttn1)
    Bot.edit_message_text(text=chos, chat_id=call.message.chat.id, message_id=help.message_id, reply_markup=keyboard)

@Bot.callback_query_handler(func=lambda call: call.data == 'back')
def edit_to_last(call):
    global help
    Bot.edit_message_text(Guide, call.message.chat.id, call.message.message_id, reply_markup=keyboardG)


@Bot.message_handler(commands=['currency'])
def currency(message):
    try:
        send_currency_to_Bot(Bot, message)
    except Exception as e:
        wrong(message, e)


@Bot.message_handler(regexp=r'^قیمت\s*(.+)$')
def find_price(message):
    match = re.match(r'^قیمت\s*(.+)$', message.text)
    if match:
        txt = match.group(1).strip()
        if txt == 'تینا':
            Bot.reply_to(message, 'مفت نمی ارزه')
        else:

            loading_msgs = ["در حال استخراج قیمت.", "در حال استخراج قیمت..", "در حال استخراج قیمت..."]
            

            to_edit = Bot.reply_to(message, loading_msgs[2])

            for i in range(6):
                Bot.edit_message_text(
                    loading_msgs[i % 3],
                    chat_id=message.chat.id,
                    message_id=to_edit.message_id
                )
                time.sleep(0.3)
            wich_currency(Bot, message, Na=txt, to_edit=to_edit)
    else:
        Bot.reply_to(message, 'اسم ارز رو بعد از کلمه قیمت وارد کن تا قیمتشو بهت بگم 😶‍🌫️')


@Bot.message_handler(func=lambda m: m.text == 'دانلود')
def download(message):
    Bot.reply_to(message, 'انتخاب کن از کدوم پلتفرم میخوای دانلود کنی 😶‍🌫️', reply_markup=downkeyboard)

User_format = {}


@Bot.callback_query_handler(func=lambda call: call.data == 'mp4')
def vid(call):
    User_format[call.from_user.id] = 'mp4'
    msg = Bot.send_message(call.message.chat.id, 'لینک ریلزو بده')
    Bot.register_next_step_handler(msg, pindown)

def pindown(message):
    import requests

    def download_stream(url):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        return response.content
    direct_url = download_stream(message.text)
    Bot.send_video(direct_url)


'''@Bot.message_handler(regexp='https://')
def downins(message):
    try:
        l = instaloader.Instaloader()
        l.login('thekiid.aa', 'Atashinsadafali@90')

        URL = message.text
        match = re.search(r'/([A-Za-z0-9_-]{5,})/', URL)
        shortcode = match.group(1)


        l.download_post(
            instaloader.Post.from_shortcode(
                l.context,
                shortcode
            ), target='tempdown'
        )
    except Exception as e:
        wrong (message, e, line='474')'''




@Bot.message_handler(regexp='^(تری)$')
def tori(message):
    Bot.reply_to(message, 'فرمایش؟')


@Bot.message_handler(func=lambda message: message.text == 'آلویر')
def j(message):
    if message.reply_to_message:
        if message.reply_to_message.from_user.is_bot:
            Bot.reply_to(message, 'بنال')
        else:
            pass
    if message.from_user.id == (Tori_id):
        Bot.reply_to(message, 'جانم 🥹')
    else:
        Bot.reply_to(message, 'بنال')

@Bot.message_handler(func=lambda message: message.text == 'الویر')
def j(message):
    if is_chat_private(message):
        if message.reply_to_message:
            if message.reply_to_message.from_user.is_bot:
                Bot.reply_to(message, 'جون', reply_markup=keyboard)
            else:
                pass
        if message.from_user.id == (Tori_id):
            Bot.reply_to(message, 'جانم 🥹', reply_markup=keyboard)
        else:
            Bot.reply_to(message, 'بنال', reply_markup=keyboard)

    else:
        if message.reply_to_message:
            if message.reply_to_message.from_user.is_bot:
                Bot.reply_to(message, 'جون')
            else:
                pass
        if message.from_user.id == (Tori_id):
            Bot.reply_to(message, 'جانم 🥹')
        else:
            Bot.reply_to(message, 'بنال')


@Bot.message_handler(func=lambda message: message.text == 'تاس')
def dice(message):
    Bot.send_dice(message.chat.id, emoji='🎲')

@Bot.message_handler(regexp=r'^(اسممو یادت باشه)$')
def db(message):
    Bot.reply_to(message, 'اسمتو بگو (ریپلای کن)🦦')
    Bot.register_next_step_handler(message, lambda m: get_name(Bot, m))


@Bot.message_handler(regexp=r'^ا+\s*س+\s*م+\s*م+\s*ی+\s*ا+\s*د+\s*ت+\s*ب+\s*ا+\s*ش+\s*ه+\s*$')
def db(message):
    
    Bot.reply_to(message, 'اسمتو بگو (ریپلای کن)🦦')

    if message.chat.type in ['group', 'supergroup']:
        group_name = safe_filename(message.chat.title)
        group_file = f"{group_name}.xlsx"
    else:
        group_file = None

    Bot.register_next_step_handler(
        message,
        lambda m: get_name(Bot, m, group_file)
    )


@Bot.message_handler(regexp=r'^ثبتش کن\s*(.+)$')
@Only_if_is_Ali
def change_name(message):
    try:
        match = re.match(r'^ثبتش کن\s*(.+)$', message.text)
        if match:
            txt = match.group(1).strip()
            change(Bot, message, name=txt)
        else:
            Bot.reply_to(message, 'چی ثبتش کنم؟')


    except Exception as e:
        wrong(message, e, line='549')


@Bot.message_handler(func=lambda m: m.text == 'آیدیم')
def extract_chat_id(message):
    try:
        user_id = message.from_user.id
        username = f'@{message.from_user.username}'
        is_premium = message.from_user.is_premium
        info = f'یوزر آیدی: {user_id}\nیوزرنیم: {username}\nوضعیت پریمیوم: {is_premium}'


        photos = Bot.get_user_profile_photos(message.from_user.id)
        media = []
        for photo_group in photos.photos:
            biggest = photo_group[0]
            media.append(InputMediaPhoto(biggest.file_id))

        # فقط اولین عکس می‌تونه کپشن داشته باشه
        if media:
            media[0].caption = info
            Bot.send_media_group(message.chat.id, media)
        else:
            Bot.send_message(message.chat.id, info)

    except Exception as e:
        wrong(message, e)


@Bot.message_handler(commands=['Chat'])
def chat_id(message):
    chatID = message.chat.id
    type = message.chat.type
    Bot.reply_to(message, f'chat ID:\n{chatID}\nchat type: {type}', parse_mode='Markdown')


@Bot.message_handler(commands=['inf'])
@Only_if_is_Ali
def info(message):
    show_info(Bot, message)



@Bot.message_handler(regexp=r'^بگو\s*(.+)$')
@reply_to_bot_only
def repeat(message):
    try:
        # اجرای regex روی متن
        match = re.match(r'^بگو\s*(.+)$', message.text)
        if match:
            txt = match.group(1).strip()  # فقط متن بعد از "بگو"
            Bot.reply_to(message, txt)
        else:
            Bot.reply_to(message, 'چی بگم؟ 😅')

    except Exception as e:
        wrong(message, e, line='574')


# Date
@Bot.message_handler(regexp='^(تاریخ)$')
def date(message):
    now = jdatetime.datetime.now()
    weekday_en = now.strftime("%A")  # روز هفته به انگلیسی
    days_fa = {
        'Saturday': 'شنبه',
        'Sunday': 'یک‌شنبه',
        'Monday': 'دوشنبه',
        'Tuesday': 'سه‌شنبه',
        'Wednesday': 'چهارشنبه',
        'Thursday': 'پنج‌شنبه',
        'Friday': 'جمعه'
    }

    weekday_fa = days_fa.get(weekday_en, weekday_en)
    formatted = now.strftime("%Y/%m/%d")
    try:
        Bot.reply_to(message, f'📅 تاریخ امروز: {formatted} - {weekday_fa}')
    except Exception as e:
        wrong(message, e, line='597')
        
# Time
@Bot.message_handler(func=lambda m: m.text == 'ساعت چنده')
def Time_now(message):
    Bot.reply_to(message, f'ساعت: {iran_time()}')


@Bot.message_handler(regexp='چاکس')
def ch(message):
    if message.from_user.id != IdAli:
      Bot.reply_to(message, 'نبینم لفظ علیو به کار ببری')
    else:
      pass




@Bot.message_handler(content_types=['voice'])
def sik(audio):
    Bot.reply_to(audio, 'صدا بچه نشنوم')

@Bot.message_handler(regexp='عشق منی')
def youto(lv):
    Bot.reply_to(lv, 'توعم عشق علی ای')


@Bot.message_handler(regexp=r'^ص+\s*ب+\s*ب+\s*خ+\s*ی+\s*ر+$')
def sabah(message):
    Bot.reply_to(message, "صبحت عسل 🍒")

@Bot.message_handler(regexp=r'^ش+\s*ب+\s*ب+\s*خ+\s*ی+\s*ر+\s*$')
def shab(message):
    Bot.reply_to(message, 'مسواک و جیش یادت نره 💜🙂')



waiting_for_name = {}  # دیکشنری جهانی برای نگهداری کاربرهایی که منتظر پاسخشونیم
@Bot.message_handler(regexp=r'^\s*س+\s*ل+\s*ا+\s*م+\s*$')
def reply_to_hello(message):

    target_user = message.from_user
    user_id = target_user.id

    with sqlite3.connect(File_name) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM users WHERE ID = ?", (user_id,))
        exists = cursor.fetchone() is not None
    if not exists:
        msg = Bot.reply_to(message, 'اسمت چیه 🦦؟')
        waiting_for_name[user_id] = True

    elif not message.reply_to_message:
        if is_chat_private(message):
            Bot.reply_to(message, "سلام زیبارو 😍", reply_markup=keyboard)
        else:
            Bot.reply_to(message, "سلام زیبارو 😍")

    elif message.reply_to_message.from_user.is_bot:
        if is_chat_private(message):
            Bot.reply_to(message, 'سلام عشقم 🥹', reply_markup=keyboard)
        else:
            Bot.reply_to(message, 'سلام عشقم 🥹')

    else:
        pass


@Bot.message_handler(func=lambda m: waiting_for_name.get(m.from_user.id))
def save_name(message):
    user_id = message.from_user.id
    name = message.text.strip()

    get_name(Bot, message)

    waiting_for_name.pop(user_id, None)



@Bot.message_handler(regexp=r'^Del\s*(.+)$')
def delete(message):
    if message.from_user.id == IdAli:
        match = re.match(r'^Del\s*(.+)$', message.text)
        if not match:
            Bot.reply_to(message, "چی رو حذف کنم؟ 😅")
            return

        txt = match.group(1).strip()

        if message.chat.type == 'private':
            with sqlite3.connect(File_name) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1 FROM users WHERE Name = ?", (txt,))
                exists = cursor.fetchone() is not None

            if exists:
                with sqlite3.connect("Users.db") as conn:
                    cursor = conn.cursor()
 
                    # حذف ردیف‌ها بر اساس شرط
                    cursor.execute("DELETE FROM users WHERE Name = ?", (txt,))

                Bot.reply_to(message, f"{txt} deleted (U)")
            else:
                Bot.reply_to(message, f"{txt} wasn't found in (USERS)")

        elif message.chat.type in ['group', 'supergroup']:
            chat = message.chat.title
            safe_name = safe_filename(chat)
            GF_name = f"{safe_name}.db"

            with sqlite3.connect(GF_name) as connection:
                cursor = connection.cursor()
                cursor.execute("SELECT 1 FROM users WHERE Name = ?", (txt,))
                exists = cursor.fetchone() is not None

            if exists:
                with sqlite3.connect(GF_name) as conn:
                    cursor = conn.cursor() 
                    # حذف ردیف‌ها بر اساس شرط
                    cursor.execute("DELETE FROM users WHERE Name = ?", (txt,))
            else:
                Bot.reply_to(message, f"{txt} wasn't found in (Group.Usrs)")
    else:
        pass




@Bot.message_handler(regexp=r'(?=.*میزونی)(?=.*\؟)')
@reply_to_bot_only
def thanks(message):
    Bot.reply_to(message, 'شکر')


@Bot.message_handler(regexp=r'(?=.*خوبی)(?=.*\؟)')
@reply_to_bot_only
def thanks(message):
    Bot.reply_to(message, 'شکر')


@Bot.message_handler(regexp=r'(?=.*حالت خوبه)(?=.*\؟)')
@reply_to_bot_only
def thanks(message):
    Bot.reply_to(message, 'شکر')


@Bot.message_handler(regexp=r'(?=.*ردیفی)(?=.*\؟)')
@reply_to_bot_only
def thanks(message):
    Bot.reply_to(message, 'شکر')


@Bot.message_handler(func=lambda message: message.text == 'اسمم چیه؟')
@reply_to_bot_only
def names(message):
    userid = message.from_user.id
    with sqlite3.connect(File_name) as connection:
        cursor = connection.cursor()

        # دریافت مقدار ستون Name برای این ID
        cursor.execute("SELECT Name FROM users WHERE ID = ?", (userid,))
        row = cursor.fetchone()

    if row:
        name = row[0] 
        Bot.reply_to(message, name)
    else:
        Bot.reply_to(message, 'بلد نیستم')

@Bot.message_handler(func=lambda message: message.text == 'اسمش چیه؟')
def who_is_that(message):
    if message.reply_to_message:
        userid = message.reply_to_message.from_user.id
        with sqlite3.connect(File_name) as connection:
            cursor = connection.cursor()

            # دریافت مقدار ستون Name برای این ID
            cursor.execute("SELECT Name FROM users WHERE ID = ?", (userid,))
            row = cursor.fetchone()

        if row:
            name = row[0] 
            Bot.reply_to(message, name)
        else:
            Bot.reply_to(message, 'بلد نیستم')
    else:
        Bot.reply_to(message, 'اگه میخوای بدونی هرکسیو با چه اسمی میشناسم، روش  ریپلای کن و اسمشو بپرس ')






#Group Only
fohsh  = 'کسکش عنتر گوت آشغال کونی بچ جیشو. زنگ بزنم مامانت بگم زیر کل ایران خوابیدی پولی؟ یا خودم پلمپ تونل وحشتتو باز کنم؟\n کونده کسپدر بسس کن ایدز گرفتی کونی مونی'
def is_user_admin(chat_id, user_id):
    admins = Bot.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.user.id == user_id:
            return True
    return False

# Change group info
@Bot.message_handler(func=lambda m: m.text == 'پروفایلو عوض کن')
def delete_profile(message):

    if is_user_admin(message.chat.id, message.from_user.id):
        msg = Bot.reply_to(message, 'عکس رو بفرست تا ستش کنم')
        Bot.register_next_step_handler(msg, change_profile)
    else:
        pass
def change_profile(message):
    if message.content_type != 'photo':
        Bot.reply_to(message, '⚠️ لطفا فقط یک عکس بفرست!')
        return

    # گرفتن فایل بزرگترین سایز عکس
    file_id = message.photo[-1].file_id
    file_info = Bot.get_file(file_id)
    downloaded_file = Bot.download_file(file_info.file_path)

    # ست کردن عکس جدید
    Bot.set_chat_photo(message.chat.id, downloaded_file)
    Bot.reply_to(message, 'پروفایل قبلی گپ پاعک')


# Tag
def escape_markdown(text):
    escape_chars = r'_*[]()~`>#+=|{}.!-'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))

@Bot.message_handler(func=lambda message: message.text == 'تگ')
def tag_all(message):
    chat = message.chat.title
    GF_name = f"{safe_filename(chat)}.db"

    row = []
    fetch_data_query = '''
    SELECT ID, Name FROM users
    '''
    with sqlite3.connect(GF_name) as connection:
        cursor = connection.cursor()
        cursor.execute(fetch_data_query)
        row = cursor.fetchall()

    dfg = pd.DataFrame(row, columns=['UserID', 'Name'])
    try:

        if dfg.empty:
            Bot.reply_to(message, "⚠️ هنوز هیچ کاربری ثبت نشده.")
            return

        text = "📢 تگ همه اعضا:\n\n"
        for i, row in dfg.iterrows():
            name = escape_markdown(row['Name'])
            user_id = str(row['UserID']).strip()

            tag = f"[{name}](tg://user?id={user_id})"
            text += f"{i+1}\\.\u0020{tag}\n"

        Bot.send_message(
            message.chat.id,
            text,
            parse_mode="MarkdownV2"
        )

    except Exception as e:
        Bot.reply_to(message, f"❌ خطا هنگام تگ کردن:\n{e}")



@Bot.message_handler(regexp=r'^الویر بگو\s*(.+)$')
def Arpeat(message):
    match = re.match(r'^الویر بگو\s*(.+)$', message.text)
    if match:
        txt = match.group(1).strip()
        if message.reply_to_message:
            try:
                Bot.reply_to(message.reply_to_message, txt)
                Bot.delete_message(message.chat.id, message.id)
            except Exception as e:
                wrong(message, e, line='844')



# Mute
@Bot.message_handler(func=lambda message: message.text == 'میوتش کن')
def mute_who(message):
    if message.reply_to_message:
        if message.reply_to_message.from_user.id == Bot_id:
            Bot.reply_to(message, 'میخوای خودتو میوت کنم دلقک؟')
            return
            
        if is_user_admin(message.chat.id, user_id=message.from_user.id):
            target = message.reply_to_message.from_user.id
            target_name = message.reply_to_message.from_user.first_name
            if is_user_admin(chat_id=message.chat.id, user_id=target):
                Bot.reply_to(message, 'نمیتونم ادمینا رو میوت کنم متاسفانه 🦦💔')
            else:
                msg = Bot.reply_to(message, 'چند دقیقه میوت باشه؟ (یه عدد بده)')
                Bot.register_next_step_handler(msg, mute, target_user=target, target_name=target_name)
        else:
            Bot.reply_to(message, 'ادمین نیستی')
    else:
        pass
def mute(message, target_user, target_name):
    try:
        minutes = int(message.text)
    except:
        Bot.reply_to(message, 'فقط عدد بفرست 🫥')
        return

    until = datetime.now() + timedelta(minutes=minutes)
    chatid = message.chat.id
    try:
        Bot.restrict_chat_member(chatid, target_user, until_date=until, permissions=telebot.types.ChatPermissions(
            can_send_messages= False,
            can_send_media_messages= False,
            can_send_other_messages= False,
            can_add_web_page_previews= False))
        Bot.reply_to(message, f'{target_name} برای {minutes} دقیقه میوت شد')
    except Exception as e:
        wrong(message, e, line='1093')

    

# Unmute
@Bot.message_handler(func=lambda message: message.text == 'آنمیوت')
def unmute(message):
    chatID = message.chat.id
    userID = message.from_user.id
    if is_user_admin(chatID, userID):
        if message.reply_to_message:

            until = datetime.now() + timedelta(minutes=3)
            user = message.reply_to_message.from_user.id
            chatid = message.chat.id
            try:
                Bot.restrict_chat_member(chatid, user, until_date=until, permissions=telebot.types.ChatPermissions(
                    can_send_messages= True,
                    can_send_media_messages= True,
                    can_send_other_messages= True,
                    can_add_web_page_previews= True))
                Bot.reply_to(message, 'حل شد.')
            except Exception as e:
                wrong(message, e, line='890')
        else:
            pass
    else:
        Bot.reply_to(message, 'ادمین نیستی')


# Text edited
@Bot.edited_message_handler(func=lambda m: True)
def edited(message):
    USERid = message.from_user.id
    if USERid != IdAli:
        Name = message.from_user.first_name
        try:
            Bot.reply_to(message, f'علیییی\n {Name} پیامشو ادیت زد')
        except Exception as e:
            wrong(message, e, line='906')
    else:
        Bot.reply_to(message, 'تریییی \nعلی پیامشو ادیت زد 🦦')


# invite link
@Bot.message_handler(func=lambda m: m.text == 'لینک' and m.chat.type in ['group', 'supergroup'])
def invite_link(message):
    try:
        invite = Bot.create_chat_invite_link(message.chat.id, name="My Bot's link")
        link = invite.invite_link
        Bot.reply_to(message, f'لینک دعوت به گپ: {link}')
    except Exception as e:
        wrong(message, e)

    
# Bad words
@Bot.message_handler(func=lambda message: message.text == 'برین بهش')
def fosh(message):
    if message.reply_to_message:
        userid = message.reply_to_message.from_user.id
        if userid != Bot_id:
        
            Bot.reply_to(message.reply_to_message, fohsh)
            time.sleep(2)
            Bot.reply_to(message, 'بسشه؟')

        else:
            Bot.reply_to(message, 'تو منو فر خرض کردی؟')
    else:
        pass


# Delete
@Bot.message_handler(func=lambda message: message.text == 'پاکش کن')
def dlt(message):

    chatID = message.chat.id
    userID = message.from_user.id
    if is_user_admin(chatID, userID):
        if message.reply_to_message:
            try:
                user = message.from_user.id
                name = message.from_user.first_name
                deleted = message.reply_to_message
                deleted_message = deleted.text
                deleted_user = deleted.from_user.first_name
                time = iran_time()

                delete_keyboard = InlineKeyboardMarkup(row_width=1)
                delbttn = InlineKeyboardButton('مشاهده جزئیات', callback_data=f'MoreInfo_{name}_{deleted_user}_{time}')
                delete_keyboard.add(delbttn)

                
                

                if deleted_message.txt:
                    Bot.send_message(user, f"پیامت پاعک:\n\n'{deleted_message}'")
                    Bot.send_message(IdAli, f"یه پیام پاک شد: {deleted_message}", reply_markup=delete_keyboard)
                else:
                    Bot.send_message(user, 'پیامت پاعک:')
                    send_any_message(user, deleted_message)
                    Bot.send_message(IdAli, 'یه پیام پاک شد که از قضا، تکست نبوده:')
                    send_any_message(IdAli, deleted_message, reply_markup=delete_keyboard)
                
                Bot.delete_message(message.chat.id, message.reply_to_message.id)
                Bot.delete_message(message.chat.id, message.id)
    
            except Exception as e:
                wrong(message, e, line = '939')
        else:
            Bot.reply_to(message, 'چیو پاک کنم کسخل؟ ریپلای کن')
    else:
        pass

@Bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('MoreInfo_'))
def more_info_deleted(call):
    try:
        who = str(call.data.split("_")[1])
        whos = str(call.data.split("_")[2])
        time = str(call.data.split("_")[3])

        Bot.send_message(call.message.chat.id, f'━━━━━━━━━━━━━━\nکی پاک کرد: {who}\nکی رو پاک کرد: {whos}\nساعت: {time}\n━━━━━━━━━━━━━━')

    except Exception as e:
        wrong(call.message, e, line=('1240'))



# Pin
@Bot.message_handler(func=lambda message: message.text == "پین")
def pinMS(message):

    chatID = message.chat.id
    userID = message.from_user.id
    if is_user_admin(chatID, userID):
        if message.reply_to_message:
            Bot.pin_chat_message(message.chat.id, message.reply_to_message.message_id)
            Bot.reply_to(message, '✅')
        if not message.reply_to_message:
            Bot.reply_to(message, 'اگه میخوای چیزیو پین کنی، روش ریپلای کن')
    
    else:
        Bot.reply_to(message, 'فقط ادمینا میتونن')

# Tori        
@Bot.message_handler(regexp=r'تری\b')
def tore(message):
    if message.reply_to_message:
        Bot.reply_to(message, 'با عشق من چیکار داری 🧐😑؟')
    else:
        pass


# New member
@Bot.message_handler(content_types=['new_chat_members'])
def premision(message):
    for user in message.new_chat_members:
        if user.id != Bot_id:
            name = user.first_name
            Bot.send_message(message.chat.id, f'علی اجازه داد بیای {name}؟')
        else:
            Bot.send_message(message.chat.id, 'خوش اومدم ')

# Left member
@Bot.message_handler(content_types=['left_chat_member'])
def goodbye_member(message):
    user = message.left_chat_member
    Bot.send_message(
        message.chat.id,
        f"👋 {user.first_name} Siiiiik")    


# Chos
handle_quarrel(Bot)
handle_chosing(Bot)
check_quarrels(Bot)


@Bot.message_handler(func=lambda message: message.text == 'چنل')
@Only_if_is_Ali
def manage_channel(message):
    msg = Bot.reply_to(message, 'چیو بزارم چنل؟')
    Bot.register_next_step_handler(msg, channel_media)
def channel_media(message):
    try:
        send_any_message(ThekidascryptID, message)
        Bot.reply_to(message, 'ارسال شد!')
    except Exception as e:
        wrong(message, e)

@Bot.message_handler(
    func=lambda m: m.text and "instagram.com/reel" in m.text
)
def handle_instagram_reel(message):
    msg = Bot.reply_to(message, "⏳ در حال دانلود ریلز...")

    download_and_send_reel(
        bot=Bot,
        chat_id=message.chat.id,
        reel_url=message.text.strip()
    )

    Bot.delete_message(message.chat.id, msg.message_id)



@Bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def excl(message):
    try:
        chat = message.chat.title
        safe_name = safe_filename(chat)
        GF_name = f"{safe_name}.db"

        # ایجاد جدول دیتابیس گروه
        create_group_table = '''
            CREATE TABLE IF NOT EXISTS users(
                Name TEXT,
                ID INTEGER PRIMARY KEY
            )
        '''
        with sqlite3.connect(GF_name) as conn:
            cursor = conn.cursor()
            cursor.execute(create_group_table)

        name = message.from_user.first_name
        user_id = message.from_user.id

        # --- مرحله ۱: ثبت در دیتابیس کلی Users.db ---
        with sqlite3.connect(File_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Name FROM users WHERE ID = ?", (user_id,))
            row = cursor.fetchone()

            if row is None:
                # کاربر جدید در دیتابیس کلی
                cursor.execute(
                    "INSERT INTO users (Name, ID) VALUES (?, ?)",
                    (name, user_id)
                )
            else:
                # نام ذخیره‌شده را استفاده می‌کنیم
                name = row[0]

        # --- مرحله ۲: ثبت در دیتابیس گروه ---
        with sqlite3.connect(GF_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE ID = ?", (user_id,))
            exists_group = cursor.fetchone() is not None

            if not exists_group:
                cursor.execute(
                    "INSERT INTO users (Name, ID) VALUES (?, ?)",
                    (name, user_id)
                )

    except Exception as e:
        wrong(message, e, line='1123')





# Poilig
while True:
    try:
        Bot.polling(none_stop=True, interval=0, skip_pending=True)
    except Exception as e:
        print(f"Bot stopped due to: {e}")
        time.sleep(5)



