def fetch_currency_data():
    import requests
    from bs4 import BeautifulSoup
    import pandas as pd


    Price = []
    Names = []
    Cprice = []
    Ctitle = []

    C_URL = 'https://www.tgju.org/crypto'
    CR_URL = 'https://www.tgju.org/currency'

    Currency = requests.get(CR_URL)
    Crypto = requests.get(C_URL)

    soup_Cr = BeautifulSoup(Currency.text, 'html.parser')
    soup_C = BeautifulSoup(Crypto.text, 'html.parser')


    Cname = soup_C.find_all ('span', attrs={'class' : 'original-title-en tgcss-text-xs max-md:tgcss-text-xs3 tgcss-font-semibold'})
    divs = soup_C.find_all ('div', attrs={'class' : 'tgcss-flex tgcss-items-center tgcss-flex-col tgcss-min-w-max tgcss-text-nowrap max-sm:!tgcss-pl-2'})


    prices = soup_Cr.find_all ('td', attrs={'class' : 'nf'})
    Title = soup_Cr.find_all ('th')


    for s in prices:
        for sp in s.find_all('span'):
            sp.decompose()


    for p in prices:
        Price.append(p.text.strip())


    for t in Title:
        Names.append(t.text.strip())

    #

    for div in divs:
        Cprice.append(div.find_next('div').text.strip())


    for i in Cname:
        Ctitle.append(i.text.strip())

    Name1 = Names[7:25]
    Name2 = Names[32:50]
    titles = Name1 + Name2

    C_df = pd.DataFrame({'Title' : Ctitle, 'Price(R)' : Cprice})
    df = pd.DataFrame({'Title' : titles, 'Price(R)' : Price[0::2]})
    return df, C_df



def send_currency_to_Bot(Bot, message):
    df, _ = fetch_currency_data()

    text = "📊 **قیمت ارزها (ریال)**\n\n"
    for i, row in df.iterrows():
        text += f"🔹 {row['Title']}: `{row['Price(R)']}`\n"
    Bot.send_message(message.chat.id, text, parse_mode="Markdown")


def wich_currency(Bot,message ,Na, to_edit):

    df, _ = fetch_currency_data()

    row = df[df['Title'] == Na]
    if row.empty:
        Bot.edit_message_text(
            'ارز مورد نظرتو پیدا نکردم 🫠',
            chat_id=message.chat.id,
            message_id=to_edit.message_id
        )
    else:
        text = "نتیجه:\n\n"
        for idx, r in row.iterrows():
            text += f"• {r['Title']} : {r['Price(R)']} ریال\n"
        Bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=to_edit.message_id
        )
