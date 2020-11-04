import sqlite3

conn = sqlite3.connect('C:/sqlite/db/ebooksstat2.db')

c = conn.cursor()
conn.close()

c.execute('''CREATE TABLE stats
             (book_name text, number_of_paragraph integer, number_of_words integer, number_of_letters integer, 
             words_with_capital_letters integer, words_in_lowercase integer)''')
c.execute('''CREATE TABLE logs (datetime text, log_message text)''')


c.execute("DROP TABLE stats")

c.execute("SELECT * FROM stats")
rows = c.fetchall()
for row in rows:
    print(row)

# (' Цветы для Элджернона Flowers for Algernon', 2267, 62898, 299183, 8058, 52743)

c.execute("DROP TABLE _Цветы_для_Элджернона_Flowers_for_Algernon")

c.execute("SELECT * FROM _Цветы_для_Элджернона_Flowers_for_Algernon where word = 'и'")
rows = c.fetchall()
for row in rows:
    print(row)

c.execute("DROP TABLE logs")

c.execute("SELECT * FROM logs")
rows = c.fetchall()
for row in rows:
    print(row)

c.execute("SELECT * FROM sqlite_master")
rows = c.fetchall()
for row in rows:
    print(row)

c.execute("DROP TABLE stats")
c.execute("DROP TABLE logs")
c.execute("DROP TABLE _Цветы_для_Элджернона_Flowers_for_Algernon")