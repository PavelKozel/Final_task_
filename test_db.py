import sqlite3

conn = sqlite3.connect(r'C:\sqlite\db\ebooksstat2.db')

c = conn.cursor()
conn.close()

c.execute('''CREATE TABLE stats
             (book_name text, number_of_paragraph integer, number_of_words integer, number_of_letters integer, 
             words_with_capital_letters integer, words_in_lowercase integer)''')
c.execute('''CREATE TABLE logs (datetime text, log_message text)''')


c.execute("DROP TABLE stats")

c.execute("SELECT COUNT(*) FROM stats")
rows = c.fetchall()
for row in rows:
    print(row)

c.execute("DROP TABLE _Цветы_для_Элджернона_Flowers_for_Algernon")

c.execute("SELECT COUNT(*) FROM _Цветы_для_Элджернона_Flowers_for_Algernon")
rows = c.fetchall()
for row in rows:
    print(row)

c.execute("DROP TABLE logs")

c.execute("SELECT * FROM logs")
rows = c.fetchall()
for row in rows:
    print(row)


