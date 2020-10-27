import os
import collections
import xml.etree.ElementTree as ET
import sqlite3
from sqlite3 import Error
from datetime import datetime, date, time

path = 'C:\Input1'
path2 = 'C:\Incorrect input'
name = 'Example.fb2'

class FileMoving():

    def __init__(self):
        print('Checking and moving class')

    def listoffiles(self, path):
        return os.listdir(path)[0]

    def movenotfb2(self, input_folder_path, trash_folder_path, conn):
        c = conn.cursor
        if os.listdir(input_folder_path):
            for file_name in os.listdir(input_folder_path):
                with open(file_name):
                    if file_name[-4:] != '.fb2':
                        os.rename(os.path.join(input_folder_path, file_name), os.path.join(trash_folder_path, file_name))
            c.execute("INSERT INTO logs VALUES('" + str(datetime.now()) + "', 'All files with incorrect format are moved to trash folder')")
        else:
            c.execute("INSERT INTO logs VALUES('" + str(datetime.now()) + "', 'The folder is empty, nothing to move')")

    def moveprocessedfb2(self, input_folder_path, processed_folder_path, conn):
        c = conn.cursor
        if os.listdir(input_folder_path):
            for file_name in os.listdir(input_folder_path):
                os.rename(os.path.join(input_folder_path, file_name), os.path.join(processed_folder_path, file_name))
            c.execute("INSERT INTO logs VALUES('" + str(datetime.now()) + "', 'All processed files are moved to processed folder')")
        else:
            c.execute("INSERT INTO logs VALUES('" + str(datetime.now()) + "', 'The folder is empty, nothing to move')")

class Statistics():

    def __init__(self):
        print('Statistics of the e-book')

    def book_name(self, path, file):
        # book name
        name = file.listoffiles(path)
        tree = ET.parse(os.path.join(path, name))
        root = tree.getroot()
        root_tag = root.tag[0:(root.tag.find('}')+1)]
        book_title = str()
        for i in root.iter(root_tag+'book-title'):
            book_title = book_title + ' ' + i.text
        return book_title

    def paragraphs(self, path, file):
        # number of paragraphs
        name = file.listoffiles(path)
        tree = ET.parse(os.path.join(path, name))
        root = tree.getroot()
        root_tag = root.tag[0:(root.tag.find('}')+1)]
        number_of_paragraphs = len(list(root.iter(root_tag + 'p')))
        return number_of_paragraphs

    def words(self, path, file):
        # number of words
        name = file.listoffiles(path)
        tree = ET.parse(os.path.join(path, name))
        root = tree.getroot()
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        number_of_words = 0
        for i in root.iter(root_tag+'p'):
            if str(type(i.text)) == "<class 'str'>":
                number_of_words = number_of_words + len(list(i.text.split()))
        return number_of_words

    def letters(self, path, file):
        # number of letters
        name = file.listoffiles(path)
        tree = ET.parse(os.path.join(path, name))
        root = tree.getroot()
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        number_of_letters = 0
        for i in root.iter(root_tag+'p'):
            if str(type(i.text)) == "<class 'str'>":
                number_of_letters = number_of_letters + len([letter for letter in i.text if letter not in (os.linesep, ' ', '.', ',', ':', ';', '-', '!', '?', '(', ')')])
        return number_of_letters

    def words_capital_letter(self, path, file):
        # number of words first letter capitalized
        name = file.listoffiles(path)
        tree = ET.parse(os.path.join(path, name))
        root = tree.getroot()
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        number_of_words_capital_letter = 0
        for i in root.iter(root_tag+'p'):
            if str(type(i.text)) == "<class 'str'>":
                number_of_words_capital_letter = number_of_words_capital_letter + sum(list(map(lambda x: x.istitle(), i.text.split())))
        return number_of_words_capital_letter

    def words_lower_case(self, path, file):
        # number of words in lower case
        name = file.listoffiles(path)
        tree = ET.parse(os.path.join(path, name))
        root = tree.getroot()
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        number_of_words_in_lower_case = 0
        for i in root.iter(root_tag+'p'):
            if str(type(i.text)) == "<class 'str'>":
                number_of_words_in_lower_case = number_of_words_in_lower_case + sum(list(map(lambda x: x.islower(), i.text.split())))
        return number_of_words_in_lower_case

    def frequency(self, path, file):
        # frequency of each word
        name = file.listoffiles(path)
        tree = ET.parse(os.path.join(path, name))
        root = tree.getroot()
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        list_of_words = []
        for i in root.iter(root_tag + 'p'):
            if str(type(i.text)) == "<class 'str'>":
                for word in i.text.split():
                    list_of_words.append(word.strip('.,:;!?()[]{}"'))
        dict_of_frequency = collections.Counter(list_of_words)
        return dict_of_frequency

class DBfilling():

    def __init__(self):
        print('Filling of the tables')

    def fill_book_table(self, stat, path, file):
        # filling of the first table
        name = file.listoffiles(path)
        conn = sqlite3.connect(r'C:\sqlite\db\ebooksstat.db')
        c = conn.cursor()
        results = (stat.book_name(path, name),stat.paragraphs(path, name),stat.words(path, name),
                   stat.letters(path, name),stat.words_capital_letter(path, name),stat.words_lower_case(path, name))
        sql = "INSERT INTO stats VALUES(?,?,?,?,?,?)"
        c.execute(sql, results)
        c.execute("INSERT INTO logs VALUES('" + str(datetime.now()) + "', 'First table is filled')")
        conn.commit()
        conn.close()

    def fill_words_table(self, stat, path, file):
        # creating and filling of the second table
        name = file.listoffiles(path)
        conn = sqlite3.connect(r'C:\sqlite\db\ebooksstat.db')
        c = conn.cursor()
        val1 = stat.book_name(path, name).replace(' ', '_')
        sql1 = "CREATE TABLE " + val1 + " (word text, count integer)"
        c.execute(sql1)
        val2 = stat.frequency(path, name)
        sql2 = "INSERT INTO " + val1 + " VALUES(?,?)"
        for key, value in val2.items():
            c.execute(sql2, (key, value))
        c.execute("INSERT INTO logs VALUES('" + str(datetime.now()) + "', 'Words table is filled')")
        conn.commit()
        conn.close()

file = FileMoving()
file.listoffiles(path)

d = Statistics()
d.__init__()
d.book_name(path, file)
d.words_lower_case(path, file)

e = DBfilling()
e.fill_book_table(d, path, file)
e.fill_words_table(d, path, file)




conn = sqlite3.connect(r'C:\sqlite\db\ebooksstat.db')
c = conn.cursor()


c.execute('''CREATE TABLE stats
             (book_name text, number_of_paragraph integer, number_of_words integer, number_of_letters integer, 
             words_with_capital_letters integer, words_in_lowercase integer)''')
c.execute("DROP TABLE stats")

c.execute('''CREATE TABLE logs (datetime text, log_message text)''')

c.execute("SELECT * FROM stats")
rows = c.fetchall()
for row in rows:
    print(row)

c.execute("DROP TABLE _Цветы_для_Элджернона_Flowers_for_Algernon")
c.execute("SELECT COUNT(*) FROM _Цветы_для_Элджернона_Flowers_for_Algernon")
rows = c.fetchall()
for row in rows:
    print(row)

c.execute("SELECT * FROM logs")
rows = c.fetchall()
for row in rows:
    print(row)
c.execute("DROP TABLE logs")

