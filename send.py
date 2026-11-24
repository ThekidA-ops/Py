import pandas as pd
import sqlite3

excel = 'Ksg.xlsx'
db = 'Ksg.db'

create_table_query = '''
    CREATE TABLE IF NOT EXISTS users(
    Name text,
    ID integer primary key
    )
    '''
with sqlite3.connect(db) as connection:
    cursor = connection.cursor()
    cursor.execute(create_table_query)



df = pd.read_excel(excel)
rows = list(df.itertuples(index=False, name=None))

sample_data_query = '''
    INSERT INTO users(Name, ID)
    VALUES (?,?)
'''


with sqlite3.connect(db) as connection:
    cursor = connection.cursor()
    cursor.executemany(sample_data_query, rows)