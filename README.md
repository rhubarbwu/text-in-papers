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

Install [`cs` (`scala`)](https://www.scala-lang.org/download/) and [`sbt`](https://www.scala-sbt.org/1.x/docs/Installing-sbt-on-Linux.html).

### Datasets

This repository is written for [ICLR2023 Statistics](https://github.com/weigq/iclr2023_stats).

```sh
git clone https://github.com/weigq/iclr2023_stats
```

## Query by Keywords

Use the following CSV template: `<query_id>:<keyword><op><keyword>:` where `<op>` is `OR` (`|`) or `AND` (`&`). For example,

```csv
query_id:patterns:paper_ids
qml:quantum&machine&learning:
```

Running `search.py` will append the `paper_id`s of the matching submissions. For the above example,

```csv
query_id:patterns:paper_ids
qml:quantum&machine&learning:Ry-cTiH_cus,wyjAf9GPD_,xveTeHVlF7j,o-Yxq5iicIp,ymFhZxw70uz,ySQeVdXOcx0,3wCqIZivcJx
```

## Analysis

Analyze and collect fig/character counts.

```sh
# full repository
python counts.py -o analytics.h5

# second hundred
python counts.py -o analytics.h5 -s 100 -e 200
```

### Scoring

Extract scores to matching paper IDs.

```sh
python scores.py analytics.h5
```
