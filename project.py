import os
import collections
import xml.etree.ElementTree as ET
import sqlite3
from datetime import datetime, date, time

path1 = 'C:\Work\Input'
path2 = 'C:\Work\Incorrect_input'
path3 = 'C:\Work\Processed'
path4 = r'C:\sqlite\db\ebooksstat2.db'

class Connection():

    def __init__(self):
        pass
        # print('Connection to the DB')

    def newconnection(self, path):
        conn = sqlite3.connect(path)
        return conn

class Logger():

    def __init__(self):
        pass
        # print('Logging of the processes')

    def writing_log(self, conn, message):
        c = conn.cursor()
        c.execute("INSERT INTO logs VALUES('" + str(datetime.now()) + "', ' " + message + "')")
        conn.commit()

class FileMoving():

    def __init__(self):
        pass
        # print('Checking and moving class')

    def listoffiles(self, path):
        return os.listdir(path)

    def movenotfb2(self, input_folder_path, trash_folder_path, conn, logg):
        logg.writing_log(conn, 'Starting moving not fb2 files')
        if os.listdir(input_folder_path):
            if any([x[-4:] != '.fb2' for x in os.listdir(input_folder_path)]):
                for file_name in os.listdir(input_folder_path):
                    if file_name[-4:] != '.fb2':
                        os.rename(os.path.join(input_folder_path, file_name), os.path.join(trash_folder_path, file_name))
                logg.writing_log(conn, 'All files with incorrect format are moved to trash folder')
            else:
                logg.writing_log(conn, 'All files in the input folder are correct')
        else:
            logg.writing_log(conn, 'The folder is empty, nothing to move')
        conn.commit()

    def moveprocessedfb2(self, input_folder_path, processed_folder_path, conn, logg):
        logg.writing_log(conn, 'Starting moving processed fb2 files')
        if os.listdir(input_folder_path):
            for file_name in os.listdir(input_folder_path):
                os.rename(os.path.join(input_folder_path, file_name), os.path.join(processed_folder_path, file_name))
            logg.writing_log(conn, 'All processed files are moved to processed folder')
        else:
            logg.writing_log(conn, 'The folder is empty, nothing to move')
        conn.commit()
        conn.close()

class Parser():

    def __init__(self):
        pass
        # print("Parsing of the xml file")

    def parsing_xml(self, path, filemoving):
        name = str(filemoving.listoffiles(path)[0])
        tree = ET.parse(os.path.join(path, name))
        root = tree.getroot()
        return root

class Statistics():

    def __init__(self):
        pass
        # print('Statistics of the e-book')

    def book_name(self, path, filemoving, parser):
        # book name
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}')+1)]
        book_title = str()
        for i in root.iter(root_tag+'book-title'):
            book_title = book_title + ' ' + i.text
        return book_title

    def paragraphs(self, path, filemoving, parser):
        # number of paragraphs
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}')+1)]
        number_of_paragraphs = len(list(root.iter(root_tag + 'p')))
        return number_of_paragraphs

    def words(self, path, filemoving, parser):
        # number of words
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        number_of_words = 0
        for i in root.iter(root_tag+'p'):
            if str(type(i.text)) == "<class 'str'>":
                number_of_words = number_of_words + len(list(i.text.split()))
        return number_of_words

    def letters(self, path, filemoving, parser):
        # number of letters
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        number_of_letters = 0
        for i in root.iter(root_tag+'p'):
            if str(type(i.text)) == "<class 'str'>":
                number_of_letters = number_of_letters + len([letter for letter in i.text if letter not in
                    (os.linesep, ' ', '.', ',', ':', ';', '-', '!', '?', '(', ')')])
        return number_of_letters

    def words_capital_letter(self, path, filemoving, parser):
        # number of words first letter capitalized
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        number_of_words_capital_letter = 0
        for i in root.iter(root_tag+'p'):
            if str(type(i.text)) == "<class 'str'>":
                number_of_words_capital_letter = number_of_words_capital_letter + sum(list(map(lambda x: x.istitle(), i.text.split())))
        return number_of_words_capital_letter

    def words_lower_case(self, path, filemoving, parser):
        # number of words in lower case
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        number_of_words_in_lower_case = 0
        for i in root.iter(root_tag+'p'):
            if str(type(i.text)) == "<class 'str'>":
                number_of_words_in_lower_case = number_of_words_in_lower_case + sum(list(map(lambda x: x.islower(), i.text.split())))
        return number_of_words_in_lower_case

    def frequency(self, path, filemoving, parser):
        # frequency of each word
        root = parser.parsing_xml(path, filemoving)
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
        pass
        # print('Filling of the tables')

    def fill_book_table(self, statistics, path, filemoving, conn, logg, parser):
        # filling of the first table
        logg.writing_log(conn, 'Starting filling book table')
        # name = filemoving.listoffiles(path)[0]
        c = conn.cursor()
        results = (statistics.book_name(path, filemoving, parser), statistics.paragraphs(path, filemoving, parser),
                   statistics.words(path, filemoving, parser), statistics.letters(path, filemoving, parser),
                   statistics.words_capital_letter(path, filemoving, parser), statistics.words_lower_case(path, filemoving, parser))
        sql = "INSERT INTO stats VALUES(?,?,?,?,?,?)"
        c.execute(sql, results)
        logg.writing_log(conn, 'Book table is filled')
        conn.commit()

    def fill_words_table(self, statistics, path, filemoving, conn, logg, parser):
        # creating and filling of the second table
        logg.writing_log(conn, 'Starting filling words table')
        # name = filemoving.listoffiles(path)[0]
        c = conn.cursor()
        val1 = statistics.book_name(path, filemoving, parser).replace(' ', '_')
        sql1 = "CREATE TABLE " + val1 + " (word text, count integer)"
        c.execute(sql1)
        val2 = statistics.frequency(path, filemoving, parser)
        sql2 = "INSERT INTO " + val1 + " VALUES(?,?)"
        for key, value in val2.items():
            c.execute(sql2, (key, value))
        logg.writing_log(conn, 'Words table is filled')
        conn.commit()



def main():
    filemoving = FileMoving()
    connection = Connection()
    logg = Logger()
    parser = Parser()
    statistics = Statistics()
    dbfilling = DBfilling()
    connect = connection.newconnection(path4)
    c = connect.cursor()
    try:
        c.execute("SELECT * FROM logs")
    except:
        c.execute("CREATE TABLE logs (datetime text, log_message text)")
    try:
        c.execute("SELECT * FROM stats")
    except:
        c.execute('''CREATE TABLE stats
             (book_name text, number_of_paragraph integer, number_of_words integer, number_of_letters integer, 
             words_with_capital_letters integer, words_in_lowercase integer)''')
    if filemoving.listoffiles(path1):
        filemoving.movenotfb2(path1, path2, connect, logg)
        if filemoving.listoffiles(path1):
            dbfilling.fill_book_table(statistics, path1, filemoving, connect, logg, parser)
            dbfilling.fill_words_table(statistics, path1, filemoving, connect, logg, parser)
            filemoving.moveprocessedfb2(path1, path3, connect, logg)
        else:
            print("Nothing to process")
        print("Processing is finished")
    else:
        print("Nothing to process")
    connect.close()

if __name__ == '__main__':
    main()




