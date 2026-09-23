# Machine Learning in Finance: deconstructing published papers

One day of the four-day course **MSCA_DF_10 Introduction to AI for Financial Applications**, MSCA Doctoral Network Digital Finance.
Instructor: Barbara Będowska-Sójka, Poznań University of Economics and Business.

A one-day online training for doctoral candidates. We read published papers as research designs: the question and the hypothesis, the data, the validation, the economic evaluation, robustness and replication. For each block we rebuild the core of the design in a Python notebook that runs in class.

Before the course this folder holds the notebooks, the data we may share, the paper cards and the reading list. The slides follow after the course.

## Contents

| File or folder | What it holds |
|---|---|
| `Paper_cards.pdf` | one slide per paper: question, data, method, test, result, what to watch for |
| `Reading_list.pdf` | the 15 papers of the day, with links |
| `notebooks/` | the notebooks we run in class (outputs cleared) |
| `scripts/` | scripts that precompute the slow steps |
| `data/` | the public data the notebooks use (sources below) and the download scripts |
| `data/cache/` | precomputed results, so each live notebook runs in under two minutes |
| `experiments/` | where to put the cryptocurrency data for notebook `05` |
| `slides/` | the slides, after the course |

## The day

| Block | Topic | Papers | Notebook |
|---|---|---|---|
| Opener | Prediction vs inference | Mullainathan & Spiess (2017) | none |
| A | Factor models, ML forecasts of returns, and who earns the alpha | Fama & French (2015); Gu, Kelly & Xiu (2020); Avramov, Cheng & Metzker (2023) | `01_ff_factors_real`, `01a_gu_kelly_xiu_simplified` (`01b_gu_fama_french`: homework) |
| B | Classification → portfolio → frictions | Krauss, Do & Huck (2017) | `02_krauss_simplified` |
| C | Credit: the benchmark protocol | Lessmann et al. (2015); Gunnarsson et al. (2021); Fuster et al. (2022); Zeng et al. (2008), as an exercise | `03_lessmann_credit_lab` (`03_invoice_timing_simplified`: optional homework) |
| A+ | Economics inside the loss | Chen, Pelger & Zhu (2024) | `04_chen_pelger_zhu_sketch` (homework) |
| D | Replication and robustness | Harvey, Liu & Zhu (2016); Jensen, Kelly & Pedersen (2023); Kelly, Malamud & Zhou (2024); Nagel (2025) | `06_kmz_nagel` |
| E | Replication from the author's side | Będowska-Sójka, Wójcik & Pele (2025) | `05_crypto_zombies_csv_only` |

Full references are in `Reading_list.pdf` and in `../Reading materials for Introduction to AI for Financial Applications.txt`.

The classroom notebooks are teaching versions, not replications. Where a paper needs licensed data (CRSP, Compustat, Datastream), the notebook uses synthetic data or a small public sample and says so.

## How to run

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python data/download_krauss_panel.py   # stock prices for notebooks 01 and 02 (see below)
jupyter lab                        # or: jupyter notebook
```

Open the notebooks from `notebooks/` and run all cells. The first run in a new environment takes a minute longer while Python builds its caches. Without the price file, notebooks `01` and `02` stop and tell you to run the download script; `02` can also run on synthetic data (`DATA_MODE = "synthetic"`).

## Data and sources

| Data | Used in | Included here? | Source and how to get it |
|---|---|---|---|
| Fama–French daily factors | `01` | yes | Kenneth R. French Data Library |
| Daily prices of 50 S&P 500 stocks and SPY | `01`, `02` | no: Yahoo Finance terms do not allow redistribution | run `python data/download_krauss_panel.py` |
| German and Australian credit data (UCI) | `03` | yes (CC BY 4.0) | UCI Machine Learning Repository |
| Give Me Some Credit | `03` | no: Kaggle competition data | download `cs-training.csv` from Kaggle into `data/gmc/`, then run `python scripts/precompute_gmc.py`. Without it, the lab runs on the two UCI data sets |
| Welch–Goyal monthly predictors, 2025 release | `06` | yes | Amit Goyal's website |
| Weekly cryptocurrency snapshots | `05` | no (about 1 GB) | QuantLet, Crypto_Zombies; `experiments/crypto_zombies_runbook.txt` says where to put `all_symbols.csv` |
| Synthetic panels | `01a`, `01b`, `04`, `03_invoice` | generated in the notebooks | none |

Each data set keeps its own licence or terms of use. Please cite the original sources.

## Licence

Code: MIT (see `LICENSE`). Slides and text: CC BY 4.0.
