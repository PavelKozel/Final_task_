from sys import argv
import os


import collections
import xml.etree.ElementTree as ET
import sqlite3
from datetime import datetime
import time                         # importing all required modules


class Configurator:

    def __init__(self, environment):
        """Class Configurator is used for receiving environment variables with the paths of the folders"""
        with open('config.json') as f:
            self.config = eval(f.read())
        self.config = self.config[environment]

    def get_database_url(self):
        """get_database_url method is used to receive path of the database"""
        return self.config['dbase_path']

    def get_input_data_folder(self):
        """get_input_data_folder method is used to receive path of the input folder"""
        return self.config['input_folder_path']

    def get_trash_data_folder(self):
        """get_trash_data_folder method is used to receive path of the trash folder"""
        return self.config['trash_folder_path']

    def get_processed_data_folder(self):
        """get_processed_data_folder method is used to receive path of the processed folder"""
        return self.config['processed_folder_path']

    def get_period_of_monitoring(self):
        """get_period_of_monitoring method is used to receive period of monitoring"""
        return int(self.config['period_of_monitoring_seconds'])

    def get_interval_of_checking(self):
        """get_period_of_monitoring method is used to receive period of monitoring"""
        return int(self.config['interval_of_checking'])


class Connection:

    def __init__(self):
        """Class Connection is used to establish the connection to the sqlite3 database"""
        pass

    def newconnection(self, path):
        """newconnection method is used for the establishing connection to the database"""
        conn = sqlite3.connect(path)
        return conn


class Logger:

    def __init__(self):
        """Class Logger is used for logging the activity of the working script"""
        pass

    def writing_log(self, conn, message):
        """writing_log method is used to write each activity to the [logs] table """
        c = conn.cursor()
        c.execute("INSERT INTO logs VALUES('" + str(datetime.now()) + "', ' " + message + "')")
        conn.commit()


class FileMoving:

    def __init__(self):
        """Class FileMoving is used for noving of the processed files between the folders"""
        pass

    def listoffiles(self, path):
        """writing_log method is used to get the list of files in the folder"""
        return os.listdir(path)

    def movenotfb2(self, input_folder_path, trash_folder_path, conn, logg):
        """writing_log is used to move not fb2 files to the trash folder"""
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
        """moveprocessedfb2 is used to move processed fb2 files to the processed folder"""
        logg.writing_log(conn, 'Starting moving processed fb2 files')
        if os.listdir(input_folder_path):
            for file_name in os.listdir(input_folder_path):
                os.rename(os.path.join(input_folder_path, file_name), os.path.join(processed_folder_path, file_name))
            logg.writing_log(conn, 'All processed files are moved to processed folder')
        else:
            logg.writing_log(conn, 'The folder is empty, nothing to move')
        conn.commit()
        conn.close()


class Parser:

    def __init__(self):
        """Class Parser is used to parse the xml file"""
        pass

    def parsing_xml(self, path, filemoving):
        """parsing_xml is used to receive the root of the parsed file"""
        name = str(filemoving.listoffiles(path)[0])
        tree = ET.parse(os.path.join(path, name))
        root = tree.getroot()
        return root


class Statistics:

    def __init__(self):
        """Class Statistics is used to calculate the statistics parameters of the book"""
        pass

    def book_name(self, path, filemoving, parser):
        """book_name method is used to get book name"""
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}')+1)]
        book_title = str()
        for i in root.iter(root_tag+'book-title'):
            book_title = book_title + ' ' + i.text
        return book_title

    def paragraphs(self, path, filemoving, parser):
        """paragraphs method is used to calculate the number of paragraphs"""
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}')+1)]
        number_of_paragraphs = len(list(root.iter(root_tag + 'p')))
        return number_of_paragraphs

    def words(self, path, filemoving, parser):
        """words method is used to calculate the number of words"""
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        number_of_words = 0
        for i in root.iter(root_tag+'p'):
            if str(type(i.text)) == "<class 'str'>":
                number_of_words = number_of_words + len(list(i.text.split()))
        return number_of_words

    def letters(self, path, filemoving, parser):
        """letters method is used to calculate the number of letters"""
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        number_of_letters = 0
        for i in root.iter(root_tag+'p'):
            if str(type(i.text)) == "<class 'str'>":
                number_of_letters = number_of_letters + len([letter for letter in i.text if letter.isalnum()])
        return number_of_letters

    def words_capital_letter(self, path, filemoving, parser):
        """words_capital_letter method is used to calculate the number of words starting from capital letter"""
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        number_of_words_capital_letter = 0
        for i in root.iter(root_tag+'p'):
            if str(type(i.text)) == "<class 'str'>":
                number_of_words_capital_letter = number_of_words_capital_letter + sum(list(map(lambda x: x.istitle(), i.text.split())))
        return number_of_words_capital_letter

    def words_lower_case(self, path, filemoving, parser):
        """words_lower_case method is used to calculate the number of words in lower case"""
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        number_of_words_in_lower_case = 0
        for i in root.iter(root_tag+'p'):
            if str(type(i.text)) == "<class 'str'>":
                number_of_words_in_lower_case = number_of_words_in_lower_case + sum(list(map(lambda x: x.islower(), i.text.split())))
        return number_of_words_in_lower_case

    def frequency(self, path, filemoving, parser):
        """frequency method is used to calculate the frequency of each word"""
        root = parser.parsing_xml(path, filemoving)
        root_tag = root.tag[0:(root.tag.find('}') + 1)]
        list_of_words = []
        for i in root.iter(root_tag + 'p'):
            if str(type(i.text)) == "<class 'str'>":
                for word in i.text.split():
                    alphanumeric_filter = filter(str.isalnum, word)
                    alphanumeric_string = "".join(alphanumeric_filter)
                    list_of_words.append(alphanumeric_string)
        dict_of_frequency = collections.Counter(list_of_words)
        return dict_of_frequency


class DBfilling:

    def __init__(self):
        """DBfilling method is used to fill the appropriate table with the new data"""
        pass

    def fill_book_table(self, statistics, path, filemoving, conn, logg, parser):
        """fill_book_table method is used to fill [stats] table"""
        logg.writing_log(conn, 'Starting filling book table')
        c = conn.cursor()
        results = (statistics.book_name(path, filemoving, parser), statistics.paragraphs(path, filemoving, parser),
                   statistics.words(path, filemoving, parser), statistics.letters(path, filemoving, parser),
                   statistics.words_capital_letter(path, filemoving, parser), statistics.words_lower_case(path, filemoving, parser))
        sql = "INSERT INTO stats VALUES(?,?,?,?,?,?)"
        c.execute(sql, results)
        logg.writing_log(conn, 'Book table is filled')
        conn.commit()

    def fill_words_table(self, statistics, path, filemoving, conn, logg, parser):
        """fill_words_table method is used to fill [words] table"""
        logg.writing_log(conn, 'Starting filling words table')
        c = conn.cursor()
        val1 = statistics.book_name(path, filemoving, parser).replace(' ', '_')
        sql1 = "CREATE TABLE " + val1 + " (word text, count integer, count_uppercase integer)"
        c.execute(sql1)
        val2 = statistics.frequency(path, filemoving, parser)
        sql2 = "INSERT INTO " + val1 + " VALUES(?,?,?)"
        for key, value in val2.items():
            if not key.istitle():
                c.execute(sql2, (key, value, (0 if val2.get(key.capitalize()) == None else val2.get(key.capitalize()))))
        logg.writing_log(conn, 'Words table is filled')
        conn.commit()


def main():
    config = Configurator(argv[1])                          # receiving the path parameters, according to the env
    path1 = config.get_input_data_folder()
    path2 = config.get_trash_data_folder()
    path3 = config.get_processed_data_folder()
    path4 = config.get_database_url()
    period = config.get_period_of_monitoring()
    interval = config.get_interval_of_checking()
    t = 0
    filemoving = FileMoving()
    connection = Connection()
    logg = Logger()
    parser = Parser()
    statistics = Statistics()
    dbfilling = DBfilling()

    for path in (path1, path2, path3):
        os.mkdir(path)

    for file_name in os.listdir("Test_data"):               # moving test file to the input folder
        os.rename(os.path.join("Test_data", file_name), os.path.join(path1, file_name))

    connect = connection.newconnection(path4)               # creating connection to the db
    c = connect.cursor()
    try:                                                    # creating table if not exists
        c.execute("SELECT * FROM logs")
    except:
        c.execute("CREATE TABLE logs (datetime text, log_message text)")
    try:
        c.execute("SELECT * FROM stats")
    except:
        c.execute('''CREATE TABLE stats
             (book_name text, number_of_paragraph integer, number_of_words integer, number_of_letters integer,
             words_with_capital_letters integer, words_in_lowercase integer)''')

    while t < period:                                               # monitoring during period with the interval
        if filemoving.listoffiles(path1):
            filemoving.movenotfb2(path1, path2, connect, logg)                     # moving not fb2 files to trash
            if filemoving.listoffiles(path1):
                dbfilling.fill_book_table(statistics, path1, filemoving, connect, logg, parser)  # filling of the tables
                dbfilling.fill_words_table(statistics, path1, filemoving, connect, logg, parser)  # filling of the tables
                filemoving.moveprocessedfb2(path1, path3, connect, logg)    # moving of the processed file
            else:
                print("Nothing to process")
            print("Processing is finished")
        else:
            print("Nothing to process")
        time.sleep(interval)                                       # monitoring during period with the interval
        t += interval

    connect.close()


if __name__ == '__main__':
    main()


