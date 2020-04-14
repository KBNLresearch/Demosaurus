DROP TABLE IF EXISTS onix;
DROP TABLE IF EXISTS publication;
DROP TABLE IF EXISTS author;
DROP TABLE IF EXISTS authorship;
DROP TABLE IF EXISTS author_roles;


CREATE TABLE "onix" ( 
  "isbn" TEXT PRIMARY KEY, 
  "cover_front" TEXT, 
  "cover_back" TEXT, 
  "hoofdTitel_title" TEXT, 
  "hoofdTitel_subtitle" TEXT
);


CREATE TABLE "publication" (
  "ppn" TEXT PRIMARY KEY,
  "title" TEXT,
  "isbn" TEXT,

);

CREATE TABLE "NTA" ( 
  "editorial" TEXT, 
  "foaf_name" TEXT, 
  "foaf_givenname" TEXT, 
  "foaf_familyname" TEXT, 
  "birthyear" TEXT, 
  "deathyear" TEXT, 
  "related_entry" TEXT, 
  "viaf_link" TEXT, 
  "ppn" TEXT 
);


CREATE TABLE "authorship" (
  "authorshipID" INTEGER PRIMARY KEY AUTOINCREMENT, 
  "publication_ppn" TEXT,
  "publication_isbn" TEXT,
  "seq_nr" INTEGER,
  "author_ppn" TEXT,  
  "display_name" TEXT,
  "role" INTEGER,
  "source" TEXT,
  "created" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY ("author_ppn") REFERENCES contributor (ppn),
  FOREIGN KEY ("publication_ppn") REFERENCES publication (ppn),
  FOREIGN KEY ("publication_isbn") REFERENCES onix (isbn)
);

CREATE TABLE "author_roles" (
  "author_rolesID" INTEGER PRIMARY KEY, 
  "ggc_code" TEXT,
  "onix_code" TEXT,
  "legible" TEXT
);
  

