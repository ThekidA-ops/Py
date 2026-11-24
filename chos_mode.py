import re
import pandas as pd
import sqlite3

USERS_FILE = 'Users.db'

def is_chat_private(message):
    if message.chat.type in ['private']:
        return True
    else:
        return False

def load_db():
    with sqlite3.connect(USERS_FILE) as conn:
        return pd.read_sql_query("SELECT Name, ID FROM users", conn)

def safe_filename(name):
    if not name:
        return "Unknown_Group"

# دیکشنری برای نگهداری روابط قهر
quarrels = {}

def handle_chosing(Bot):
    @Bot.message_handler(regexp= r'چسم')
    def chosing(message):
        if not message.reply_to_message:
            Bot.reply_to(message,"'اگه میخوای اجازه ندم روت ریپلای کنه، روش ریپلای کن و بگو 'چسم")
        else:
            if is_chat_private(message):
                Bot.reply_to(message, 'باید توی گپ باشی!')
            else:
                try:
                    id = message.from_user.id
                    target_name = message.reply_to_message.from_user.first_name
                    target_id = message.reply_to_message.from_user.id
                    quarrels[target_id] = target_id

                    if id == target_id:
                        Bot.reply_to(message, 'آدم عاقل با خودش قهر میکنه؟ کسخلی؟')
                    else:
                        Bot.reply_to(message, f"میزونه. {target_name} دیگه اجازه نداره روت ریپ بزنه.")

                except Exception as e:
                    Bot.reply_to(message, f"⚠️ خطا در حالت قهر:\n{e}")
        




def handle_quarrel(Bot):
    """
    فعال‌سازی حالت قهر از طریق پیام 'من با [اسم] چسم'
    """
    @Bot.message_handler(regexp=r'^من با (.+) چسم$')
    def set_quarrel(message):
        if is_chat_private(message):
            Bot.reply_to(message, 'باید توی گپ باشی!')

        else:
            try:
                match = re.match(r'^من با (.+) چسم$', message.text)
                if not match:
                    return

                target_name = match.group(1).strip()

                # بارگذاری فایل کاربران
                df = load_db()
                target = df[df['Name'].str.contains(target_name, case=False, na=False)]

                if not target.empty:
                    target_id = str(target.iloc[0]['ID'])
                    user_id = str(message.from_user.id)

                    quarrels[user_id] = target_id
                    Bot.reply_to(message, f"میزونه. {target_name} دیگه اجازه نداره روت ریپ بزنه.")
                else:
                    Bot.reply_to(message, "اسمش تو لیست نیست 🦦")

            except Exception as e:
                Bot.reply_to(message, f"⚠️ خطا در حالت قهر:\n{e}")



def chos2(Bot, message):
    if message.reply_to_message:
        try:
            target_id = message.reply_to_message.from_user.id
            target_name = message.reply_to_message.from_user.first_name
            userid = message.from_user.id
            quarrels[userid] = target_id
            Bot.reply_to(message,f"میزونه. {target_name} دیگه اجازه نداره روت ریپ بزنه.")
        except Exception as e:
            Bot.reply_to(message, f"⚠️ خطا در حالت قهر:\n{e}")
    else:
        Bot.reply_to(message, 'با کی چصی کسخل؟')





def check_quarrels(Bot):
    """
    بررسی هر پیام جدید، شامل حذف پیام‌های طرف قهر و امکان آشتی
    """
    @Bot.message_handler(func=lambda m: m.reply_to_message is not None)
    def manage_quarrels(message):
        try:
            sender_id = message.from_user.id

            # ✅ حالت آشتی
            if message.reply_to_message and message.text.strip() == 'آشتی':
                replied_id = message.reply_to_message.from_user.id

                # اگر در لیست قهرها بود، حذفش کن
                if quarrels.get(sender_id) == replied_id:
                    quarrels.pop(sender_id)
                    Bot.reply_to(message, "حله 👍")
                else:
                    Bot.reply_to(message, "قهر نبودی که")

                return  # اینجا تمومش کن تا بقیه شرط‌ها اجرا نشن

            # ✅ حذف پیام‌های طرف قهر
            if message.reply_to_message:
                replied_id = message.reply_to_message.from_user.id

                for user, enemy in quarrels.items():
                    # اگر کسی با فرستنده پیام قهره و اون پیام رو برای همون نفر ریپلای کرده
                    if enemy == sender_id and replied_id == user:
                        Bot.delete_message(message.chat.id, message.message_id)
                        break

        except Exception as e:
            Bot.send_message(message.chat.id, f"⚠️ خطا در مدیریت قهر:\n{e}")


