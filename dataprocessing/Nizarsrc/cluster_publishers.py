import sqlite3
import re
import difflib
from .preprocessing import process_text, add_new_column

def process_publisher(publisher):
    throwaway = ['uitgeverij', 'uitgevers', 'uitgever', 'drukkerij', 'uitgegeven',
                 'boekdrukkerij', 'uitgeversmaatschappij', 'uitgeversmij'
        , 'n.v.', 'uitgevers-maatschappij', 'maatschappij', '-maatschappij',
                 '-', 'uitgevers-mij', 'gebr', '.', ']', '[', 'gebroeders'
        , 'stichting', 'n.v', 'b.v', 'b.v.', 'be', 'uitgeversmij',
                 'mij.', '-mij', '-mij.', 'uitg.', 'mij', 'amsterdam', 'holland']
    publisher_2 = re.sub('^.*?: ', '', publisher)
    publisher_3 = process_text(publisher_2, split=False, lowercase=True, token=True, stopword=False, stemming=False)
    clean_publisher = []
    for i in publisher_3:
        if i not in throwaway:
            clean_publisher.append(i)
    publisher_final = ' '.join(word for word in clean_publisher)
    publisher_final = publisher_final.strip()
    return publisher_final


def compute_similarity(publisher1, publisher2):
    return difflib.SequenceMatcher(None, publisher1, publisher2).ratio()


def get_publishers_from_db():
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    publishers = cur.execute(
        "SELECT rowid, uitgever_agg FROM publication_basicinfo GROUP BY uitgever_agg ORDER BY count(uitgever_agg) desc").fetchall()
    id_publishers = [(rowid, process_publisher(publisher)) for rowid, publisher in publishers]
    dup_publishers = [(rowid, publisher) for rowid, publisher in id_publishers]
    return id_publishers, dup_publishers


def group_publishers_surface_level():
    # i did not use 'throwaway' words with this method
    # similarity set at 88% (strict)
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    id_publishers, dup_publishers = get_publishers_from_db()
    new_column = add_new_column("publication_basicinfo", "uitgever_agg")
    group_publishers = "UPDATE publication_basicinfo SET " + str(new_column) + " = ? WHERE uitgever = ?"
    get_uitgever = "SELECT uitgever FROM publication_basicinfo WHERE rowid = ?"
    for rowid, publisher in id_publishers:
        relevant = []
        for rowid2, publisher2 in dup_publishers:
            similarity = compute_similarity(publisher, publisher2)
            if similarity > 0.88:
                relevant.append((rowid2, publisher2))
                uitgever = cur.execute(get_uitgever, (rowid2,))
                update_data = (str(publisher), str(uitgever.fetchall()[0][0]))
                cur.execute(group_publishers, update_data)
                con.commit()
        for i in relevant:
            dup_publishers.remove(i)
        print(len(dup_publishers))
    cur.close()


def group_publishers_in_depth():
    #aggregrate with more rules
    con = sqlite3.connect('demosaurus.sqlite')
    cur = con.cursor()
    id_publishers, dup_publishers = get_publishers_from_db()
    new_column = add_new_column("publication_basicinfo", "uitgever_agg")
    group_publishers = "UPDATE publication_basicinfo SET " + str(new_column) + " = ? WHERE uitgever_agg = ?"
    get_uitgever = "SELECT uitgever_agg FROM publication_basicinfo WHERE rowid = ?"
    for rowid, publisher in id_publishers:
        relevant = []
        for rowid2, publisher2 in dup_publishers:
            similarity = compute_similarity(publisher, publisher2)
            if " " + publisher + " " in publisher2 or publisher + " " in publisher2 or publisher2.endswith(
                    " " + publisher):
                similarity = similarity + 0.5
            if similarity > 0.88:
                relevant.append((rowid2, publisher2))
                uitgever = cur.execute(get_uitgever, (rowid2,))
                update_data = (str(publisher), str(uitgever.fetchall()[0][0]))
                cur.execute(group_publishers, update_data)
                con.commit()
        for i in relevant:
            dup_publishers.remove(i)
        print(len(dup_publishers))
    cur.close()
