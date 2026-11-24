import pandas as pd
import os

File_name = 'Users.xlsx'
Group_members = 'Group.xlsx'

# اگه فایل وجود نداشت، بسازش
if not os.path.exists(File_name):
    df = pd.DataFrame(columns=['Name', 'UserID'])
    df.to_excel(File_name, index=False)

if not os.path.exists(Group_members):
    df_group = pd.DataFrame(columns=['Name', 'UserID'])
    df_group.to_excel(Group_members, index=False)


def get_name(Bot, message, group_file=None):
    """دریافت یا بروزرسانی نام کاربر و در صورت لزوم آپدیت فایل گروه"""
    
    if not message.reply_to_message:
        Bot.send_message(message.chat.id, "رو پیام من ریپلای بزن 😅")
        return

    if message.reply_to_message.from_user.id != Bot.get_me().id:
        Bot.send_message(message.chat.id, "باید روی پیام خود من ریپلای کنی 😤")
        return

    name = message.text.strip()
    user_id = str(message.from_user.id)

    df = pd.read_excel('Users.xlsx')

    if user_id in df['UserID'].astype(str).values:
        idx = df.index[df['UserID'].astype(str) == user_id][0]
        old_name = df.loc[idx, 'Name']
        df.loc[idx, 'Name'] = name
        msg = f"✅ اسمت از '{old_name}' به '{name}' تغییر کرد!"
    else:
        new_row = pd.DataFrame([[name, user_id]], columns=['Name', 'UserID'])
        df = pd.concat([df, new_row], ignore_index=True)
        msg = f"✅ {name} ثبت شدی 🌹"

    df.to_excel('Users.xlsx', index=False)

    # 💡 اگر فایل گروه داده شده، اون رو هم آپدیت کن
    if group_file and os.path.exists(group_file):
        dfg = pd.read_excel(group_file)
        if user_id in dfg['UserID'].astype(str).values:
            idx = dfg.index[dfg['UserID'].astype(str) == user_id][0]
            dfg.loc[idx, 'Name'] = name
        else:
            new_row = pd.DataFrame([[name, user_id]], columns=['Name', 'UserID'])
            dfg = pd.concat([dfg, new_row], ignore_index=True)
        dfg.to_excel(group_file, index=False)

    Bot.send_message(message.chat.id, msg)




def show_info(Bot, message):
    """نمایش اطلاعات کاربران"""
    if not os.path.exists(File_name):
        Bot.send_message(message.chat.id, "❌ هنوز هیچ کاربری ثبت نشده.")
        return

    df = pd.read_excel(File_name, sheet_name=0)

    if df.empty:
        Bot.send_message(message.chat.id, "ℹ️ فایل خالیه، هیچ کاربری ثبت نشده.")
    else:
        text = "📋 لیست کاربران:\n\n"
        for i, row in df.iterrows():
            text += f"{i+1}. {row['Name']} — {row['UserID']}\n"
        Bot.send_message(message.chat.id, text)




def change(Bot, message, name):

    user_id = str(message.reply_to_message.from_user.id)

    df = pd.read_excel('Users.xlsx')

    if user_id in df['UserID'].astype(str).values:
        idx = df.index[df['UserID'].astype(str) == user_id][0]
        old_name = df.loc[idx, 'Name']
        df.loc[idx, 'Name'] = name
        Bot.reply_to(message, f'اسمش از {old_name} به {name} تغییر کرد')

    else:
        new_row = pd.DataFrame([[name, user_id]], columns=['Name', 'UserID'])
        df = pd.concat([df, new_row], ignore_index=True)
        Bot.reply_to(message, f"✅ {name} ثبت شد 🌹")

    df.to_excel('Users.xlsx', index=False)