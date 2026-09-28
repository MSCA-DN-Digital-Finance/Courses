---
marp: true
paginate: true
size: 16:9
theme: default
title: Module B — Krauss Do Huck (2017)
style: |
  section { font-size: 28px; }
  h1 { font-size: 40px; }
  table { font-size: 22px; }
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
footer: Module B · Krauss–Do–Huck (2017) · EJOR
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _footer: "" -->
<!-- cover -->
# Module B
## Krauss, Do, Huck (2017)

Barbara Będowska-Sójka · Poznań University of Economics and Business

MSCA Doctoral Network Digital Finance · MSCA_DF_10 Introduction to AI for Financial Applications

![h:120](img/logo_digital.jpg)![h:88](img/logo_uep.png)

---

# Papers and materials

Krauss, C., Do, X. A., & Huck, N. (2017).
*Deep neural networks, gradient-boosted trees, random forests: Statistical arbitrage on the S&P 500.*
*European Journal of Operational Research*, 259(2), 689–702.

**Live:** `notebooks/02_krauss_simplified.ipynb`

---

<!-- _class: card -->
<!-- card:krauss -->
# Paper card: Krauss, Do & Huck (2017)

| | *European Journal of Operational Research* 259: 689–702 |
|---|---|
| **Question** | Can deep nets, gradient-boosted trees and random forests rank S&P 500 stocks well enough for profitable statistical arbitrage? |
| **Data** | S&P 500 constituents from month-end membership lists (no survivor bias); daily data 1990–2015; trading December 1992 – October 2015. |
| **Method** | Classify whether tomorrow's return beats the cross-sectional median. Features: 31 lagged returns (1–20 days, then monthly out to 240 days). DNN, GBT, RF and their equal-weighted ensemble. |
| **How it is tested** | Walk-forward: train 750 days, trade the next 250, 23 periods. Each day, go long the top 10 and short the bottom 10. |
| **Main result** | The ensemble earns 0.45% a day before costs and 0.25% after 5 bp per half-turn. RF beats the DNN. Returns decay after 2001. |
| **Watch for** | The abstract claims a challenge to semi-strong efficiency. Which form of efficiency do lagged returns test? |
| **Code & data** | Datastream data (licensed); no code package. Our notebook rebuilds the design on public Yahoo data. |

---

# Contrast with Gu

| Gu–Kelly–Xiu | Krauss–Do–Huck |
|--------------|----------------|
| Predict the **return** (regression) | Predict **above the CS median** (classification) |
| Characteristic zoo, monthly | 31 lagged returns, daily |
| OOS $R^2$ + sorts | Probabilities → ranked long–short |

Same ML tools, different **decision object**.

---

# Economic question

Can classifiers rank S&P 500 stocks by their chance of **beating the cross-sectional median tomorrow**, well enough to build a market-neutral long–short book?

---

# Hypothesis check (5 min)

The abstract: "our findings pose a severe challenge to the **semi-strong** form of market efficiency."

The features: **31 lagged returns**, nothing else.

**Which form of efficiency does this test?**
Restate the paper's hypothesis in one sentence.

---

# Label & sample (paper)

- S&P 500, daily data 1990–2015, trading **Dec 1992 – Oct 2015**
- Survivor bias removed with **month-end constituent lists** (§3.1)
- Label (§4.2): $y_{i,t+1} = 1\{r_{i,t+1} > \mathrm{median}_j\, r_{j,t+1}\}$, **not** measured against the index
- The median label gives balanced classes and a market-neutral target

---

# Features & validation

- $R_{t,m}$ for $m \in \{1,\dots,20\} \cup \{40, 60, \dots, 240\}$: daily for one month, monthly out to a year
- Study period: **750 days training + 250 days trading**, 23 non-overlapping trading periods
- **No hyperparameter search:** a heuristic DNN architecture, H2O defaults elsewhere
- Rank by $P(y=1)$, not by the hard 0/1 label

---

# Model ladder (paper)

| Model | Key settings | Daily return, $k=10$, pre-cost |
|-------|--------------|------|
| DNN | 31-31-10-5-2, maxout, dropout | 0.33% |
| GBT | 100 trees, depth 3, lr 0.1 | 0.37% |
| RF | 1,000 trees, depth 20 | 0.43% |
| ENS1 | equal-weighted average | **0.45%** |

Classroom: Logistic → RF → GBT → small MLP.

---

# From scores to P&L

Each day:

1. Predict probabilities
2. Long top-$k$, short bottom-$k$ ($k = 10$ of about 500)
3. Track the excess long–short return
4. Costs: **5 bp per half-turn** cut ENS1 from 0.45% to **0.25% per day**

A great AUC with fatal turnover is not a strategy.

---

# Decay

- Returns spike in turmoil (the dot-com bust, 2008)
- They **decline after 2001**, as ML and computing spread

Link: McLean & Pontiff (2016, *JF*): publication erodes predictability.

Is the edge a market fact or a period fact?

---

# Our real mode is not a replication

| | Paper | Our real mode |
|---|---|---|
| Universe | ~500, historical members | 50 **current** names (survivors) |
| $k$ per side | 10 (2%) | set $k = 1$ to match 2% |
| Membership | month-end lists | none |

In our run: AUC ≈ 0.50 and the best break-even cost is ≈ 3 bp, below the 5 bp cost. Survivorship lifts the *level* of returns, not the edge in *ranking* them.

---

# Live notebook agenda

1. Build labels (**above the cross-sectional median**)
2. Fit Logit / RF / GBT / MLP
3. Long–short from ranks, $k$ scaled to the universe
4. Cost grid in bp; break-even cost
5. Experiment: change $k$; median vs index label

---

# Discussion hooks

- Can AUC rise while Sharpe falls?
- What does high turnover say about capacity?
- After costs: would you still ship the NN?
- Nothing was tuned. Does that make the horse race fairer or less fair?

---

# Frontier pointer

Guijarro-Ordonez, J., Pelger, M., & Zanotti, G. *Deep Learning Statistical Arbitrage.* *Management Science*, 72(9).

The same question, with economic structure:

- trade **residual** portfolios after removing factor exposure
- extract the signal with a CNN + transformer
- learn the **trading policy** directly, with costs inside the objective

The same step as Gu → Chen–Pelger–Zhu: put the objective inside the loss.

---

# Takeaway

A classifier is only as good as the **label, the portfolio rule and the frictions** you attach to its scores.

**Next:** Module C, where credit decisions and the benchmark protocol are the contribution
