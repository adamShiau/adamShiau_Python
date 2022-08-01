import sqlite3
import pandas as pd

df = pd.read_csv('Billionaire.csv')
conn = sqlite3.connect('Billionaire.db')
cursor = conn.cursor()
# cursor.execute('CREATE TABLE Billionaire(Name, NetWorth, Country, Source, Rank555)')
# cursor.execute('CREATE TABLE TTTTT(Name, NetWorth, Country, Source, Rank)')
# cursor.execute('CREATE TABLE Adam(Name, abc, def)')

df.to_sql('TTTTT', conn, if_exists='append', index=False)

conn.commit()
print(df)