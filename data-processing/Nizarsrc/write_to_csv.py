import sqlite3
import csv

def write_to_csv(table):
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    with open(str(table) + ".csv", 'w',  encoding='utf-8', newline='') as csv_output:
        csvWriter = csv.writer(csv_output, delimiter = '\t')
        cur.execute("SELECT * FROM " + str(table))
        column_names = [description[0] for description in cur.description]
        rows = cur.fetchall()
        csvWriter.writerow(column_names)
        csvWriter.writerows(rows)

write_to_csv("publication_basicinfo")