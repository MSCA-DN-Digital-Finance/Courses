---
marp: true
paginate: true
size: 16:9
theme: default
title: Module A homework — Gu pipeline with Fama–French characteristics
style: |
  section { font-size: 28px; }
  h1 { font-size: 40px; }
  table { font-size: 22px; }
  section.cover h1 { font-size: 50px; margin-bottom: 0; }
  section.cover h2 { font-size: 30px; font-weight: 400; color: #4a5568; margin-top: 6px; }
  section.cover p { font-size: 21px; color: #4a5568; margin: 6px 0; }
  section.cover p:last-of-type { position: absolute; bottom: 56px; left: 70px; margin: 0; }
  section.cover p:last-of-type img { margin-right: 44px; vertical-align: middle; }
footer: Module A · homework · Gu pipeline · Fama–French characteristics
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _footer: "" -->
<!-- cover -->
# Module A: homework
## The Gu pipeline with Fama–French characteristics

Barbara Będowska-Sójka · Poznań University of Economics and Business

MSCA Doctoral Network Digital Finance · MSCA_DF_10 Introduction to AI for Financial Applications

![h:120](img/logo_digital.jpg)![h:88](img/logo_uep.png)

---

# Homework: same Gu design, named fundamentals

Gu, S., Kelly, B., & Xiu, D. (2020). *Empirical Asset Pricing via Machine Learning.* *RFS*, 33(5), 2223–2273.

Characteristic names from Fama & French (1993, 2015) *JFE*. This is not a new paper.

**Notebook:** `notebooks/01b_gu_fama_french.ipynb` (homework, not run on the day)
**Sibling:** `notebooks/01a_gu_kelly_xiu_simplified.ipynb` (anonymous $x_j$)

---

# Characteristic OLS (not CAPM)

The classroom **FF** means Fama–French **characteristics**, in the cross-section, ranked:

| Name | Spirit |
|------|--------|
| `size` | SMB |
| `bm` | HML |
| `op` | RMW |
| `inv` | CMA |
| `mom` | Carhart (not in FF5) |

This is not $r_{it}=\alpha_i+\beta_i r_{m,t}$.

---

# Frozen protocol

The same as notebook `01a`:

1. Stock–month panel
2. Calendar train / val / test split
3. Predictive OOS $R^2$ against a forecast of 0
4. Long–short on $\hat r$

Only the **feature story** changes.

---

# Ladder in 01b

| Rung | Features |
|------|----------|
| **FF3_OLS** | size, bm |
| **OLS3_GKX** | size, bm, mom (GKX's own OLS-3: $R^2_{\text{OOS}}$ = 0.16%) |
| **FF5_OLS** | size, bm, op, inv |
| OLS-all / Ridge / RF / MLP | named FF + zoo $z_0$–$z_6$ |
| ORACLE_f | true $f$ (DGP cheat) |

The 1990s model is the first row, not a competing paper.

---

# Homework questions

1. OLS3_GKX vs FF3_OLS: adding `mom` changes almost nothing. Why? (In this DGP momentum enters only through `size × mom`.)
2. FF3 vs FF5 vs OLS-all: does the zoo help, or does it overfit?
3. Here RF and the MLP can beat the FF baselines because the DGP plants `op²` and `size × mom`. Is that a market fact?

---

# Takeaway

Gu–Kelly–Xiu means: keep the linear factor/characteristic baseline, then add the zoo and ML **under the same OOS rules**.

**Back:** notebook `01a` if you want the anonymous $x_j$ first.
