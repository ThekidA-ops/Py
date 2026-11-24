import pandas as pd
import sqlite3
import os

File_name = 'Users.db'
Group_members = 'Group.db'

create_table_query = '''
    CREATE TABLE IF NOT EXISTS users(
        Name text,
        ID integer primary key
    )
'''
with sqlite3.connect(File_name) as connection:
    cursor = connection.cursor()
    cursor.execute(create_table_query)



sample_data_query = '''
    INSERT INTO users (Name, ID)
    VALUES (?,?)
'''



def get_name(Bot, message, group_file=None):
    """دریافت یا بروزرسانی نام کاربر و در صورت لزوم آپدیت فایل گروه"""
    
    if not message.reply_to_message:
        Bot.send_message(message.chat.id, "رو پیام من ریپلای بزن 😅")
        return

    if message.reply_to_message.from_user.id != Bot.get_me().id:
        Bot.send_message(message.chat.id, "باید روی پیام خود من ریپلای کنی 😤")
        return

    name = message.text.strip()
    user_id = message.from_user.id

    sample_data = (name, user_id)



    with sqlite3.connect(File_name) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM users WHERE ID = ?", (user_id,))
        exists = cursor.fetchone() is not None

    if exists:
        with sqlite3.connect(File_name) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO users (ID, Name) VALUES (?, ?)
                ON CONFLICT(ID) DO UPDATE SET Name=excluded.Name
            """, (user_id, name))
    else:
        with sqlite3.connect(File_name) as connection:
            cursor = connection.cursor()
            cursor.execute(sample_data_query, sample_data)

    Bot.send_message(message.chat.id, f'ثبت شدی {name} 🍒')




def show_info(Bot, message):
    """نمایش اطلاعات کاربران"""
    import sqlite3

    with sqlite3.connect(File_name) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]

    if count == 0:
        Bot.reply_to(message, 'فایل خالیه، هنوز کسی ثبت نشده !💌')
    else:
        rows = []
        fetch_data_query = '''
            SELECT Name, ID FROM users
        '''
        with sqlite3.connect('Users.db') as connection:
            cursor = connection.cursor()
            cursor.execute(fetch_data_query)
            rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=['Name','ID'])
        text = "📋 لیست کاربران:\n\n"
        for i, row in df.iterrows():
            text += f"{i+1}. {row['Name']} — {row['ID']}\n"
        Bot.send_message(message.chat.id, text)





def change(Bot, message, name):

    user_id = message.reply_to_message.from_user.id

    with sqlite3.connect(File_name) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM users WHERE ID = ?", (user_id,))
        exists = cursor.fetchone() is not None

    if exists:
        with sqlite3.connect(File_name) as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO users (ID, Name) VALUES (?, ?)
                ON CONFLICT(ID) DO UPDATE SET Name=excluded.Name
            """, (user_id, name))
        Bot.reply_to(message, f'از الان اسمش {name}ه')

    else:
        sample_data = (name, user_id)
        with sqlite3.connect(File_name) as connection:
            cursor = connection.cursor()
            cursor.execute(sample_data_query, sample_data)

        Bot.reply_to(message, f"✅ {name} ثبت شد 🌹")