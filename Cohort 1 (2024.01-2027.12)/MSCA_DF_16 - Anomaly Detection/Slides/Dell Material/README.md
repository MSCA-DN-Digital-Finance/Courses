# Anomaly Detection: MSCA Doctoral Programme

A hands-on course on detecting anomalies in tabular and time-series data, from classical detectors to cost-sensitive decisions in production.

**Date:** 09/11/2026 (9 November 2026)
**Instructors:** Eduard Stan, Oana Sîrbu, Luiza Ciucu (Data Scientists, Dell Technologies)

## Modules

The three modules run back to back on the same day.

| Module | Topic | What it covers | Data |
|---|---|---|---|
| 1 | Classical models on tabular data | Anomaly types (point, contextual, collective); Isolation Forest, LOF and One-Class SVM; precision, recall and PR-AUC; threshold tuning | Credit Card Fraud, KDD Cup 1999 |
| 2 | Fraud: cost, drift and explainability | Imbalance strategies; cost-sensitive decisions; supervised vs. unsupervised under concept drift; SHAP | Sparkov card transactions (synthetic by default) |
| 3 | Contextual anomalies and seasonality | Trend, seasonality and residual; sliding-window features; dynamic z-score vs. Isolation Forest | NYC taxi demand |

Module 3 materials are not in this repository yet.

## How the course is structured

Each module has two parts:

1. **Lecture:** a slide deck that introduces the ideas, with short interactive checks.
2. **Lab:** a Jupyter notebook that turns those ideas into code straight after the lecture.

In the student notebooks:

- ✏️ cells are yours to complete.
- ⭐ cells are optional.
- Discussion cells are for your group.

## The project

By **30 December 2026, 23:59** (fixed deadline), you complete an individual final project that applies the course pipeline to **a dataset you choose**. The topics and requirements are in a separate brief.

> Explore → prepare → score → threshold → evaluate

## Repository branches

| Branch | Contents |
|---|---|
| `main` | This README only |
| `student` | README, requirements, slide decks and student labs |
| `instructor` | README, requirements, slide decks and instructor labs with solutions |

## Setup

Clone the branch you need, then install the dependencies:

```bash
git clone -b student https://github.com/EdyStan/Anomaly-Detection-MSCA-Course.git
cd Anomaly-Detection-MSCA-Course
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

Open the decks (`.html`) directly in a browser. The labs also run in Google Colab. They try to download the real datasets from Kaggle where available and fall back to synthetic data, so they still run offline.
