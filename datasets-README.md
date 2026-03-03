# LLM-SQL-PHC Benchmark Datasets

Source paper: *Optimizing LLM Queries in Relational Data Analytics Workloads*
(arXiv:2403.05821v2, April 2025) [[LLM-SQL](https://arxiv.org/abs/2403.05821)].
Section 6.1.1 lists 7 datasets used for evaluation.

## Dataset Summary (from Table 1)

| Name     | nrows | nfields | input avg tokens | Query Types |
|----------|------:|--------:|-----------------:|-------------|
| Movies   | 15000 |       8 |              276 | T1–T4       |
| Products | 14890 |       8 |              377 | T1–T4       |
| BIRD     | 14920 |       4 |              765 | T1, T2      |
| PDMX     | 10000 |      57 |              738 | T1, T2      |
| Beer     | 28479 |       8 |              156 | T1, T2      |
| SQuAD    | 22665 |       5 |             1047 | T5 (RAG)    |
| FEVER    | 19929 |       5 |             1302 | T5 (RAG)    |

## Download Status

| Dataset  | Downloaded | Processed file                               | Raw files                   | Notes                                            |
|----------|:----------:|----------------------------------------------|-----------------------------|--------------------------------------------------|
| Movies   |     ✅      | `movies/movies.jsonl` (11 MB, 15,000 rows)   | 2 CSVs (25 MB)              | Kaggle mirror; exact paper category              |
| Products |     ✅      | `amazon/products.jsonl` (15 MB, 14,890 rows) | 2 gz (128 MB)               | All_Beauty category; category unknown from paper |
| BIRD     |     ✅      | `bird/dev_20240627/` (dev set)               | `dev.zip` (330 MB)          | codebase_community DB is the paper's source      |
| PDMX     |     ✅      | `pdmx/pdmx.jsonl` (17 MB, 10,000 rows)       | `PDMX.csv` (215 MB)         | 55 of 57 fields; 5 fields not in new CSV version |
| Beer     |     ✅      | `beer/beer.jsonl` (7.6 MB, 28,479 rows)      | `ratebeer.json.gz` (380 MB) | Removed from SNAP; still on mcauleylab.ucsd.edu  |
| SQuAD    |     ✅      | `squad/train-v1.1.json` + `dev-v1.1.json`    | —                           | 87,599 + 10,570 Q&A pairs; CC BY-SA 4.0          |
| FEVER    |     ✅      | `fever/train.jsonl` + 3 split files          | —                           | 145,449 + 29,996 claims; CC BY-SA 3.0            |

All 7 datasets downloaded. The processed `.jsonl` files use the exact field
names from Appendix B of the paper, sampled to the paper's row counts where
applicable.

---

## 1. Movies — Rotten Tomatoes Movie Reviews

**Reference:** Pang & Lee (2005)
**Downloaded:** ✅ `movies/`

### Files
```
movies/
  rotten_tomatoes_movies.csv          16 MB   17,712 movies with metadata
  rotten_tomatoes_critic_reviews_50k.csv  8.5 MB  50,000 critic reviews
  movies.jsonl                        11 MB   15,000 rows (paper's count), 8 fields
```

### Source

The paper cites Pang & Lee (2005) but uses 15,000 rows with 8 fields
(`genres, movieinfo, movietitle, productioncompany, reviewcontent, reviewtype,
rottentomatoeslink, topcritic`) — far richer than the original 10,662-sentence
Cornell corpus. The actual dataset is the **stefanoleone992 Kaggle scrape** of
Rotten Tomatoes (Oct 2020), mirrored on GitHub.

- Kaggle
  original: https://www.kaggle.com/datasets/stefanoleone992/rotten-tomatoes-movies-and-critic-reviews-dataset
- GitHub mirror
  used: https://github.com/BRAMHOTRIPARIDA/Movies-Rating-Prediction-Rotten-Tomatoes

### Construction

`movies.jsonl` = join of `rotten_tomatoes_movies.csv` +
`rotten_tomatoes_critic_reviews_50k.csv`
on `rotten_tomatoes_link`, sampled to 15,000 rows (random seed 42). All 50,000
reviews joined successfully (0 missing movie matches).

### Stats
- 62% Fresh / 38% Rotten reviews
- 25% top critics, 75% regular critics
- ~290 tokens/row (paper: 276 ✓)

---

## 2. Products — Amazon Product Reviews

**Reference:** He & McAuley (2016)
**Downloaded:** ✅ `amazon/`

### Files
```
amazon/
  All_Beauty_reviews.jsonl.gz         90 MB   ~400K reviews (2023 format)
  All_Beauty_meta.jsonl.gz            38 MB   112,590 product metadata entries
  products.jsonl                      15 MB   14,890 rows, 8 fields
  Subscription_Boxes_reviews.jsonl.gz  2.6 MB  (kept; no usable descriptions)
  Subscription_Boxes_meta.jsonl.gz     276 KB
```

### Source

The paper uses `parent_asin` (a 2023-format field) and 8 fields
(`description, id, parent_asin, product_title, rating, review_title, text,
verified_purchase`). The exact category is not named in the paper.

`products.jsonl` uses the **All_Beauty** category from the Amazon Reviews 2023
dataset (McAuley Lab), filtered to reviews with non-empty product descriptions
and sampled to 14,890 rows (random seed 42).

- Source: https://mcauleylab.ucsd.edu/public_datasets/data/amazon_2023/raw/

### Stats
- 91% verified purchases
- ~372 tokens/row (paper: 377 ✓)
- 100% rows have non-empty `description`

### Caveat

The paper's exact category is undisclosed. No standard Amazon 2023 category has
exactly 14,890 rows. All_Beauty was chosen for description coverage and token
length match. The format and field names are correct regardless of category.

---

## 3. BIRD — Big Bench for Large-scale Database Grounded Text-to-SQL

**Reference:** Li et al. (2024)
**Downloaded:** ✅ `bird/`

### Files
```
bird/
  dev.zip                             330 MB  full dev set archive
  dev_20240627/
    dev.json                          724 KB  1,534 text-to-SQL questions
    dev_tables.json                   155 KB  schema definitions
    dev_databases/                           11 SQLite databases (unzipped)
      codebase_community/                    ← paper's source database
      california_schools/
      card_games/
      ... (8 more)
```

### Source
- Official: https://bird-bench.github.io/
- Download URL: `https://bird-bench.oss-cn-beijing.aliyuncs.com/dev.zip`

### The Paper's BIRD Rows

The paper footnote says: *"We use Posts and Comments table joined by PostID from
the BIRD dataset."* This is the `codebase_community` SQLite database (a Stack
Exchange-style Q&A corpus):

| Table                             |        Rows |
|-----------------------------------|------------:|
| posts                             |      91,966 |
| comments                          |     174,285 |
| **posts JOIN comments ON PostId** | **174,249** |

The paper's 14,920 rows is a filtered/sampled subset of this join.

### Fields (from Appendix B)

`Body, PostDate, PostId, Text` — 4 fields; FDs: `Body, PostId`

### Note

Train set (8.5 GB) not downloaded — dev set covers the paper's use case.

---

## 4. PDMX — Public Domain MusicXML

**Reference:** Long et al. (2024)
**Downloaded:** ✅ `pdmx/`

### Files
```
pdmx/
  PDMX.csv     215 MB  full metadata table (254,077 songs, 62 columns)
  pdmx.jsonl    17 MB  10,000 rows, 55 fields (paper's column names)
```

### Source
- Zenodo record 15571083 (newer split
  version): https://zenodo.org/records/15571083
- `PDMX.csv` downloaded directly as a standalone file — no need for the 1.6 GB
  full archive.
- GitHub: https://github.com/pnlong/PDMX

### Construction

`pdmx.jsonl` = 10,000 rows sampled from `PDMX.csv` (random seed 42), with CSV
columns renamed to match Appendix B field names (e.g. `song_length.bars` →
`songlengthbars`).

### Fields

55 of the paper's ~57 fields are present. Five fields from Appendix B
(`id, hasmetadata, postdate, postid, text`) do not appear in the newer CSV
version — they likely came from per-song JSON metadata files in the original
dataset version used by the paper.

### Stats
- 254,077 total songs in full CSV
- ~414 raw tokens/row before JSON prompt overhead (paper: 738 — gap partly
  because the missing 5 fields include longer text content)

---

## 5. Beer — RateBeer Reviews

**Reference:** McAuley et al. (2012)
**Downloaded:** ✅ `beer/`

### Files
```
beer/
  ratebeer.json.gz   380 MB  full RateBeer corpus (2,924,164 reviews)
  beer.jsonl           7.6 MB  28,479 rows, 9 fields (paper's column names)
```

### Source

Despite the SNAP page showing a takedown notice, the McAuley lab's own server
still hosts the original dataset:

- **Direct URL:**
  `https://mcauleylab.ucsd.edu/public_datasets/data/beer/ratebeer.json.gz`
- SNAP page (takedown notice): https://snap.stanford.edu/data/web-RateBeer.html

### Format

Raw file uses Python-dict strings (single-quoted), one record per line. Parse
with `ast.literal_eval`. All 2,924,164 records parsed without error.

### Construction

`beer.jsonl` = 28,479 rows sampled from the full corpus (random seed 42),
keeping the 9 fields from Appendix B:
`beer/beerId, beer/name, beer/style, review/appearance, review/overall,
review/palate, review/profileName, review/taste, review/time`

### Stats
- 2,924,164 total reviews in raw file
- Top styles: IPA, Pale Lager, Belgian Strong Ale, Imperial Stout
- ~116 tokens/row (paper: 156 — gap because `review/text` is excluded per
  Appendix B field list, though it exists in the raw data)

---

## 6. SQuAD — Stanford Question Answering Dataset

**Reference:** Rajpurkar et al. (2016)
**Downloaded:** ✅ `squad/`

### Files
```
squad/
  train-v1.1.json   29 MB   442 articles, 87,599 Q&A pairs
  dev-v1.1.json      4.6 MB   48 articles, 10,570 Q&A pairs
```

### Source
- Official: https://rajpurkar.github.io/SQuAD-explorer/
- Direct download URLs:
  - `https://rajpurkar.github.io/SQuAD-explorer/dataset/train-v1.1.json`
  - `https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v1.1.json`
- License: CC BY-SA 4.0

### Fields (from Appendix B)

`question, context1, context2, context3, context4, context5` — 5 fields; FDs:
none

The paper uses RAG (T5 queries): for each question, 5 contexts are retrieved via
FAISS similarity search over the Wikipedia passages. The raw SQuAD files contain
the passages; contexts are populated at query time.

### Note

The paper uses 22,665 rows. SQuAD 1.1 train has 87,599 Q&A pairs — the paper
likely uses a subset or flattened/deduped version. No pre-built `squad.jsonl`
created since context retrieval requires the embedding + FAISS step.

---

## 7. FEVER — Fact Extraction and VERification

**Reference:** Thorne et al. (2018)
**Downloaded:** ✅ `fever/`

### Files
```
fever/
  train.jsonl            31 MB   145,449 claims
  shared_task_dev.jsonl   4.1 MB   19,998 claims (labelled)
  paper_dev.jsonl         2.1 MB    9,999 claims
  paper_test.jsonl        2.1 MB    9,999 claims
```

### Source
- Official: https://fever.ai/dataset/fever.html
- Direct download: `https://fever.ai/download/fever/<filename>`
- License: CC BY-SA 3.0

### Fields (from Appendix B)

`claim, evidence1, evidence2, evidence3, evidence4` — 5 fields; FDs: none

Like SQuAD, evidence fields are populated at query time via RAG (k=4 contexts
retrieved per claim). The raw JSONL files contain `claim` + `evidence` (a nested
list of Wikipedia sentence references).

### Stats
- Labels: Supported / Refuted / NotEnoughInfo
- Keys per record: `id, verifiable, label, claim, evidence`
- `wiki-pages.zip` (Wikipedia dump) not downloaded — needed only for RAG
  retrieval

---

## Accessibility Summary

| Dataset  | Status      | Downloaded                | License / Access                         |
|----------|-------------|---------------------------|------------------------------------------|
| Movies   | ✅ Available | ✅ `movies/movies.jsonl`   | Free (Kaggle / GitHub mirror)            |
| Products | ✅ Available | ✅ `amazon/products.jsonl` | Free (McAuley Lab 2023, direct download) |
| BIRD     | ✅ Available | ✅ `bird/dev_20240627/`    | Free (bird-bench.github.io)              |
| PDMX     | ✅ Available | ✅ `pdmx/pdmx.jsonl`       | Open access (Zenodo CC)                  |
| Beer     | ✅ Available | ✅ `beer/beer.jsonl`       | Free (mcauleylab.ucsd.edu, SNAP removed) |
| SQuAD    | ✅ Available | ✅ `squad/train-v1.1.json` | CC BY-SA 4.0 (Stanford official)         |
| FEVER    | ✅ Available | ✅ `fever/train.jsonl`     | CC BY-SA 3.0 (fever.ai official)         |

**All 7 datasets successfully downloaded.** The earlier note about RateBeer
being unavailable is superseded — the McAuley lab server still hosts it directly
despite the SNAP takedown.
