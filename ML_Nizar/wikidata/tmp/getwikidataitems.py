import pywikibot
import pprint
import re
import sqlite3

file = open('wikidatamapping.txt', "r", encoding="utf-8")
lines = file.readlines()
wdids = []
for line in lines:
    match = re.search(r":\s(.*)", line)
    wdid = match.group(1)
    wdids.append(wdid)


for wdid in wdids:
    site = pywikibot.Site('nl')
    repo = site.data_repository()
    item = pywikibot.ItemPage(repo, wdid)
    item_dict = item.get()
    clm_dict = item_dict["claims"]
    clm_add_all = []
    for clm in clm_dict:
        clm_add_all.append(clm)
    #print(clm_add_all)
    dict = {}
    for property in clm_add_all:
        clm_list = clm_dict[property]
        qids = []
        for clm in clm_list:
            pprint.pprint(clm.toJSON())
            #pprint.pprint(clm.toJSON())
            #pprint.pprint(clm.toJSON()['mainsnak'].get('datavalue', {}).get('value', {}).get('numeric-id'))
            if clm.toJSON()['mainsnak'].get('datavalue') is not None:
                if 'numeric-id' in clm.toJSON()['mainsnak'].get('datavalue', {}).get('value'):
                    qid = "Q" + str(clm.toJSON()['mainsnak'].get('datavalue', {}).get('value', {}).get('numeric-id'))
                else:
                    qid = clm.toJSON()['mainsnak'].get('datavalue', {}).get('value')
            else:
                qid = "None"
            qids.append(qid)
        dict[property] = qids
    pprint.pprint(dict)

###FOR ADDING TO DATABASE:
#if property doesn't exist yet
# con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
# cur = con.cursor()
# table_wikidata = "PRAGMA table_info('Wikidata');"
# varlist = dict.values()
# values_string = ', '.join('?' * len(varlist))
# insert_wikidata = "INSERT INTO Wikidata dict.keys() VALUES (%s);' % var_string"
# cur.execute(table_wikidata)
# table_wikidata = cur.fetchall()
# for i in list(dict.keys()):
#     if i not in table_wikidata:
#         add_new_column('Wikidata', i)
# cur.execute(insert_wikidata, dict.values())
# cur.close()
