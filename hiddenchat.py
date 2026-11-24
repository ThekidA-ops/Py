from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, KeyboardButton

IdAli = 8021347462
ThekidascryptID = -1002876585043


def hidden_chat(Bot, message):

    def send_text_to_ali(message):

        callback = str(message.chat.id)
        kb = InlineKeyboardMarkup(row_width=1)
        Hbttn1 = InlineKeyboardButton('پاسخ', callback_data=f'rep_{callback}')
        Pbttn1 = InlineKeyboardButton('ارسال به چنل', callback_data='send')
        kb.add(Pbttn1)
        kb.add(Hbttn1)

        try:
            Bot.send_message(
                IdAli,
                f"📩 پیام ناشناس دریافت شد:\n\n{message.text}",
                reply_markup=kb
            )
            Bot.reply_to(message, 'پیامت ارسال شد 🫶')
        except Exception as e:
            Bot.send_message(message.chat.id, e)

    @Bot.callback_query_handler(func=lambda call: call.data == 'send')
    def send_to_channel(call):
        Orginaltxt = call.message.text
        Bot.send_message(ThekidascryptID, Orginaltxt)
        Bot.reply_to(call.message, 'رفت تو چنل 🙂‍↔️')

    @Bot.callback_query_handler(func=lambda call: call.data and call.data.startswith('rep_'))
    def answer(call):
        target_id = int(call.data.split("_")[1])
        msg = Bot.send_message(call.from_user.id, 'پاسخت رو بنویس، براش ارسال میکنم 👇')
        Bot.register_next_step_handler(msg, send_reaction, target_id)

    def send_reaction(message, target_id):
        Bot.send_message(target_id, f'علی به پیامت پاسخ داد:\n\n {message.text}')




