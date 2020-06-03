import sqlite3
import pywikibot
import re

con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
cur = con.cursor()
cur.execute("Select DISTINCT(Wikipedia.ppn), Wikipedia.identifier, Wikipedia.language from NTA inner join Wikipedia on Wikipedia.ppn = NTA.ppn inner join authorship_ggc on NTA.ppn = authorship_ggc.ppn WHERE Wikipedia.identifier IS NOT NULL and Wikipedia.ppn not in (SELECT ppn from Wikipedia where language = 'en' or language = 'nl') and language IS NOT 'species'")
wikidata_authors = cur.fetchall()
file = open('wikidatamapping-nonENNL.txt', "w", encoding="utf-8")
ppns = []
for author in wikidata_authors:
   language = author[2]
   if '_' in language:
      language = language.replace('_', "-")
   name = author[1]
   ppn = author[0]
   wikilink = name
   wikilink = re.sub(r'https://' + str(language) + '.wikipedia.org/wiki/', '', wikilink)
   name = wikilink.replace("_", " ")
   site = pywikibot.Site(str(language))
   page = pywikibot.Page(site, name)
   wikidata_id = ""
   if ('wikibase_item' in page.properties()):
       wikidata_id = (page.properties()['wikibase_item'])
   else:
      pass  # no wikidata for this page
   if ppn not in ppns:
      file.write(ppn + " | " +  name + ": " + wikidata_id + "\n")
      ppns.append(ppn)
   else:
      pass
print("succes")
cur.close()