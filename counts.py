import argparse
from os import path

from h5py import File
from tqdm import tqdm

from lib.extraction import (clean_up, count_caption_chars, count_fig_chars,
                            download_paper, extract_figures, init)
from lib.records import commit

PAPER_IDS_FILE = "iclr2023_stats/assets/filter_ids_2022-11-05-19:32-UTC.txt"


parser = argparse.ArgumentParser()
parser.add_argument(
    "-s", "--start", type=int, default=0, help="which paper index to start at"
)
parser.add_argument(
    "-e",
    "--end",
    type=int,
    default=-1,
    help="which paper index to end at (exclusive)",
)
parser.add_argument(
    "-ids",
    "--paper_ids",
    type=str,
    nargs="+",
    default=[],
    help="specific papers IDs",
)
parser.add_argument(
    "-o",
    "--records_file",
    type=str,
    default="untitled.h5",
    help="path to output file",
)
parser.add_argument(
    "-1",
    "--single",
    action="store_true",
)
args = parser.parse_args()

if len(args.paper_ids) == 0:
    with open(PAPER_IDS_FILE, "r") as file:
        args.paper_ids = [line.strip() for line in file]

if args.end < 0:
    args.end = len(args.paper_ids)

init()

for idx in tqdm(range(args.start, args.end), ncols=64):
    paper_id = args.paper_ids[idx]

    if path.exists(args.records_file):
        file = File(args.records_file, "r")
        complete = (
            "n_cap_chars" in file
            and paper_id in file["n_figs"]
            and paper_id in file["n_fig_chars"]
            and paper_id in file["n_cap_chars"]
        )
        file.close()
        if complete:
            continue

    download_paper(paper_id)
    extract_figures()
    char_counts, n_figs = count_fig_chars(paper_id)
    commit(args.records_file, "n_figs", n_figs, paper_id)
    commit(args.records_file, "n_fig_chars", char_counts, paper_id)

    n_cap_chars, n_figs_data = count_caption_chars(paper_id)
    if n_cap_chars >= 0 and n_figs_data >= 0 and n_figs == n_figs_data:
        commit(args.records_file, "n_cap_chars", n_cap_chars, paper_id)

    clean_up(paper_id)
    if args.single:
        break
