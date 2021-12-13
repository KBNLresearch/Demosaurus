BEGIN TRANSACTION;
DROP TABLE IF EXISTS "publication_datasplits";
CREATE TABLE IF NOT EXISTS "publication_datasplits" (
	"publication_ppn"	TEXT NOT NULL,
	"dataset_id"	INTEGER,
	"datasplit_id"	INTEGER
);
DROP TABLE IF EXISTS "author_fts5_config";
CREATE TABLE IF NOT EXISTS "author_fts5_config" (
	"k"	TEXT,
	"v"	TEXT,
	PRIMARY KEY("k")
) WITHOUT ROWID;
DROP TABLE IF EXISTS "author_fts5_docsize";
CREATE TABLE IF NOT EXISTS "author_fts5_docsize" (
	"id"	INTEGER,
	"sz"	BLOB,
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "author_fts5_content";
CREATE TABLE IF NOT EXISTS "author_fts5_content" (
	"id"	INTEGER,
	"c0"	TEXT,
	"c1"	TEXT,
	"c2"	TEXT,
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "author_fts5_idx";
CREATE TABLE IF NOT EXISTS "author_fts5_idx" (
	"segid"	TEXT,
	"term"	TEXT,
	"pgno"	TEXT,
	PRIMARY KEY("segid","term")
) WITHOUT ROWID;
DROP TABLE IF EXISTS "author_fts5_data";
CREATE TABLE IF NOT EXISTS "author_fts5_data" (
	"id"	INTEGER,
	"block"	BLOB,
	PRIMARY KEY("id")
);
DROP TABLE IF EXISTS "author_fts5";
CREATE VIRTUAL TABLE author_fts5 USING FTS5(author_ppn, foaf_name, skos_preflabel);
DROP TABLE IF EXISTS "thesaurus_brinkmantrefwoorden";
CREATE TABLE IF NOT EXISTS "thesaurus_brinkmantrefwoorden" (
	"identifier"	TEXT NOT NULL,
	"term"	TEXT,
	"brinkman_kind_id"	NUMERIC NOT NULL,
	PRIMARY KEY("identifier")
);
DROP TABLE IF EXISTS "thesaurus_brinkman_kinds";
CREATE TABLE IF NOT EXISTS "thesaurus_brinkman_kinds" (
	"brinkman_kind_id"	NUMERIC NOT NULL,
	"brinkman_kind"	TEXT,
	PRIMARY KEY("brinkman_kind_id")
);
DROP TABLE IF EXISTS "thesaurus_CBK_genres";
CREATE TABLE IF NOT EXISTS "thesaurus_CBK_genres" (
	"identifier"	TEXT NOT NULL,
	"term"	TEXT,
	PRIMARY KEY("identifier")
);
DROP TABLE IF EXISTS "datasplits";
CREATE TABLE IF NOT EXISTS "datasplits" (
	"datasplit_id"	INTEGER NOT NULL,
	"datasplit"	TEXT NOT NULL,
	PRIMARY KEY("datasplit_id")
);
DROP TABLE IF EXISTS "datasets";
CREATE TABLE IF NOT EXISTS "datasets" (
	"dataset_id"	INTEGER NOT NULL,
	"dataset"	TEXT NOT NULL,
	PRIMARY KEY("dataset_id")
);
DROP TABLE IF EXISTS "publication_contributors";
CREATE TABLE IF NOT EXISTS "publication_contributors" (
	"publication_ppn"	TEXT NOT NULL,
	"rank"	INTEGER NOT NULL,
	"title"	TEXT,
	"firstname"	TEXT,
	"prefix"	TEXT,
	"familyname"	TEXT,
	"role"	TEXT,
	"author_ppn"	TEXT
);
DROP TABLE IF EXISTS "authorship_roles";
CREATE TABLE IF NOT EXISTS "authorship_roles" (
	"authorship_roles_ID"	INTEGER NOT NULL,
	"ggc_code"	TEXT,
	"onix_code"	TEXT,
	"legible"	TEXT,
	PRIMARY KEY("authorship_roles_ID")
);
DROP TABLE IF EXISTS "wiki_preferred_languages";
CREATE TABLE IF NOT EXISTS "wiki_preferred_languages" (
	"language"	TEXT NOT NULL,
	"rank"	INTEGER,
	PRIMARY KEY("language")
);
DROP TABLE IF EXISTS "author_wikipedia";
CREATE TABLE IF NOT EXISTS "author_wikipedia" (
	"author_ppn"	TEXT NOT NULL,
	"wikidata_id"	TEXT,
	"wiki_url"	TEXT,
	"language"	TEXT
);
DROP TABLE IF EXISTS "author_worldcat";
CREATE TABLE IF NOT EXISTS "author_worldcat" (
	"author_ppn"	TEXT NOT NULL,
	"identifier"	TEXT
);
DROP TABLE IF EXISTS "author_viaf";
CREATE TABLE IF NOT EXISTS "author_viaf" (
	"author_ppn"	TEXT NOT NULL,
	"identifier"	TEXT
);
DROP TABLE IF EXISTS "author_isni";
CREATE TABLE IF NOT EXISTS "author_isni" (
	"author_ppn"	TEXT NOT NULL,
	"identifier"	TEXT
);
DROP TABLE IF EXISTS "author_NTA";
CREATE TABLE IF NOT EXISTS "author_NTA" (
	"author_ppn"	TEXT NOT NULL,
	"foaf_name"	TEXT,
	"foaf_givenname"	TEXT,
	"foaf_familyname"	TEXT,
	"skos_preflabel"	TEXT,
	"birthyear"	TEXT,
	"deathyear"	TEXT,
	"editorial"	TEXT,
	"editorial_nl"	TEXT,
	"skopenote_nl"	TEXT,
	"related_entry_ppn"	TEXT,
	PRIMARY KEY("author_ppn")
);
DROP TABLE IF EXISTS "publication_NUR_rubriek";
CREATE TABLE IF NOT EXISTS "publication_NUR_rubriek" (
	"publication_ppn"	TEXT NOT NULL,
	"term_identifier"	INTEGER,
	PRIMARY KEY("publication_ppn")
);
DROP TABLE IF EXISTS "publication_NUGI_genre";
CREATE TABLE IF NOT EXISTS "publication_NUGI_genre" (
	"publication_ppn"	TEXT NOT NULL,
	"term_identifier"	INTEGER,
	PRIMARY KEY("publication_ppn")
);
DROP TABLE IF EXISTS "publication_brinkman";
CREATE TABLE IF NOT EXISTS "publication_brinkman" (
	"publication_ppn"	TEXT NOT NULL,
	"term_identifier"	TEXT NOT NULL,
	"rank"	INTEGER
);
DROP TABLE IF EXISTS "publication_CBK_genre";
CREATE TABLE IF NOT EXISTS "publication_CBK_genre" (
	"publication_ppn"	TEXT NOT NULL,
	"term_identifier"	TEXT NOT NULL,
	"rank"	INTEGER
);
DROP TABLE IF EXISTS "publication_CBK_thema";
CREATE TABLE IF NOT EXISTS "publication_CBK_thema" (
	"publication_ppn"	TEXT NOT NULL,
	"term"	TEXT,
	"rank"	INTEGER
);
DROP TABLE IF EXISTS "publication_annotations";
CREATE TABLE IF NOT EXISTS "publication_annotations" (
	"publication_ppn"	TEXT NOT NULL,
	"annotation"	TEXT,
	"kind"	TEXT
);
DROP TABLE IF EXISTS "publication_koepeltitel";
CREATE TABLE IF NOT EXISTS "publication_koepeltitel" (
	"publication_ppn"	TEXT NOT NULL,
	"koepel_ppn"	TEXT NOT NULL
);
DROP TABLE IF EXISTS "publication_basicinfo";
CREATE TABLE IF NOT EXISTS "publication_basicinfo" (
	"publication_ppn"	TEXT NOT NULL,
	"isbn"	TEXT,
	"titelvermelding"	TEXT,
	"verantwoordelijkheidsvermelding"	TEXT,
	"taal_publicatie"	TEXT,
	"taal_origineel"	TEXT,
	"land_van_uitgave"	TEXT,
	"jaar_van_uitgave"	INTEGER,
	"uitgever"	TEXT,
	"uitgever_plaats"	TEXT,
	PRIMARY KEY("publication_ppn")
);
DROP VIEW IF EXISTS "author_brinkman_zaak_NBD";
CREATE VIEW author_brinkman_zaak_NBD AS 
SELECT author_ppn, term_identifier, COUNT(t1.publication_ppn) AS nPublications 
FROM publication_contributors_train_NBD t1
JOIN publication_brinkman t2 ON t2.publication_ppn = t1.publication_ppn
JOIN thesaurus_brinkmantrefwoorden ON thesaurus_brinkmantrefwoorden.identifier = t2.term_identifier
WHERE author_ppn IS NOT NULL
AND t2.term_identifier IS NOT NULL
AND thesaurus_brinkmantrefwoorden.brinkman_kind_id=1
GROUP BY author_ppn, term_identifier;
DROP VIEW IF EXISTS "author_brinkman_vorm_NBD";
CREATE VIEW author_brinkman_vorm_NBD AS 
SELECT author_ppn, term_identifier, COUNT(t1.publication_ppn) AS nPublications 
FROM publication_contributors_train_NBD t1
JOIN publication_brinkman t2 ON t2.publication_ppn = t1.publication_ppn
JOIN thesaurus_brinkmantrefwoorden ON thesaurus_brinkmantrefwoorden.identifier = t2.term_identifier
WHERE author_ppn IS NOT NULL
AND t2.term_identifier IS NOT NULL
AND thesaurus_brinkmantrefwoorden.brinkman_kind_id=0
GROUP BY author_ppn, term_identifier;
DROP VIEW IF EXISTS "author_NUR_rubriek_NBD";
CREATE VIEW author_NUR_rubriek_NBD AS 
SELECT author_ppn, term_identifier, COUNT(t1.publication_ppn) AS nPublications 
FROM publication_contributors_train_NBD t1
JOIN publication_NUR_rubriek t2 ON t2.publication_ppn = t1.publication_ppn
WHERE author_ppn IS NOT NULL
AND t2.term_identifier IS NOT NULL
GROUP BY author_ppn, term_identifier;
DROP VIEW IF EXISTS "author_NUGI_genre_NBD";
CREATE VIEW author_NUGI_genre_NBD AS 
SELECT author_ppn, term_identifier, COUNT(t1.publication_ppn) AS nPublications 
FROM publication_contributors_train_NBD t1
JOIN publication_NUGI_genre t2 ON t2.publication_ppn = t1.publication_ppn
WHERE author_ppn IS NOT NULL
AND t2.term_identifier IS NOT NULL
GROUP BY author_ppn, term_identifier;
DROP VIEW IF EXISTS "author_CBK_genre_NBD";
CREATE VIEW author_CBK_genre_NBD AS 
SELECT author_ppn, term_identifier, COUNT(t1.publication_ppn) AS nPublications 
FROM publication_contributors_train_NBD t1
JOIN publication_CBK_genre t2 ON t2.publication_ppn = t1.publication_ppn
WHERE author_ppn IS NOT NULL
AND t2.term_identifier IS NOT NULL
GROUP BY author_ppn, term_identifier;
DROP VIEW IF EXISTS "publication_contributors_test_NBD";
CREATE VIEW publication_contributors_test_NBD AS 
SELECT t1.* FROM publication_contributors t1
JOIN publication_datasplits t2 ON t1.publication_ppn = t2.publication_ppn
 JOIN datasplits ON datasplits.datasplit_id = t2.datasplit_id
 JOIN datasets ON datasets.dataset_id = t2.dataset_id
WHERE datasplit LIKE "test";
DROP VIEW IF EXISTS "publication_contributors_train_NBD";
CREATE VIEW publication_contributors_train_NBD AS 
SELECT t1.* FROM publication_contributors t1
JOIN publication_datasplits t2 ON t1.publication_ppn = t2.publication_ppn
 JOIN datasplits ON datasplits.datasplit_id = t2.datasplit_id
 JOIN datasets ON datasets.dataset_id = t2.dataset_id
WHERE datasplit LIKE "train";
COMMIT;
