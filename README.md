# Text in Visualizations

## Prerequisites

Install dependencies.

```sh
pip install -r requirements.txt
```

Download [PDFFigures 2.0](https://github.com/allenai/pdffigures2) as a subdirectory.

```sh
git clone https://github.com/allenai/pdffigures2
```

### Datasets

This repository is written for [ICLR2023 Statistics](https://github.com/weigq/iclr2023_stats).

```sh
git clone https://github.com/weigq/iclr2023_stats
```

## Analysis

Analyze and collect fig/character counts.

```sh
# full repository
python counts.py -o analytics.h5

# second hundred
python counts.py -o analytics.h5 -s 100 -e 200
```
