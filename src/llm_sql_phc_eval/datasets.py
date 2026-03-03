import json
import sqlite3
from pathlib import Path

import pandas as pd


def load_jsonl(path):
    """Load a .jsonl file into a DataFrame."""
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return pd.DataFrame(records)


def load_datasets(data_dir):
    """Load all 7 benchmark datasets from data_dir and return them as a dict.

    Parameters
    ----------
    data_dir : str or Path
        Root directory containing the dataset subdirectories.

    Returns
    -------
    dict[str, pd.DataFrame]
        Keys: Movies, Products, Beer, PDMX, FEVER, SQuAD, BIRD.
    """
    data_dir = Path(data_dir)

    movies   = load_jsonl(data_dir / "movies/movies.jsonl")
    products = load_jsonl(data_dir / "amazon/products.jsonl")
    beer     = load_jsonl(data_dir / "beer/beer.jsonl")
    pdmx     = load_jsonl(data_dir / "pdmx/pdmx.jsonl")
    fever    = load_jsonl(data_dir / "fever/train.jsonl")

    # SQuAD has nested structure — flatten to (question, context-passage) pairs
    with open(data_dir / "squad/train-v1.1.json") as f:
        squad_raw = json.load(f)
    squad_rows = [
        {"question": qa["question"],
         "context":  para["context"],
         "answer":   qa["answers"][0]["text"] if qa["answers"] else ""}
        for article in squad_raw["data"]
        for para in article["paragraphs"]
        for qa in para["qas"]
    ]
    squad = pd.DataFrame(squad_rows)

    # BIRD — load Posts JOIN Comments from codebase_community SQLite
    # Note: 'CreaionDate' is the actual column name in the DB (typo in original data)
    bird_db = (data_dir /
               "bird/dev_20240627/dev_databases/codebase_community/codebase_community.sqlite")
    with sqlite3.connect(bird_db) as con:
        bird = pd.read_sql_query(
            "SELECT p.Body, p.Id AS PostId, p.CreaionDate AS PostDate, c.Text "
            "FROM posts p JOIN comments c ON c.PostId = p.Id "
            "LIMIT 15000",   # paper uses 14,920; limit for speed
            con
        )

    return {
        "Movies":   movies,
        "Products": products,
        "Beer":     beer,
        "PDMX":     pdmx,
        "FEVER":    fever,
        "SQuAD":    squad,
        "BIRD":     bird,
    }
