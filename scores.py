import argparse
from typing import List

import h5py
import numpy as np
from tqdm import tqdm

from iclr2023_stats.py_src.funcs import DataBase
from lib.records import commit

TABLE_NAME = "submissions"

parser = argparse.ArgumentParser()
parser.add_argument(
    "-db",
    type=str,
    default="iclr2023_stats/assets/iclr2023.db",
    help="path to database file",
)
parser.add_argument(
    "-rev",
    "--review",
    type=int,
    default=-1,
    help="index of review whose scores want",
)
parser.add_argument(
    "-nproc",
    type=int,
    default=None,
    help="number of processor for multiprocessing, default as maximum processor available",
)
parser.add_argument(
    "records_file",
    type=str,
    help="path to input file",
)
args = parser.parse_args()


db = DataBase(args.db)
db.initialize(create=False)


cursor = db.database.cursor()
cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
column_names = [col[1] for col in cursor.fetchall()]


def fetch_column_vals(col_name: str = "url_id", withdraw: bool = False) -> List[str]:
    _cmd = f"SELECT {col_name} FROM submissions WHERE withdraw == {withdraw};"
    db.cursor.execute(_cmd)
    values = [val[0] for val in db.cursor.fetchall()]

    return values


def fetch_ratings(
    rev_idx: int = 0, withdraw: bool = False, paper_id: str = None
) -> np.array:
    if rev_idx < 0:
        rev_idx = 0
        while f"s_{rev_idx+1}_cnt" in column_names:
            rev_idx += 1

    _cmd = f"SELECT s_{rev_idx}_avg FROM submissions WHERE withdraw == {withdraw};"
    if paper_id is not None:
        _cmd = _cmd.replace(";", f' AND url_id == "{paper_id}";')

    db.cursor.execute(_cmd)
    data = db.cursor.fetchall()
    act_avgs = np.array(data)
    if len(act_avgs) > 1:
        print(f"review {rev_idx}: {len(data)} submissions")
        print(f"    Average ratings: {act_avgs.mean():.2f}")
        print(f"    Max ratings: {act_avgs.max():.2f}")
        print(f"    Min ratings: {act_avgs.min():.2f}")

    return act_avgs.squeeze()


file = h5py.File(args.records_file, "r")
for col in file:
    print(file[col])
KEYS = list(file["n_figs"].keys())
file.close()


for paper_id in tqdm(KEYS, ncols=79):
    rating = fetch_ratings(0, paper_id=paper_id)
    commit(args.records_file, "first_rating", rating, paper_id)
    rating = fetch_ratings(-1, paper_id=paper_id)
    commit(args.records_file, "final_rating", rating, paper_id)
