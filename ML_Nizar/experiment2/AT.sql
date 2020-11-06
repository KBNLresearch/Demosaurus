WITH link AS (
    SELECT publication_ppn,
    author_NTA.foaf_familyname AS last_name,
    authorship_ggc.author_ppn,
    "role",
    kind,
    rank  
    FROM authorship_ggc
	LEFT JOIN author_NTA
	on authorship_ggc.author_ppn = author_NTA.author_ppn
    WHERE authorship_ggc.kind LIKE 'primair'
),
ppns AS (SELECT DISTINCT author_ppn FROM author_embeddings),
subset_nta AS (
    SELECT *
    FROM ppns LEFT JOIN author_NTA
    ON ppns.author_ppn = author_NTA.author_ppn)

SELECT
    publication_basicinfo.publication_ppn,
    publication_basicinfo.titelvermelding,
	publication_basicinfo.jaar_van_uitgave,
	publication_basicinfo.land_van_uitgave,
	publication_basicinfo.taal_origineel,
	publication_basicinfo.taal_publicatie,
	publication_basicinfo.uitgever_agg,
	publication_basicinfo.uitgever_2_agg,
	publication_basicinfo.number_of_authors,
	publication_basicinfo.length_of_titelvermelding,
	publication_basicinfo.number_of_words_in_titelvermelding,
	ppn_genrelist.genres,
	ppn_themalist.themas,
	publication_NUR_rubriek.NUR_rubriek,
	publication_NUGI_genre.NUGI_genre,
    cast(REPLACE(jaar_van_uitgave, 'X', '5') AS integer) - cast(REPLACE(subset_nta.birthyear, 'X', '5') AS integer) AS age_when_published,
    subset_nta.editorial,
    subset_nta.editorial_nl,
    link.last_name,                                 -- used for linking
    link.author_ppn = subset_nta.author_ppn AS target,     -- training/ test signal
    subset_nta.author_ppn,                    -- ppn only for reference
	publication_sets.datasplit
    FROM publication_basicinfo
    LEFT JOIN link
    ON publication_basicinfo.publication_ppn = link.publication_ppn
	LEFT JOIN ppn_themalist
	ON publication_basicinfo.publication_ppn = ppn_themalist.publication_ppn
	LEFT JOIN ppn_genrelist
	ON publication_basicinfo.publication_ppn = ppn_genrelist.publication_ppn
	LEFT JOIN publication_NUR_rubriek
	ON publication_basicinfo.publication_ppn = publication_NUR_rubriek.publication_ppn
	LEFT JOIN publication_NUGI_genre
	ON publication_basicinfo.publication_ppn = publication_NUGI_genre.publication_ppn
	LEFT JOIN publication_sets
	ON publication_basicinfo.publication_ppn = publication_sets.publication_ppn
    LEFT JOIN subset_nta
    ON link.last_name LIKE subset_nta.foaf_familyname
