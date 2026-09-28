---
marp: true
paginate: true
size: 16:9
theme: default
title: Module A+ — Chen Pelger Zhu (2024)
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
footer: Module A+ · Chen–Pelger–Zhu (2024) · Management Science
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _footer: "" -->
<!-- cover -->
# Module A+
## Chen, Pelger, Zhu (2024)

Barbara Będowska-Sójka · Poznań University of Economics and Business

MSCA Doctoral Network Digital Finance · MSCA_DF_10 Introduction to AI for Financial Applications

![h:120](img/logo_digital.jpg)![h:88](img/logo_uep.png)

---

# Papers and materials

Chen, L., Pelger, M., & Zhu, J. (2024).
*Deep Learning in Asset Pricing.*
*Management Science*, 70(2), 714–750.

**After Gu and the robustness block.** 30 min, slides and discussion.
**Authors' code:** `github.com/LouisChen1992/Deep_Learning_in_Asset_Pricing`
**Homework:** `notebooks/04_chen_pelger_zhu_sketch.ipynb`

---

<!-- _class: card -->
<!-- card:cpz -->
# Paper card: Chen, Pelger & Zhu (2024)

| | *Management Science* 70(2): 714–750 |
|---|---|
| **Question** | Can a deep-learning stochastic discount factor (SDF), disciplined by no-arbitrage, price individual stocks better than pure return prediction? |
| **Data** | CRSP monthly, 1967–2016; 46 firm characteristics; 178 macro series. |
| **Method** | A GAN: a feed-forward net gives the SDF weights, an LSTM extracts a few macro states, and an adversarial net picks the test assets that are hardest to price. |
| **How it is tested** | Train 1967–86, validate 1987–91, test 1992–2016. Out-of-sample SDF Sharpe ratio, explained variation and pricing errors, against a forecasting benchmark. |
| **Main result** | Out-of-sample SDF Sharpe ratio of about 2.6 a year, almost twice the forecasting benchmark. It is still 1.73 when the 40% smallest stocks get zero weight. |
| **Watch for** | The loss targets average returns (first moments), not variance: the same distinction as $R^2$ vs GRS in our Fama–French notebook. |
| **Code & data** | Code on GitHub (LouisChen1992/Deep_Learning_in_Asset_Pricing); data need CRSP. |

---

# Why this paper after Gu

A pure prediction loss explains **variance** (a second moment).
The no-arbitrage condition targets **average returns** (a first moment).

It is the same distinction as $R^2$ vs GRS and mean $|\alpha|$ in notebook `01`.

**Question:** when does a finance constraint beat a pure ML loss?

---

# Design in one slide

- CRSP monthly, 1967–2016 · 46 firm characteristics · 178 macro series
- Train 1967–1986 · validate 1987–1991 · **test 1992–2016**
- Three networks linked by the no-arbitrage condition:
  - feed-forward → SDF weights
  - LSTM → a few macro **states**
  - adversarial network → the **test assets** that are hardest to price
- Out-of-sample SDF Sharpe ratio ≈ **2.6** per year, almost twice the forecasting benchmark (FFN)

---

# Gu vs Chen–Pelger–Zhu

| | Gu–Kelly–Xiu (2020) | Chen–Pelger–Zhu (2024) |
|---|---|---|
| Object | predict $E[r]$ | estimate the SDF |
| Objective | MSE / Huber; $R^2_{\text{OOS}}$ | conditional moments, min–max (GMM-style) |
| Test assets | none in estimation; deciles for evaluation | chosen **adversarially** |
| Macro | 8 predictors × characteristics | 178 series → LSTM states |
| Size robustness | challenged by Avramov et al. | see next slide |

---

# Size and trading frictions (published version)

Fig. 17: set the SDF weights to zero below a cutoff (no re-estimation, so these are **lower bounds**)

| Stocks removed | GAN annual Sharpe |
|----------------|-------------------|
| none | ≈ 2.6 |
| 40% smallest | 1.73 |
| 40% widest bid–ask spread | 2.07 |
| 40% least traded | 1.87 |

Fn. 44: GKX-style long–short portfolios lose about half their Sharpe ratio when value-weighted: "a clear indication that the performance of these portfolios heavily depends on small stocks."

---

# A replication dispute in print

**Avramov et al. (2023):** the CPZ signal's FF6 alpha is **71% lower** without microcaps.

**CPZ (fn. 45):** they "do not consider our SDF portfolio based on ω, but use the SDF loadings β to construct a long-short portfolio … Thus, they study different portfolios."

CPZ shared their data and estimated models with Avramov et al.

**Which portfolio tests the paper's claim?** Keep this question for Block D.

---

# Deconstruction prompts

1. What fails if we only minimize forecast MSE under a low SNR?
2. What do adversarial test assets buy intellectually?
3. Is this ML, or "econometrics with NN function classes"?
4. What would a replication need? (CRSP + characteristics, 178 macro series, GPU time, the authors' code)

---

# Homework sketch (notebook 04)

A toy illustration, **not** a replication:

- Start from Gu-style forecasts
- Add a simple penalty that encourages economically coherent long–short behaviour
- Compare pure-MSE ranking with constrained ranking on synthetic data

Put the penalty **inside** training, not after it.

---

# Takeaway

After the ML horse race, the frontier question is **which economic restrictions to encode in the objective**.

**Next:** Block D, replication and robustness as research questions
