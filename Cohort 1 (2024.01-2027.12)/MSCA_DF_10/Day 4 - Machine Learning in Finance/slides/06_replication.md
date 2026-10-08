---
marp: true
paginate: true
size: 16:9
theme: default
title: Block D — Replication and robustness
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
footer: Block D · Harvey–Liu–Zhu (2016) · Jensen–Kelly–Pedersen (2023) · Kelly–Malamud–Zhou (2024) vs Nagel (2025)
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _footer: "" -->
<!-- cover -->
# Block D
## Replication & robustness as research questions

Barbara Będowska-Sójka · Poznań University of Economics and Business

MSCA Doctoral Network Digital Finance · MSCA_DF_10 Introduction to AI for Financial Applications

![h:120](img/logo_digital.jpg)![h:88](img/logo_uep.png)

---

# Papers and materials

Harvey, C. R., Liu, Y., & Zhu, H. (2016). *…and the Cross-Section of Expected Returns.* *RFS*, 29(1), 5–68.
Jensen, T. I., Kelly, B., & Pedersen, L. H. (2023). *Is There a Replication Crisis in Finance?* *JF*, 78(5), 2465–2518.
Kelly, B., Malamud, S., & Zhou, K. (2024). *The Virtue of Complexity in Return Prediction.* *JF*, 79(1), 459–503.
Nagel, S. (2025). *Seemingly Virtuous Complexity in Return Prediction.* NBER WP 34104.

**Live:** `notebooks/06_kmz_nagel.ipynb`

---

# Back to the opener's table

Every row today was a **claim**:

- nonlinear interactions carry risk-premium information (Gu)
- past prices predict returns (Krauss)
- advanced classifiers beat LR (Lessmann)
- no-arbitrage structure improves pricing (CPZ)

**What would it take to replicate one of them? And what counts as success?**

---

<!-- _class: card -->
<!-- card:hlz_jkp -->
# Paper card: What counts as replication?

| | Harvey, Liu & Zhu (2016), *RFS* 29(1) | Jensen, Kelly & Pedersen (2023), *JF* 78(5) |
|---|---|---|
| **Question** | After hundreds of tested factors, what t-statistic should a new factor clear? | Is there a replication crisis in finance? |
| **Data** | 316 published factors. | 153 factors in 93 countries; US data from 1926. |
| **Method** | Multiple-testing adjustments (Bonferroni, Holm, BHY). | Replication = a significant CAPM alpha in the original direction; a Bayesian hierarchical model shrinks each factor toward its cluster. |
| **Main result** | A new factor should clear t > 3.0, not 2.0. | The replication rate (→ poll in class). |
| **Watch for** | The hurdle depends on how many hypotheses the field has already tried. | What counts as "replicated"? Fix the definition before you test. |
| **Code & data** | — | Factors at jkpfactors.com; code on GitHub (bkelly-lab/ReplicationCrisis). |

---

# Harvey, Liu & Zhu (2016)

- They catalogue **316** factors
- After that much testing, $t > 2$ is not a meaningful hurdle
- Proposal: $t > 3.0$ for new factors, using multiple-testing adjustments

**The hurdle depends on how many hypotheses the field has already tried.**

---

# Jensen, Kelly & Pedersen (2023): design

- **153 factors, 93 countries**; US data from 1926
- **Replication** = a significant **CAPM alpha** in the original direction
- A Bayesian hierarchical model (empirical Bayes): each factor shrinks toward its cluster, using all factors jointly
- Data: `jkpfactors.com` · Code: `github.com/bkelly-lab/ReplicationCrisis`

---

# Jensen, Kelly & Pedersen (2023): results

| Definition | US replication rate |
|------------|---------------------|
| JKP, Bayesian | **82.4%** |
| JKP, Benjamini–Yekutieli (critical $t \approx 2.7$) | 75.6% |
| Hou, Xue & Zhang (2020), their definitions | 35% |

13 themes; most matter in the tangency portfolio.

---

# Why 82% here and 35% there? (3 min)

List the choices that differ:

- raw return vs **CAPM alpha**
- treatment of **microcaps** and the weighting
- the **multiple-testing** correction

**The replication rate is a function of the definition.**
Choose the definition **before** you test. That is hypothesis development.

---

<!-- _class: card -->
<!-- card:kmz -->
# Paper card: Kelly, Malamud & Zhou (2024)

| | *Journal of Finance* 79(1): 459–503 |
|---|---|
| **Question** | Can a model with far more parameters than observations time the stock market better out of sample? |
| **Data** | Monthly US market excess return, 1926–2020; 15 predictors (14 Welch–Goyal variables plus the lagged market return). |
| **Method** | Random Fourier features of the predictors (up to $P$ = 12,000) in ridge regression on a rolling 12-month window, averaged over 1,000 random draws. Theory shows why complexity can help. |
| **How it is tested** | An out-of-sample timing strategy (forecast × return) over 1,091 months: Sharpe ratio, alpha against the market and $R^2_{\text{OOS}}$, plotted against complexity $P/T$. |
| **Main result** | The "virtue of complexity": timing performance rises with $P/T$, even when $R^2_{\text{OOS}}$ is negative. Information ratio about 0.3, alpha t = 2.6–2.9. |
| **Watch for** | With 12 observations and 12,000 parameters, what can the model actually learn? Returns are scaled by their trailing volatility. |
| **Code & data** | Welch–Goyal data are public; community replications exist on GitHub. |

---

# Kelly, Malamud & Zhou (2024): the claim

**Theory:** out-of-sample timing performance can *rise* with complexity $P/T$, even when $R^2_{\text{OOS}} < 0$.

**Empirics:**
- target: monthly market excess return
- $K = 15$ predictors: 14 Welch–Goyal variables + the lagged market return
- random Fourier features, with $\omega_i \sim N(0, I)$ and $\gamma = 2$:

$$
z_t=\sqrt{2/P}\,\big[\cos(\gamma\omega_i'x_t),\ \sin(\gamma\omega_i'x_t)\big]_{i=1}^{P/2}
$$

- $P$ up to 12,000 · **rolling $T = 12$** · ridge $z \in \{10^{-3},\dots,10^{3}\}$ · returns scaled by trailing volatility

---

# Live 1: the "virtue of complexity" curve

`06_kmz_nagel.ipynb` §1–2 (precomputed)

- timing strategy return: $\hat r_{t+1} \times r_{t+1}$
- plot the annualized Sharpe ratio and $R^2_{\text{OOS}}$ against $P/T$, one line per $z$

Ours (ridgeless): the Sharpe ratio rises from −0.10 to 0.37. The dip at $P/T = 1$ is the interpolation threshold, which KMZ's theory predicts.

**Now: what is the model actually doing?**

---

<!-- _class: card -->
<!-- card:nagel -->
# Paper card: Nagel (2025)

| | NBER Working Paper 34104 |
|---|---|
| **Question** | What does KMZ's high-complexity model actually do with a 12-month window? |
| **Data** | KMZ's replication data: the market return and the same 15 predictors. |
| **Method** | Shows that the ridgeless random-feature forecast is close to a Gaussian kernel regression, i.e. a weighted average of the last 12 returns. Builds a simple volatility-timed momentum benchmark; runs a placebo with simulated reversals and a bootstrap of the predictors. |
| **How it is tested** | Alphas and information ratios against the market; spanning regressions of the KMZ strategy on the kernel and momentum strategies. |
| **Main result** | Information ratios: KMZ strategy 0.255, kernel 0.306, vol-timed momentum 0.388. Given the kernel strategy, the KMZ alpha is zero. Placebo: → poll in class. |
| **Watch for** | The numbers replicate; the interpretation changes. Did Nagel refute the theory or its empirical reading? |
| **Code & data** | Public data; our notebook 06 rebuilds the main tests. |

---

# Nagel (2025): the reinterpretation

With $T = 12$ and $P \gg T$, the ridgeless RFF forecast ≈ **Gaussian kernel regression**:

$$
\hat r_{t+1} \approx k(x_t, X)\,K(X, X)^{-1}\, r,
\qquad k(x, x') = e^{-\frac{\gamma^2}{2}\lVert x - x'\rVert^2}
$$

This is a weighted average of the **last 12 returns**, with weights set by how similar today's predictors are to each past month's.

In effect it is a **volatility-timed momentum** strategy that happened to do well.

Nagel also drops KMZ's standardization of returns by trailing volatility: on its own, that step can create spurious predictability (his Appendix A).

---

# Live 2: Nagel's evidence ($T = 12$, $P = 12{,}000$)

| Test (1930–2020) | Nagel | Ours |
|------|--------|------|
| Correlation, RFF vs kernel forecast | 0.93 | 0.97 |
| IR: RFF / kernel / vol-timed momentum | 0.255 / 0.306 / 0.388 | 0.283 / 0.258 / 0.384 |
| RFF alpha $t$, given the kernel strategy | −0.12 | 1.33 |
| RFF alpha $t$, given vol-timed momentum | 0.95 | 1.32 |
| Bootstrapped predictors: IR | 0.228 (vs 0.255) | not run |

Vol-timed momentum replicates almost exactly and spans the RFF strategy. The kernel spans it less well in our data ($t$ falls from 1.88 to 1.33 as the RFF draws rise from 20 to 100; Nagel uses 1,000).

---

# Live 3: placebo

Add noise with **reversals** to the returns, $\tilde r_t = r_t + \xi_t - 0.2\,\xi_{t-1} - 0.2\,\xi_{t-2}$, keep the other 14 predictors, and re-run.

→ The RFF strategy **loses money**: Nagel $t = -1.84$; ours $t = -2.02$, and 19 of 20 simulated paths lose.

It does not learn the sign of the dynamics. It **imposes** momentum.

---

# After publication: 2021–2025

| IR, 60 months | RFF | Kernel | Vol-timed momentum |
|---|---|---|---|
| Ours | −0.20 | −0.19 | 0.02 |

None of the strategies has earned anything since the sample ended.

But 60 months have little power: even if the true IR were 0.28, the expected $t$ would be about $0.28 \times \sqrt{5} \approx 0.6$.

**Is this evidence against KMZ, or no evidence at all?**

---

# Discussion (5 min)

1. Did Nagel refute KMZ's **theory** or their **empirical interpretation**?
2. Which hypothesis did KMZ's empirical test actually test?
3. Which single diagnostic would you add to **your** paper to pre-empt a critique like this?

---

# Takeaway

A replication is a hypothesis test about the paper.
**Fix what counts as success before you run it.**

Homework: re-run `06` with $T = 60$ and $T = 120$. Does the momentum reading survive?

**Next:** Block E, replication from the author's side
