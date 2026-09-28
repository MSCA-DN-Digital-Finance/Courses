---
marp: true
paginate: true
size: 16:9
theme: default
title: Module A — Gu Kelly Xiu (2020) + robustness
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
footer: Module A · Gu–Kelly–Xiu (2020) · RFS · + Avramov–Cheng–Metzker (2023)
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _footer: "" -->
<!-- cover -->
# Module A
## Gu, Kelly, Xiu (2020)

Barbara Będowska-Sójka · Poznań University of Economics and Business

MSCA Doctoral Network Digital Finance · MSCA_DF_10 Introduction to AI for Financial Applications

![h:120](img/logo_digital.jpg)![h:88](img/logo_uep.png)

---

# Papers and materials

Gu, S., Kelly, B., & Xiu, D. (2020).
*Empirical Asset Pricing via Machine Learning.*
*Review of Financial Studies*, 33(5), 2223–2273.

**After `01` (FF + lagged ML).**
**Live:** `notebooks/01a_gu_kelly_xiu_simplified.ipynb`
**Authors' data & code:** `datashare.zip` (Xiu's website) · `github.com/xiubooth/ML_Codes`

---

<!-- _class: card -->
<!-- card:gkx -->
# Paper card: Gu, Kelly & Xiu (2020)

| | *Review of Financial Studies* 33(5): 2223–2273 |
|---|---|
| **Question** | Which ML methods measure the equity risk premium best, by predicting individual stock returns one month ahead? |
| **Data** | About 30,000 US stocks (CRSP), March 1957 – December 2016; 94 characteristics interacted with 8 macro predictors, plus 74 industry dummies: 920 predictors. |
| **Method** | A ladder from OLS and elastic net through PCR/PLS and generalized linear models to random forests, boosted trees and neural nets with 1–5 hidden layers. |
| **How it is tested** | Train 1957–74, validate 1975–86, test 1987–2016, refit every year; no cross-validation, to keep time order. Out-of-sample $R^2$ against a zero forecast; long–short decile portfolios. |
| **Main result** | Trees and neural nets beat linear models; shallow nets do best. The best monthly $R^2_{\text{OOS}}$ is small (→ poll in class). Long–short Sharpe ratio of the neural net: 1.35 value-weighted, 2.45 equal-weighted. |
| **Watch for** | The sample keeps stocks below \$5. Equal-weighted beats value-weighted: where does the profit come from? (→ Avramov et al.) |
| **Code & data** | Characteristics (datashare.zip) and code (GitHub: xiubooth/ML_Codes) are public; returns need CRSP. |

---

# Economic question

Measure the equity **risk premium** by predicting individual stock excess returns one month ahead.

Which ML tools beat linear benchmarks **out of sample**, in forecast accuracy and in portfolios?

**Hypothesis:** nonlinear interactions among characteristics carry risk-premium information that linear models miss.

---

# Target & sample (paper)

- Unit: stock–month, all NYSE/AMEX/NASDAQ stocks in CRSP
- March 1957 – December 2016: almost 30,000 stocks, more than 6,200 per month
- **Kept:** stocks priced below \$5, non-common share codes, financials (fn. 28)
- Target: next-month excess return (T-bill as the risk-free rate)

Classroom notebook: a synthetic panel with a planted nonlinear signal.

---

# Features: 920 predictors

| Block | Count |
|-------|-------|
| Firm characteristics (61 annual, 13 quarterly, 20 monthly) | 94 |
| × Welch–Goyal macro (dp, ep, bm, ntis, tbl, tms, dfy, svar) | 8 |
| Industry dummies (2-digit SIC) | 74 |

Characteristics are **ranked** cross-sectionally each month into $[-1,1]$.

Ask: what is known **before** the month $t+1$ return?

---

# Validation

- Training 1957–1974 (18 y) · validation 1975–1986 (12 y) · **test 1987–2016 (30 y)**
- Refit **once a year**: the training window expands, the 12-year validation window rolls forward
- **No** cross-validation, "to maintain the temporal ordering of the data"
- Tune on validation; the test period stays untouched

---

# Results: small $R^2$, clear ranking

| Model | $R^2_{\text{OOS}}$ (monthly, %) |
|-------|------|
| OLS, all 920 features | −3.46 |
| OLS-3 (size, bm, mom) | 0.16 |
| ENet + Huber | 0.11 |
| RF / GBRT + Huber | 0.33 / 0.34 |
| NN1 → **NN3** | 0.33 → **0.40** |

$R^2_{\text{OOS}}$ is measured against a forecast of **zero**, not the historical mean.

---

# Finance evaluation

**Long–short decile spread on NN forecasts:**
annualized Sharpe **1.35** (VW) / **2.45** (EW)
against 0.61 / 0.83 for the OLS benchmark.

The dominant signals are momentum, liquidity and volatility.

Discuss: EW beats VW by a lot. What does that tell you?

---

# Model ladder (paper → classroom)

| Paper | Classroom subset |
|-------|------------------|
| OLS / PCR / PLS / elastic net | OLS, Ridge |
| Trees / RF / GBRT | Random Forest |
| Neural nets | Small MLP |

Always keep the linear baseline.

Homework: `01b` (named characteristics).

---

# Live notebook agenda (~45 min)

1. Build the synthetic characteristic panel
2. Temporal split
3. Fit the ladder
4. OOS $R^2$ table
5. Long–short cumulative paths
6. One "do differently" cell

---

# Do differently (seeds)

1. Rank-transform on/off
2. Expanding vs rolling window
3. Turnover penalty
4. **Drop microcaps** (below the 20th NYSE size percentile) and re-sort

The last seed is the next paper.

---

<!-- _class: card -->
<!-- card:avramov -->
# Paper card: Avramov, Cheng & Metzker (2023)

| | *Management Science* 69(5): 2587–2619 |
|---|---|
| **Question** | Do deep-learning return signals survive economic restrictions: microcaps, distressed firms, trading costs? |
| **Data** | US stocks, out-of-sample 1987–2017; signals from GKX's NN3, CPZ's GAN, IPCA and the conditional autoencoder. |
| **Method** | Re-sort the ML signals after excluding microcaps (below the 20th NYSE size percentile), distressed firms (12 months around a rating downgrade) and high limits-to-arbitrage periods. |
| **How it is tested** | Value-weighted, FF6-adjusted long–short returns; portfolio turnover. |
| **Main result** | GKX's FF6-adjusted return falls from 0.92% to 0.31% a month without microcaps. Without distressed firms, no deep-learning method is significant. Turnover is at least 87% a month. The signals still pay on the long side and in crashes. |
| **Watch for** | Different filters, benchmark and weighting from GKX. Which claim is each paper testing? |
| **Code & data** | Needs CRSP/Compustat and the original authors' signals. |

---

# Robustness: who earns Gu's alpha?

Avramov, D., Cheng, S., & Metzker, L. (2023). *Machine Learning vs. Economic Restrictions: Evidence from Stock Return Predictability.* *Management Science*, 69(5), 2587–2619.

- Models: GKX NN3, CPZ GAN, IPCA, conditional autoencoder
- Out-of-sample 1987–2017
- **Microcaps:** below the 20th NYSE size percentile
- **Distressed:** rated firms from 12 months before to 12 months after a downgrade

---

# Robustness: the numbers

| | GKX, VW, FF6-adjusted |
|---|---|
| All stocks | ≈ 0.92% / month |
| Without microcaps | ≈ 0.31% / month (≈ −2/3) |
| Without distressed firms | not significant |

"None of the deep learning methods generates significant value-weighted FF6-adjusted returns at the 5% level after excluding distressed firms."

GKX turnover: ≥ 87% per month.

On the other side: the long leg is profitable, recent years are profitable, and downside risk is low.

---

# Discussion: both papers can be right

**GKX (fn. 28):** results unchanged when low-price stocks, non-common shares and financials are filtered out.
**Avramov et al.:** excluding microcaps or distressed firms "considerably attenuates profitability".

What differs?

- the **filter** (price and share code vs size, rating and volatility state)
- the **benchmark** (raw return vs FF6 alpha)
- the **weighting** (EW vs VW)

Which hypothesis does each paper test?

---

# Takeaway

Gu–Kelly–Xiu is a **research design** for ML in the cross-section, not a verdict that "neural nets win".

**Where** the alpha lives is part of the result.

**Next:** Krauss, with classification and a portfolio rule
