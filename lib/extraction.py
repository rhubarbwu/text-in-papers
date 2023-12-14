import json
import shutil
import subprocess
from os import chdir, listdir, makedirs, path, remove, system
from typing import Tuple

import pytesseract
from PIL import Image

ARTIFACTS = ["pdfs", "jsons", "figures"]


def init():
    for directory in ARTIFACTS:
        makedirs(directory, exist_ok=True)


def clean_up(paper_id: str = None):
    for directory in ARTIFACTS:
        if paper_id is None:
            shutil.rmtree(directory)
        for file in listdir(directory):
            if file.startswith(paper_id):
                remove(f"{directory}/{file}")


def download_paper(paper_id: str) -> Tuple[int, float, float]:
    url = f"https://openreview.net/pdf?id={paper_id}"
    paper_path = f"pdfs/{paper_id}.pdf"

    # command = ["curl", "-s", "-o", paper_path, url]
    command = ["wget", "-O", paper_path, url]
    try:
        subprocess.check_output(command, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")


def extract_figures():
    chdir("pdffigures2")
    command = 'sbt "runMain org.allenai.pdffigures2.FigureExtractorBatchCli ../pdfs/ -s ../stat_file.json -m ../figures/ -d ../jsons/ -i 300"'

    exit_code = system(command)

    if exit_code == 0:
        print("Command executed successfully.")
    else:
        print(f"Command failed with exit code {exit_code}.")

    chdir("..")


def count_caption_chars(paper_id: str) -> Tuple[int, int]:
    char_counts = 0  # may want per-figure counts later
    n_figs = 0

    json_path = f"jsons/{paper_id}.json"
    if not path.exists(json_path):
        return -1, -1
    with open(f"jsons/{paper_id}.json", "r") as f:
        metadata = json.load(f)

    paths = set()
    for fig_data in metadata:
        caption = fig_data["caption"]
        if fig_data["renderURL"] in paths or not caption.split(" ")[1].endswith(":"):
            continue
        paths.add(fig_data["renderURL"])

        char_counts += len(fig_data["caption"])
        n_figs += 1
    return char_counts, n_figs


def count_fig_chars(paper_id: str) -> Tuple[int, int]:
    char_counts = 0  # may want per-figure counts later
    n_figs = 0

    for fig_file in listdir("figures"):
        if not fig_file.startswith(paper_id):
            continue

        image = Image.open(f"figures/{fig_file}")
        text = pytesseract.image_to_string(image)  # OCR
        text = "".join([c for c in text if not c.isspace()])
        char_count = len(text)
        char_counts += char_count
        n_figs += 1

    return char_counts, n_figs
