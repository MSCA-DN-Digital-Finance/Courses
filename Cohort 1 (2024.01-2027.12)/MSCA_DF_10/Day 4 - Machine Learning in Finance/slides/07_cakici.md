---
marp: true
paginate: true
size: 16:9
theme: default
title: Cakici et al. — ML and the crypto cross-section (IRFA)
style: |
  section { font-size: 28px; }
  h1 { font-size: 40px; }
  table { font-size: 20px; }
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
footer: Cakici, Shahzad, Będowska-Sójka, Zaremba · IRFA · crypto ML
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _footer: "" -->
<!-- cover -->
# Block 07
## Cakici et al. (2024) — ML and the crypto cross-section

Barbara Będowska-Sójka · Poznań University of Economics and Business

MSCA Doctoral Network Digital Finance · MSCA_DF_10 Introduction to AI for Financial Applications

![h:120](img/logo_digital.jpg)![h:88](img/logo_uep.png)

---

# Papers and materials

Cakici, N., Shahzad, S. J. H., Będowska-Sójka, B., & Zaremba, A. (2024).
*Machine learning and the cross-section of cryptocurrency returns.*
*International Review of Financial Analysis*, 94, 103244.
DOI [10.1016/j.irfa.2024.103244](https://doi.org/10.1016/j.irfa.2024.103244)

**Notebook:** `notebooks/07_cakici_crypto_ml.ipynb`
**Siblings:** `01a` (Gu on equities) · `05` (crypto zombies: classifiers, not the return cross-section)

---

<!-- _class: card -->
<!-- card:cakici -->
# Paper card: Cakici, Shahzad, Będowska-Sójka & Zaremba (2024)

| | *International Review of Financial Analysis* 94: 103244 |
|---|---|
| **Question** | Can ML predict the cross-section of crypto returns, and does complexity help? |
| **Data** | 500+ coins and tokens, 250 exchanges, weekly 2017–2023; 40 characteristics. |
| **Method** | Eight models: dimension reduction, OLS and regularized regressions, trees, neural nets; equal-weight forecast combination. |
| **How it is tested** | Predictive $R^2$; value-weighted long–short; three-factor alpha; costs; splits by limits to arbitrage. |
| **Main result** | Combination: 2.37% a week, Sharpe 1.66. Simple models win. Signal: price, past alpha, illiquidity, momentum. |
| **Watch for** | Profit is the **long** leg, in small / illiquid / volatile coins. Drawdowns of 70–80%. |
| **Code & data** | Coin panel not in our package. Classroom sketch is synthetic. |

---

# Why this paper next to 01a and 05

| | Gu (`01a`) | Cakici | Zombies (`05`) |
|---|---|---|---|
| Market | equities | crypto | crypto |
| Object | $E[r]$ | $E[r]$ | delisting |
| Tool | ML ladder | ML ladder | classifiers |
| Complexity | usually helps | **usually does not** | RF vs logit |

Same market as `05`. Same *question* as Gu — different answer on complexity.

---

# Economic question

Is the crypto “factor zoo” a job for **deep** models, or do a few **simple** characteristics already sort winners from losers?

And once they do: is the alpha on the **short** leg (equities) or the **long** leg?

---

# Data (paper vs classroom)

| | Paper | Classroom sketch |
|---|---|---|
| Cross-section | 500+ coins | 80 synthetic coins |
| Frequency | weekly, 2017–2023 | 260 weeks |
| Characteristics | 40 | 4 signal + 4 noise |
| Models | eight families | OLS, Ridge, RF, MLP, Combo |

The planted signal is **linear** in price, alpha, illiquidity and momentum, and **stronger** for hard-to-trade names.

---

# Eight families → four classroom models

```
OLS → Ridge → RF → MLP → Combo (equal-weight average)
```

Paper punchline: **OLS often beats trees and nets.**
Forecast combination is their best **value-weighted** Sharpe.

If the classroom $R^2$ table has OLS / Ridge on top, that is the point — not a bug.

---

# Headline results (paper)

- All models make money; **complexity does not** add much
- Variable importance: **price, past alpha, illiquidity, momentum**
- Combination, value-weighted long–short: **2.37%** a week, Sharpe **1.66**, three-factor alpha **2.42%**
- $R^2$ looks disappointing; the **ranking** still works
- Gains **persist** in the second half of the sample (unlike many equity anomalies)

---

# Long leg, not short leg

Equities: anomalies often live in the names you want to **short**.

Crypto (this paper): the pattern is **L-shaped**.
The top predicted quintile earns; the rest is mediocre.

So short-sale constraints are **not** the main story — **limits to arbitrage on the long side** are.

---

# Costs and implementability

- High turnover, but most strategies **survive** costs (more than half the LS can disappear)
- Alphas **3–4×** larger in the hardest-to-trade tercile
- Four caveats they insist on:
  1. 70–80% drawdowns
  2. tiny, illiquid coins
  3. signals die if you rebalance every two weeks (~30% less)
  4. you need the extreme volatile names

Same Avramov / Krauss lesson: *who* you are long is part of the result.

---

# Live materials

| Where | What |
|-------|------|
| `notebooks/07_cakici_crypto_ml.ipynb` | synthetic panel; ladder; long vs short; VW / costs / hard-to-trade |
| Coin panel | not in the package |

---

# Map to the rest of the day

| Earlier module | Bridge |
|----------------|--------|
| Gu / 01a | same pipeline; opposite complexity result |
| Avramov et al. | ML alpha in hard-to-trade names |
| Krauss | a forecast is not a strategy without a portfolio rule and costs |
| Crypto zombies (`05`) | same market, different target |

---

# Do differently

1. Fit on the four signal columns only (drop the noise $z^*$)
2. Hold two weeks (paper: about 30% less profit)
3. Winsorize test returns at 1/99 (no extreme volatile coins)
4. Value-weight only the long leg

Tune on **validation**. Report on **test**.

---

# Takeaway

A crypto ML cross-section is still the craft of the day:

**simple characteristics → a model ladder → ranking, not $R^2$ → long vs short → who you can actually trade.**

Gu asked whether complexity pays in equities. This paper’s answer in crypto is: **usually not.**
