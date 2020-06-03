import sqlite3
import re

def map_wikidata():
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    add_wdid = "UPDATE Wikipedia SET Wikidata_id = ? WHERE ppn = ?"
    file = open('wikidatamapping-nonENNL.txt', "r", encoding="utf-8")
    lines = file.readlines()
    for line in lines:
        match = re.search(r":\s(.*)", line)
        wdid = match.group(1)
        ppn = re.match("(.*?) |", line).group()
        ppn = ppn.strip()
        insert_wdid = (wdid, ppn)
        cur.execute(add_wdid, insert_wdid)
        con.commit()


map_wikidata()