---
marp: true
paginate: true
size: 16:9
theme: default
title: MSCA_DF_10 — Machine Learning in Finance (paper deconstruction)
description: Framing deck for the training day
style: |
  section { font-size: 28px; }
  h1 { font-size: 42px; }
  h2 { font-size: 34px; }
  table { font-size: 22px; }
  footer { font-size: 14px; }
  blockquote { font-size: 30px; }
  section.cover h1 { font-size: 50px; margin-bottom: 0; }
  section.cover h2 { font-size: 30px; font-weight: 400; color: #4a5568; margin-top: 6px; }
  section.cover p { font-size: 21px; color: #4a5568; margin: 6px 0; }
  section.cover p:last-of-type { position: absolute; bottom: 56px; left: 70px; margin: 0; }
  section.cover p:last-of-type img { margin-right: 44px; vertical-align: middle; }
  section.card { font-size: 20px; padding: 30px 50px 44px; }
  section.card h1 { font-size: 30px; margin: 0 0 10px; }
  section.card table { font-size: 19px; }
  section.card td, section.card th { padding: 5px 10px; vertical-align: top; }
  section.card td:first-child { white-space: nowrap; }
footer: MSCA_DF_10 · Machine Learning in Finance · paper deconstruction
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _footer: "" -->
<!-- cover -->
# Machine Learning in Finance
## Deconstructing published papers

This is not a methods survey. It is a **research-design** workshop.

Barbara Będowska-Sójka · Poznań University of Economics and Business

MSCA Doctoral Network Digital Finance · MSCA_DF_10 Introduction to AI for Financial Applications

![h:120](img/logo_digital.jpg)![h:88](img/logo_uep.png)

---

# Learning goals

By the end of today you can:

1. Restate a paper as an **economic question + prediction design**
2. Tell a **prediction** apart from a **hypothesis test**
3. Spot **leakage**, bad validation and metric mismatch
4. Walk a pipeline: sample → features → split → models → finance evaluation
5. Judge a **robustness** or **replication** claim
6. Propose one falsifiable **"do differently"** experiment

---

# Day map

| Block | Focus | Min | Live artifact |
|-------|-------|-----|---------------|
| Opener | pitfalls · R vs Python · prediction vs inference | 20 | this deck · `00b` |
| A · FF → Gu → robustness | factors, ML forecast, who earns the alpha | 110 | `01`, `01a` |
| B · Krauss–Do–Huck | classify → portfolio → frictions | 90 | `02` |
| C · Credit | Lessmann protocol on public data · Fuster | 60 | `03_lessmann_credit_lab` |
| A+ · Chen–Pelger–Zhu | economics inside the loss | 30 | slides |
| D · Replication | what counts · KMZ vs Nagel live | 40 | `06_kmz_nagel` |
| E · Crypto zombies | replication from the author's side | 50 | `05` |
| 07 · Cakici | ML and the crypto cross-section | — | `07` |
| Wrap | seven moves | 5 | `08_wrap` |

---

<!-- _class: card -->
# The day's papers at a glance

![w:1160](img/papers_map.svg)

---

# Papers (1/2): asset pricing

| Block | Citation |
|-------|----------|
| Opener | Mullainathan & Spiess (2017) *JEP*, *Machine Learning: An Applied Econometric Approach* |
| A | Fama & French (1993, 2015) *JFE*, *Common risk factors…* / *A five-factor asset pricing model* |
| A | Gu, Kelly & Xiu (2020) *RFS*, *Empirical Asset Pricing via Machine Learning* |
| A | Avramov, Cheng & Metzker (2023) *MS*, *Machine Learning vs. Economic Restrictions* |
| B | Krauss, Do & Huck (2017) *EJOR*, *…Statistical arbitrage on the S&P 500* |
| A+ | Chen, Pelger & Zhu (2024) *MS*, *Deep Learning in Asset Pricing* |

---

# Papers (2/2): credit, replication, crypto

| Block | Citation |
|-------|----------|
| C | Lessmann, Baesens, Seow & Thomas (2015) *EJOR*, *Benchmarking … credit scoring* |
| C | Gunnarsson et al. (2021) *EJOR*, *Deep learning for credit scoring: Do or don't?* |
| C | Fuster, Goldsmith-Pinkham, Ramadorai & Walther (2022) *JF*, *Predictably Unequal?* |
| D | Harvey, Liu & Zhu (2016) *RFS*; Jensen, Kelly & Pedersen (2023) *JF* |
| D | Kelly, Malamud & Zhou (2024) *JF* vs Nagel (2025) NBER WP 34104 |
| E | Będowska-Sójka, Wójcik & Pele (2025) *NAJEF*, *…Predicting 'zombie' assets* |

Used as an exercise only: Zeng, Melville et al. (2008) *KDD*, *invoice-to-cash collection*.

---

# How we work each paper

We use the same 8 prompts every time (`sessions/SESSION_TEMPLATE.md`):

1. Economic question, and the **hypothesis**
2. Target & sample
3. Features
4. Validation
5. Model ladder
6. Finance evaluation
7. Replicability: data **and code**
8. Do differently

---

<!-- _class: card -->
<!-- card:ms -->
# Paper card: Mullainathan & Spiess (2017)

| | *Journal of Economic Perspectives* 31(2): 87–106 |
|---|---|
| **Question** | What is machine learning good for in applied economics, and what is it not good for? |
| **Data** | American Housing Survey 2011: predict house values from 150 variables; 10,000 training and 41,808 hold-out units. |
| **Method** | OLS vs regression tree, LASSO, random forest and an ensemble, tuned by cross-validation. |
| **How it is tested** | Hold-out $R^2$; LASSO re-fitted on ten random partitions of the data. |
| **Main result** | ML predicts better, but modestly: hold-out $R^2$ 41.7% (OLS) vs 45.9% (ensemble). LASSO picks different variables in each partition with the same fit. |
| **Watch for** | "ML belongs in the $\hat y$ compartment, not the $\hat\beta$ compartment." A selected variable is not a finding. |
| **Code & data** | Replication files on openICPSR (project 113993). |

---

# Prediction vs inference

Mullainathan, S., & Spiess, J. (2017). *Machine Learning: An Applied Econometric Approach.* *Journal of Economic Perspectives*, 31(2), 87–106.

> "Machine learning belongs in the part of the toolbox marked $\hat{y}$ rather than in the more familiar $\hat{\beta}$ compartment."

ML algorithms are built to predict. Even when they report coefficients, "the estimates are rarely consistent".

---

# ML predicts well, but modestly

American Housing Survey 2011: 10,000 training units, 150 variables, 41,808 hold-out units.

| Model | Hold-out $R^2$ |
|-------|----------------|
| OLS | 41.7% |
| Regression tree | 34.5% |
| LASSO | 43.3% |
| Random forest | 45.5% |
| Ensemble | 45.9% |

---

# …but the selected variables are unstable

- LASSO re-fit on **ten partitions** of about 5,000 units each
- A different set of variables in each partition, with the same fit
- "Similar predictions can be produced using very different variables"

**So a selected variable is not a finding.** The same holds for feature importance (Gu, Block A) and XAI (crypto zombies, Block E).

Where ML helps research: new data (text, images) · first-stage prediction (IV, propensity scores) · prediction-policy problems.

---

# Map the day: $\hat{y}$ or $\hat{\beta}$?

| Paper | Prediction target | Hypothesis, if any |
|-------|-------------------|--------------------|
| FF (2015) | none | Five factors price average returns ($\alpha = 0$) |
| Gu (2020) | next-month return | Nonlinear interactions carry risk-premium information |
| Krauss (2017) | $P(r > \text{CS median})$ | Past prices predict returns (weak form) |
| Lessmann (2015) | $P(\text{default})$ | Advanced classifiers beat LR under a fixed protocol |
| Fuster (2022) | $P(\text{default})$ | ML changes who gains from credit |
| CPZ (2024) | SDF weights | No-arbitrage structure improves pricing |
| KMZ vs Nagel | market return | More parameters improve timing |
| Zombies (2025) | $P(\text{delisting}, 28\text{d})$ | Zombie status is predictable from market data |

We come back to this table in Block D.

---

# Why finance breaks naive ML

- **Low SNR:** a tiny $R^2$ can still matter in portfolios
- **Time:** the future must not train the past
- **Decisions:** AUC ≠ Sharpe ≠ expected loss
- **Frictions:** turnover, shorting, collection capacity
- **Multiple testing:** the factor zoo is real

---

# Pitfall 1: Look-ahead / leakage

Classic killers:

- Using revised filings as if they were known in real time
- Features updated *after* the label date
- Random CV on panels / invoices / customers
- Index membership known only ex post (survivors)
- LLMs trained on text from *after* the forecast date

**Rule:** write down the information set at decision time.

---

# Pitfall 2: Wrong split

| OK under i.i.d. | Dangerous in finance |
|-----------------|----------------------|
| Shuffle + K-fold | Leaks adjacent times / firms |
| Tune on test | Inflates horse-race winners |
| One lucky seed | Unstable rankings |

Prefer a **calendar** train / validation / test split (expanding or rolling).

---

# Pitfall 3: Metric mismatch

| Domain | Statistical score | Economic object |
|--------|-------------------|-----------------|
| Asset pricing | OOS $R^2$; GRS / mean $\lvert\alpha\rvert$ | long–short, Sharpe, costs |
| Stat-arb | AUC / accuracy | ranked portfolio + turnover |
| Credit | AUC / H / Brier | expected cost, calibration, who gains |

Always ask: *what decision does the score feed?*

---

# The model ladder (classroom habit)

Always keep a **strong simple baseline**.

```
linear / logit  →  regularized  →  trees / boosting  →  small NN
```

Complexity must buy something on the **economic** metric, not only on fit.

---

# What the classroom notebooks are

| Module | Data | Goal |
|--------|------|------|
| FF (`01`) | real, 50 current names | attribution vs forecast; survivors |
| Gu (`01a`) | synthetic characteristics | pipeline, not a CRSP replica |
| Krauss (`02`) | synthetic, or real 50 names | label → portfolio → costs |
| Credit (`03`) | **real, public** (UCI; Kaggle if you download it) | a mini-Lessmann replication |
| KMZ–Nagel (`06`) | **real, public** (Welch–Goyal) | replicate, then reinterpret |
| Zombies (`05`) | real, public CSV | an author-led pipeline |

With synthetic data the magnitudes will not match the paper. The **design choices** should.

---

# Your course folder

- `00_START_HERE.pdf`: setup check and data sources
- `Programme.pdf` · `Reading_list.pdf` · `Paper_cards.pdf`
- `notebooks/`: the Python notebooks we run today
- `data/`: the data, with precomputed results in `data/cache/`
- `scripts/`: the scripts that precompute the slow steps
- The slides are in slides/, one deck per block

---

# Ground rules for discussion

- Critique the **design**, not the authors' intelligence
- Prefer "how would we test that?" over vibes
- Park deep architecture rabbit holes for later
- One takeaway sentence per module

---

# Next up: Module A

**First** Fama–French on 50 names (`01`), **then** Gu, **then** who earns Gu's alpha.

→ `slides/01_ff_factors.md` · `notebooks/01_ff_factors_real.ipynb`
→ `slides/01a_gu_kelly_xiu.md` · `notebooks/01a_gu_kelly_xiu_simplified.ipynb`
