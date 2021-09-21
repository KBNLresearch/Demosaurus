BEGIN TRANSACTION;
CREATE VIRTUAL TABLE author_fts5 USING FTS5(author_ppn, foaf_name);
CREATE TABLE IF NOT EXISTS "publication_basicinfo" (
	"publication_ppn"	TEXT NOT NULL,
	"titelvermelding"	TEXT,
	"verantwoordelijkheidsvermelding"	TEXT,
	"taal_publicatie"	TEXT,
	"taal_origineel"	TEXT,
	"land_van_uitgave"	TEXT,
	"isbn"	INTEGER,
	"isbn_2"	INTEGER,
	"jaar_van_uitgave"	INTEGER,
	"uitgever"	TEXT,
	"uitgever_2"	TEXT,
	PRIMARY KEY("publication_ppn")
);
CREATE TABLE IF NOT EXISTS "publication_inhoud" (
	"publication_ppn"	TEXT,
	"inhoud"	TEXT
);
CREATE TABLE IF NOT EXISTS "similarity_training" (
	"publication_ppn"	INTEGER,
	"age_when_published"	TEXT,
	"last_name"	TEXT,
	"target"	REAL,
	"author_ppn"	TEXT,
	"datasplit"	TEXT,
	"genres_similarity"	REAL,
	"NUR_rubriek_similarity"	REAL,
	"NUGI_genre_similarity"	REAL,
	"uitgever_2_agg_similarity"	REAL,
	"uitgever_agg_similarity"	REAL,
	"jaar_van_uitgave_similarity"	REAL,
	"number_of_authors_similarity"	REAL,
	"number_of_words_in_titelvermelding_similarity"	REAL,
	"land_van_uitgave_similarity"	REAL,
	"taal_origineel_similarity"	REAL,
	"taal_publicatie_similarity"	REAL,
	"themas_similarity"	REAL,
	"role_imp_similarity"	REAL,
	"median_wordlength_titelvermelding_similarity"	REAL,
	"mean_wordlength_titelvermelding_similarity"	REAL,
	"length_titelvermelding_ranges_similarity"	REAL,
	"inhoud_similarity"	REAL,
	"title_similarity"	REAL,
	"inhoud_w2vsim"	REAL,
	"autobiography_w2vsim"	REAL
);
CREATE TABLE IF NOT EXISTS "publication_titlefeatures" (
	"publication_ppn"	TEXT NOT NULL,
	"titelvermelding"	TEXT,
	"titellengte"	INTEGER,
	"titellengte_ranges"	TEXT,
	"titelwoorden"	TEXT,
	"titellengte_Nwoorden"	INTEGER,
	"woordlengte_gem"	REAL,
	"woordlengte_gem_rond"	REAL,
	"woordlengte_med"	REAL,
	PRIMARY KEY("publication_ppn")
);
CREATE TABLE IF NOT EXISTS "publication_annotations" (
	"publication_ppn"	TEXT NOT NULL,
	"annotation"	TEXT,
	"kind"	TEXT
);
CREATE TABLE IF NOT EXISTS "publication_datasplits" (
	"publication_ppn"	TEXT NOT NULL,
	"datasplit"	TEXT,
	PRIMARY KEY("publication_ppn")
);
CREATE TABLE IF NOT EXISTS "authorship_ggc" (
	"publication_ppn"	TEXT NOT NULL,
	"kmc"	INTEGER NOT NULL,
	"title"	TEXT,
	"name"	TEXT,
	"role"	TEXT,
	"author_ppn"	TEXT
);
CREATE TABLE IF NOT EXISTS "thesaurus_brinkmantrefwoorden" (
	"ppn"	TEXT NOT NULL,
	"term"	TEXT,
	"kind"	TEXT
);
CREATE TABLE IF NOT EXISTS "thesaurus_CBK_genres" (
	"identifier"	TEXT NOT NULL,
	"genre"	TEXT,
	PRIMARY KEY("identifier")
);
CREATE TABLE IF NOT EXISTS "publication_CBK_genre" (
	"publication_ppn"	TEXT NOT NULL,
	"CBK_genre"	TEXT,
	"rank"	INTEGER
);
CREATE TABLE IF NOT EXISTS "author_wikipedia" (
	"author_ppn"	TEXT NOT NULL,
	"wikidata_id"	TEXT,
	"wiki_url"	TEXT,
	"language"	TEXT
);
CREATE TABLE IF NOT EXISTS "author_viaf" (
	"author_ppn"	TEXT NOT NULL,
	"identifier"	TEXT
);
CREATE TABLE IF NOT EXISTS "author_isni" (
	"author_ppn"	TEXT NOT NULL,
	"identifier"	TEXT
);
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
CREATE TABLE IF NOT EXISTS "authorship_roles" (
	"authorship_roles_ID"	INTEGER NOT NULL,
	"ggc_code"	TEXT,
	"onix_code"	TEXT,
	"legible"	TEXT,
	PRIMARY KEY("authorship_roles_ID")
);
CREATE TABLE IF NOT EXISTS "wiki_preferred_languages" (
	"language"	TEXT NOT NULL,
	"rank"	INTEGER,
	PRIMARY KEY("language")
);
CREATE TABLE IF NOT EXISTS "author_worldcat" (
	"author_ppn"	TEXT NOT NULL,
	"identifier"	TEXT
);
CREATE TABLE IF NOT EXISTS "publication_NUR_rubriek" (
	"publication_ppn"	TEXT NOT NULL,
	"NUR_rubriek"	TEXT,
	PRIMARY KEY("publication_ppn")
);
CREATE TABLE IF NOT EXISTS "publication_NUGI_genre" (
	"publication_ppn"	TEXT NOT NULL,
	"NUGI_genre"	TEXT,
	PRIMARY KEY("publication_ppn")
);
CREATE TABLE IF NOT EXISTS "publication_CBK_thema" (
	"publication_ppn"	TEXT NOT NULL,
	"CBK_thema"	TEXT,
	"rank"	INTEGER
);
CREATE TABLE IF NOT EXISTS "publication_brinkman" (
	"publication_ppn"	TEXT NOT NULL,
	"brinkman"	TEXT,
	"rank"	INTEGER
);
CREATE INDEX IF NOT EXISTS "author_NTA_foaf_name" ON "author_NTA" (
	"foaf_name"
);
CREATE INDEX IF NOT EXISTS "authorship_ggc_publication_ppn" ON "authorship_ggc" (
	"publication_ppn"
);
CREATE INDEX IF NOT EXISTS "authorship_ggc_author_ppn" ON "authorship_ggc" (
	"author_ppn"
);
CREATE VIEW author_jaar_van_uitgaves AS 
SELECT author_ppn, jaar_van_uitgave, COUNT(authorship_ggc.publication_ppn) AS nPublications 
FROM authorship_ggc
JOIN publication_datasplits ON publication_datasplits.publication_ppn = authorship_ggc.publication_ppn
JOIN publication_basicinfo AS tt ON tt.publication_ppn = authorship_ggc.publication_ppn
WHERE publication_datasplits.datasplit like "train"
AND author_ppn IS NOT NULL
AND jaar_van_uitgave IS NOT NULL
GROUP BY author_ppn, jaar_van_uitgave;
CREATE VIEW author_brinkmans AS 
SELECT author_ppn, brinkman, COUNT(authorship_ggc.publication_ppn) AS nPublications 
FROM authorship_ggc
JOIN publication_datasplits ON publication_datasplits.publication_ppn = authorship_ggc.publication_ppn
JOIN publication_brinkman AS tt ON tt.publication_ppn = authorship_ggc.publication_ppn
WHERE publication_datasplits.datasplit like "train"
AND author_ppn IS NOT NULL
AND brinkman IS NOT NULL
GROUP BY author_ppn, brinkman;
CREATE VIEW author_NUR_rubrieks AS 
SELECT author_ppn, NUR_rubriek, COUNT(authorship_ggc.publication_ppn) AS nPublications 
FROM authorship_ggc
JOIN publication_datasplits ON publication_datasplits.publication_ppn = authorship_ggc.publication_ppn
JOIN publication_NUR_rubriek AS tt ON tt.publication_ppn = authorship_ggc.publication_ppn
WHERE publication_datasplits.datasplit like "train"
AND author_ppn IS NOT NULL
AND NUR_rubriek IS NOT NULL
GROUP BY author_ppn, NUR_rubriek;
CREATE VIEW author_NUGI_genres AS 
SELECT author_ppn, NUGI_genre, COUNT(authorship_ggc.publication_ppn) AS nPublications 
FROM authorship_ggc
JOIN publication_datasplits ON publication_datasplits.publication_ppn = authorship_ggc.publication_ppn
JOIN publication_NUGI_genre AS tt ON tt.publication_ppn = authorship_ggc.publication_ppn
WHERE publication_datasplits.datasplit like "train"
AND author_ppn IS NOT NULL
AND NUGI_genre IS NOT NULL
GROUP BY author_ppn, NUGI_genre;
CREATE VIEW author_CBK_themas AS 
SELECT author_ppn, CBK_thema, COUNT(authorship_ggc.publication_ppn) AS nPublications 
FROM authorship_ggc
JOIN publication_datasplits ON publication_datasplits.publication_ppn = authorship_ggc.publication_ppn
JOIN publication_CBK_thema AS tt ON tt.publication_ppn = authorship_ggc.publication_ppn
WHERE publication_datasplits.datasplit like "train"
AND author_ppn IS NOT NULL
AND CBK_thema IS NOT NULL
GROUP BY author_ppn, CBK_thema;
CREATE VIEW author_CBK_genres AS 
SELECT author_ppn, CBK_genre, COUNT(authorship_ggc.publication_ppn) AS nPublications 
FROM authorship_ggc
JOIN publication_datasplits ON publication_datasplits.publication_ppn = authorship_ggc.publication_ppn
JOIN publication_CBK_genre AS tt ON tt.publication_ppn = authorship_ggc.publication_ppn
WHERE publication_datasplits.datasplit like "train"
AND author_ppn IS NOT NULL
AND CBK_genre IS NOT NULL
GROUP BY author_ppn, CBK_genre;
CREATE VIEW authorship_ggc_test AS 
SELECT authorship_ggc.* FROM authorship_ggc JOIN publication_datasplits
ON authorship_ggc.publication_ppn = publication_datasplits.publication_ppn
WHERE datasplit LIKE"test";
CREATE VIEW authorship_ggc_train AS 
SELECT authorship_ggc.* FROM authorship_ggc JOIN publication_datasplits
ON authorship_ggc.publication_ppn = publication_datasplits.publication_ppn
WHERE datasplit LIKE"train";
COMMIT;
