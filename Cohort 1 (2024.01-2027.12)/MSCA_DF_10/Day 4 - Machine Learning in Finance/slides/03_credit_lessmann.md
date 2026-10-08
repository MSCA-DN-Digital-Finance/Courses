---
marp: true
paginate: true
size: 16:9
theme: default
title: Module C — Credit and the benchmark protocol
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
footer: Module C · Lessmann et al. (2015) · Gunnarsson et al. (2021) · Fuster et al. (2022)
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _footer: "" -->
<!-- cover -->
# Module C
## Credit: the benchmark protocol is the contribution

Barbara Będowska-Sójka · Poznań University of Economics and Business

MSCA Doctoral Network Digital Finance · MSCA_DF_10 Introduction to AI for Financial Applications

![h:120](img/logo_digital.jpg)![h:88](img/logo_uep.png)

---

# Papers and materials

Lessmann, S., Baesens, B., Seow, H.-V., & Thomas, L. C. (2015). *Benchmarking state-of-the-art classification algorithms for credit scoring: An update of research.* *EJOR*, 247(1), 124–136.

Gunnarsson, B. R., vanden Broucke, S., Baesens, B., Óskarsdóttir, M., & Lemahieu, W. (2021). *Deep learning for credit scoring: Do or don't?* *EJOR*, 295(1), 292–305.

Fuster, A., Goldsmith-Pinkham, P., Ramadorai, T., & Walther, A. (2022). *Predictably Unequal? The Effects of Machine Learning on Credit Markets.* *JF*, 77(1), 5–47.

**Live:** `notebooks/03_lessmann_credit_lab.ipynb`

---

# Domain shift

From markets → **credit decisions**

- Asymmetric costs: a bad loan granted ≠ a good client rejected
- Imbalance and calibration matter
- Governance and fairness pressure
- The loss function is **economic**

---

# Spot the flaw (5 min)

Zeng, Melville, Lang, Boier-Martin & Murphy (2008), *KDD*: predict whether an invoice will be paid late.

- 4 firms, invoices 2004–2005, 5 classes (on time … 90+ days late)
- Features include the **customer's payment history**
- "Experiments … were run using **10-fold cross validation**, and classification **accuracy** is reported"

**What is wrong with this evaluation?**

---

# Answer

- **Random folds** train on a customer's *future* invoices → leakage through history patterns
- **Accuracy** on imbalanced classes, against a majority-class baseline
- No cost of acting too early vs too late

This paper is the source of the AR task, **not** of current methods. (The AR notebook is optional homework.)

---

<!-- _class: card -->
<!-- card:lessmann -->
# Paper card: Lessmann, Baesens, Seow & Thomas (2015)

| | *European Journal of Operational Research* 247: 124–136 |
|---|---|
| **Question** | Do newer classifiers beat logistic regression (LR) for credit scoring when all of them follow one protocol? |
| **Data** | 8 retail credit data sets (690 to 150,000 applicants); 3 are public (German, Australian, Give Me Some Credit). |
| **Method** | 41 classifiers (individual, homogeneous and heterogeneous ensembles; 1,141 models), with the same preprocessing, tuning and Platt calibration for all. |
| **How it is tested** | N×2 cross-validation; six metrics (AUC, H-measure, partial Gini, Brier, KS, accuracy); Friedman test, then pairwise tests; cost curves against LR. |
| **Main result** | HCES-Bag ranks first, RF is the best homogeneous ensemble and ANN the best single classifier. LR is significantly worse. The most complex methods (dynamic selection) do worse than LR. Cost savings against LR average 3.4–5.7%. |
| **Watch for** | Random splits, no time dimension. The most accurate model is not always the most profitable. |
| **Code & data** | Three data sets are public; our lab reruns a mini version on them. |

---

# Lessmann: question & hypothesis

Do novel classifiers beat **logistic regression** for PD scorecards, and does the answer depend on the metric?

**Hypothesis:** under an identical protocol, advanced classifiers beat LR, and the gain is economically meaningful.

41 classifiers · 1,141 models · 8 datasets · 6 metrics

---

# Lessmann: data

| Name | Cases | Vars | Default rate | Public? |
|------|-------|------|--------------|---------|
| AC (Australian) | 690 | 14 | .445 | UCI |
| GC (German) | 1,000 | 20 | .300 | UCI |
| Th02 | 1,225 | 17 | .264 | on request |
| Bene 1 / Bene 2 | 3,123 / 7,190 | 27 / 28 | .667 / .300 | no |
| UK | 30,000 | 14 | .040 | no |
| PAK | 50,000 | 37 | .261 | PAKDD 2010 |
| GMC | 150,000 | 12 | .067 | Kaggle |

---

# Lessmann: protocol

- N×2 cross-validation with **random** splits ($N$ = 10 / 5 / 3 by dataset size)
- Meta-parameters tuned on an inner 5-fold CV, **per metric**
- No resampling for imbalance; Platt calibration
- Metrics: PCC, AUC, **H-measure**, partial Gini ($b = 0.4$), **Brier**, KS
- Friedman test on average ranks → Rom / Bergmann–Hommel post-hoc

---

# Lessmann: results

- **HCES-Bag** (hill-climbing ensemble selection with bootstrap sampling) is best overall; RF is the best homogeneous ensemble; ANN the best individual classifier
- **LR is significantly worse** than HCES-Bag, RF and ANN (Table 5)
- The most complex methods (dynamic ensemble selection) are **worse than LR**
- Expected error cost relative to LR: ANN −3.4%, RF −5.7%, HCES-Bag −4.8%
- At high cost ratios HCES-Bag loses its lead: the most accurate model is not the most profitable

---

# What the protocol does not do

1. **No time dimension.** Random N×2 CV assumes a stable population. Would the ranking survive an out-of-time split?
2. **It predates XGBoost.** Stochastic gradient boosting ranks mid-table.

Gunnarsson et al. (2021): **XGBoost** performs best, and deep networks do not repay their computational cost.

---

# Live lab: mini-Lessmann (25 min)

| Choice | Classroom |
|--------|-----------|
| Data | GC, AC (UCI) + GMC (Kaggle), three of Lessmann's eight |
| Split | 5×2 CV (GC, AC) · 3×2 CV (GMC, cached) |
| Models | LR, reg. LR, RF, gradient boosting (sklearn HGB), small MLP, simple average |
| Preprocessing | linear models and MLP: clip at 1st/99th percentile, log of skewed features, standardize |
| Tuning | live: fixed settings (< 1 min) · full: inner 5-fold CV, precomputed |
| Metrics | AUC, H-measure, partial Gini, Brier |
| Test | Friedman across datasets + Holm post-hoc |
| Economics | cost curve vs LR, $C(-\mid+)/C(+\mid-)$ = 2 … 50 |

---

# Same models, same data

GMC, AUC, 3×2 CV

| Preprocessing for linear models | LR | Reg. LR | MLP | RF |
|---|---|---|---|---|
| standardize only | 0.703 | 0.703 | 0.828 | 0.864 |
| clip + log + standardize | **0.858** | **0.858** | 0.855 | 0.864 |

GMC has extreme outliers and skewed counts. Trees do not care; LR does.

**Before claiming that ML beats LR, give LR a fair chance.**

---

# The lab's built-in lesson

With **3 datasets** the Friedman test sees only the largest gaps: p = 0.022 live, 0.074 after tuning.

No Friedman rejection, no pairwise claims (Demšar 2006).

That is why Lessmann used 8.

**Protocol choices decide what you can claim.**

---

<!-- _class: card -->
<!-- card:gunnarsson_fuster -->
# Paper card: Two more credit papers

| | Gunnarsson et al. (2021), *EJOR* 295(1) | Fuster et al. (2022), *JF* 77(1) |
|---|---|---|
| **Question** | Does deep learning pay off in credit scoring? | When lenders move from logit to ML, who gains and who loses? |
| **Method** | A Lessmann-style benchmark of deep networks against XGBoost, random forests and LR. | US mortgage default prediction, logit vs random forest, fed into an equilibrium model of loan pricing. |
| **Main result** | XGBoost performs best; deep networks do not repay their computational cost. | "Black and Hispanic borrowers are disproportionately less likely to gain." ML raises disparity mainly through flexibility, not by inferring race. |
| **Watch for** | A benchmark update six years later: which rankings survive? | Better prediction is not a better outcome for every borrower. |

---

# Fuster et al. (2022): who gains?

Lenders move from logit to ML for mortgage default prediction.

> "Black and Hispanic borrowers are disproportionately less likely to gain from the introduction of machine learning."

In their equilibrium model, ML increases rate disparity between and within groups, mainly through **flexibility**, not by triangulating excluded characteristics.

---

# Discussion (10 min)

Your lab's winning model lowers expected cost by $x$%.

1. What would you need to know before deploying it?
2. Lessmann's hypothesis is about **methods**. Fuster's is about **markets**. Which one is a finance paper?
3. Accuracy ≠ welfare. Which metric would capture the difference?

---

# Cost matrix (Lessmann's convention)

|  | Predict good | Predict bad |
|--|--------------|-------------|
| Actually good | 0 | $C(+\mid-)$: good client rejected |
| Actually bad | $C(-\mid+)$: loss given default | 0 |

Fix $C(+\mid-) = 1$ and vary $C(-\mid+)$ from 2 to 50.
Bayes-optimal threshold → re-rank the models by **expected cost**, not AUC.

---

# Homework (½ page)

Write a **benchmark protocol** for a credit dataset you care about:

sample · leakage rules · split (random or out-of-time, and **why**) · tuning budget · primary metric · statistical test · kill criteria for complex models

Optional: the AR notebook (random vs chronological vs customer-grouped split).

---

# Takeaway

In credit, **the benchmark design is the contribution**.
A better prediction is not automatically a better outcome for borrowers.

**Next:** Chen–Pelger–Zhu, with economics inside the loss
