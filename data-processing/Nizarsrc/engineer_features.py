import sqlite3
from unidecode import unidecode
from preprocessing import process_text, add_new_column

#Feature engineering #1: Count number of authors per publication
def count_number_of_entity(table1, table2, entity):
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    column_name = add_new_column(table2, "number_of_" + str(entity))
    cur.execute("SELECT publication_ppn, COUNT(publication_ppn) FROM " + str(table1) + " GROUP BY publication_ppn")
    rows = cur.fetchall()
    add_number_of_authors = "UPDATE " + str(table2) + " SET " + str(column_name) + " = ? WHERE ppn = ?"
    for row in rows:
        insert_data = (str(row[1]), str(row[0]))
        cur.execute(add_number_of_authors, insert_data)
        con.commit()
    con.close()

#count_number_of_entity("authorship_ggc", "publication_basicinfo", "authors")

#Feature engineering #2: Measure length of title in characters, spaces etc. Everything included.
def get_length_text(table, text):
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    column_name = add_new_column(str(table), "length_of_" + str(text))
    cur.execute("SELECT ppn, " + str(text) + " FROM " + str(table))
    rows = cur.fetchall()
    add_text_length = "UPDATE " + str(table) + " SET " + str(column_name) + " = ? WHERE ppn = ?"
    i = 0
    for row in rows:
        #get length of text string
        i = i + 1
        if i > 74000:
            text_length = len(row[1])
            insert_data = (text_length, str(row[0]))
            cur.execute(add_text_length, insert_data)
            con.commit()
        if i % 10000 == 0:
            print('nummer: ' + str(i))


#get_length_text("publication_basicinfo", "titelvermelding")

#Feature engineering #3: Measure length of title in words.
def get_number_of_words(table, text):
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    column_name = add_new_column(str(table), "number_of_words_in_" + str(text))
    cur.execute("SELECT ppn, " + str(text) + " FROM " + str(table))
    rows = cur.fetchall()
    add_number_of_words = "UPDATE " + str(table) + " SET " + str(column_name) + " = ? WHERE ppn = ?"
    i = 0
    for row in rows:
        no_accents_text = unidecode(row[1])
        words = process_text(no_accents_text, True, False, False)
        number_of_words = len(words)
        insert_data = (number_of_words, str(row[0]))
        i = i + 1
        if i % 10000 == 0:
            print('nummer: ' + str(i))
        cur.execute(add_number_of_words, insert_data)
        con.commit()

#get_number_of_words("publication_basicinfo", "titelvermelding")


# Feature engineering #4: Measure age of author at the time of publication (if available)
def age_known():
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    cur.execute(
        "SELECT count(birthyear) FROM NTA INNER JOIN authorship_ggc ON NTA.ppn = authorship_ggc.ppn WHERE birthyear IS NOT NULL")
    result = cur.fetchall()[0][0]
    return result


# approximately 57% of the authors have a known age, might be worth it to make a feature based on it in relation to publication
print(age_known() / 488048)
