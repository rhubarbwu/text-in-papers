import argparse
import re
from os import path
from typing import List

import pandas as pd

from iclr2023_stats.py_src.funcs import DataBase

TABLE_NAME = "submissions"
AND, OR = "&", "|"


parser = argparse.ArgumentParser()
parser.add_argument(
    "-db",
    "--database_path",
    type=str,
    default="iclr2023_stats/assets/iclr2023.db",
    help="path to database file",
)
parser.add_argument(
    "-io",
    "--io_path",
    type=str,
    default="queries.csv",
    help="path to load from and update queries",
)
parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
)
args = parser.parse_args()

db = DataBase(args.database_path)
db.initialize(create=False)


cursor = db.database.cursor()
cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
column_names = [col[1] for col in cursor.fetchall()]


def fetch_column(col_name: str = "url_id", withdraw: bool = False) -> List[str]:
    _cmd = f"SELECT {col_name} FROM submissions WHERE withdraw == {withdraw};"
    db.cursor.execute(_cmd)
    values = [val[0] for val in db.cursor.fetchall()]

    return values


if path.exists(args.io_path):
    df = pd.read_csv(args.io_path, sep=":")
else:
    df = pd.DataFrame({"query_id": [], "patterns": [], "paper_ids": []})
df["paper_ids"] = df["paper_ids"].astype(str)


def query_for_paper(
    query_patterns: list, query_type: str = AND, verbose: bool = False
) -> List[str]:
    query_patterns = set(patt.lower() for patt in query_patterns)

    paper_ids = fetch_column("url_id")
    keywords_sets = fetch_column("keywords")

    filtered_ids = []
    for paper_id, kw_set in zip(paper_ids, keywords_sets):
        kw_set_sub = [kw.lower() for kw in re.split(", | ", kw_set)]
        if query_type == AND and query_patterns.issubset(kw_set_sub):
            if verbose:
                print("-----")
                print(paper_id, kw_set, kw_set_sub)
            filtered_ids.append(paper_id)
        if query_type == OR and any(kw in query_patterns for kw in kw_set_sub):
            if verbose:
                print("-----")
                print(paper_id, kw_set, kw_set_sub)
            filtered_ids.append(paper_id)

    return filtered_ids


for idx, row in df.iterrows():
    TYPE = AND if AND in row["patterns"] else OR
    query_id = row["query_id"]
    patterns = row["patterns"].split(TYPE)
    paper_ids = query_for_paper(patterns, TYPE)
    joined_ids = ",".join(paper_ids)
    df["paper_ids"][idx] = joined_ids

    print(f"{query_id} ({len(paper_ids)}): {patterns}")

df.to_csv(args.io_path, sep=":", index=False)
