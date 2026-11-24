# Bot_modes.py (اصلاح‌شده)
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# متغیرهای سراسری
mode_active = False
IdAli = 8021347462

# لیست کلمات فیلترشده
Bad = ['کیر', 'کون', 'گایید', 'تخم', 'پلشت', 'کص', 'کیون', 'صیک', 'سیک', 'جنده', 'جندس']
pattern = r'(' + '|'.join(re.escape(w) for w in Bad) + r')'

MODE_FILE = 'mode_state.txt'

def save_mode_state(state):
    try:
        with open(MODE_FILE, 'w', encoding='utf-8') as f:
            f.write('on' if state else 'off')
    except Exception as e:
        print("Error saving mode state:", e)

def load_mode_state():
    if os.path.exists(MODE_FILE):
        try:
            with open(MODE_FILE, 'r', encoding='utf-8') as f:
                return f.read().strip() == 'on'
        except Exception as e:
            print("Error loading mode state:", e)
            return False
    return False

mode_active = load_mode_state()

def register_handlers(Bot):
    global mode_active

    # -------------------------------
    # 1️⃣ کامند اصلی برای دیدن وضعیت مود (فقط علی اجازه داره)
    # -------------------------------
    @Bot.message_handler(regexp = '^(filter)$')
    def filter_menu(message):
        if message.from_user.id != IdAli:
            Bot.reply_to(message, "تو اجازه نداری به تنظیمات من دست بزنی 😏")
            return

        status = "✅ فعال" if mode_active else "❌ غیرفعال"
        text = f"🔘 وضعیت فعلی: {status}"

        # ساخت دکمه‌ها به شکل صحیح (inline_keyboard param)
        markup = InlineKeyboardMarkup()
        markup.row(
    InlineKeyboardButton("روشن کن", callback_data="filter_on"),
    InlineKeyboardButton("خاموش کن", callback_data="filter_off")
)


        Bot.send_message(message.chat.id, text, reply_markup=markup)

    # -------------------------------
    # 2️⃣ هندل دکمه‌ها (CallbackQuery)
    # -------------------------------
    @Bot.callback_query_handler(func=lambda call: call.data in ['filter_on', 'filter_off'])
    def toggle_filter(call):
        global mode_active
        # برای اطمینان از دیباگ
        print("toggle_filter called:", call.data, "from user:", call.from_user.id)

        if call.from_user.id != IdAli:
            Bot.answer_callback_query(call.id, "تو اجازه نداری 😏")
            return

        # همیشه جواب callback رو بده تا client لودینگ رو برداره
        Bot.answer_callback_query(call.id, "در حال پردازش...")

        if call.data == 'filter_on':
            mode_active = True
            save_mode_state(mode_active)
            # ویرایش متن پیام قبلی (نمایش نتیجه)
            try:
                Bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"🔘 وضعیت فعلی: ✅ فعال"
                )
            except Exception as e:
                print("edit_message_text error:", e)

        elif call.data == 'filter_off':
            mode_active = False
            save_mode_state(mode_active)
            try:
                Bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"🔘 وضعیت فعلی: ❌ غیرفعال"
                )
            except Exception as e:
                print("edit_message_text error:", e)

    # -------------------------------
    # 3️⃣ هندل فحش‌ها (فقط وقتی مود فعاله)
    # -------------------------------
    @Bot.message_handler(regexp=pattern)
    def adab(message):
        global mode_active

        if not mode_active:
            return  # اگر مود خاموشه، هیچ کاری نکن

        try:
            if message.reply_to_message:
                repliedUser = message.reply_to_message.from_user.id
                if repliedUser == IdAli:
                    Bot.reply_to(message, 'به علی بی‌ادبی کردی؟ ')
                else:
                    Bot.reply_to(message, 'مودب باش نکنمت ')
            else:
                Bot.reply_to(message, 'مودب باش گوت')
        except Exception as e:
            print("Error in adab handler:", e)
