import sqlite3
import pywikibot
import re

con = sqlite3.connect('C:/Users/nizar/Downloads/demosaurus.sqlite')
cur = con.cursor()
cur.execute("Select DISTINCT(Wikipedia.ppn), Wikipedia.identifier, Wikipedia.language from NTA inner join Wikipedia on Wikipedia.ppn = NTA.ppn inner join authorship_ggc on NTA.ppn = authorship_ggc.ppn WHERE Wikipedia.identifier IS NOT NULL and (language = 'nl' or language = 'en')")
wikidata_authors = cur.fetchall()
file = open('wikidatamapping.txt', "w", encoding="utf-8")
ppns = []
for author in wikidata_authors:
   language = author[2]
   name = author[1]
   ppn = author[0]
   if language == 'en':
      wikilink = name
      wikilink = re.sub(r'https://en.wikipedia.org/wiki/', '', wikilink)
      name = wikilink.replace("_", " ")
   elif language == 'nl':
      wikilink = name
      wikilink = re.sub(r'https://nl.wikipedia.org/wiki/', '', wikilink)
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