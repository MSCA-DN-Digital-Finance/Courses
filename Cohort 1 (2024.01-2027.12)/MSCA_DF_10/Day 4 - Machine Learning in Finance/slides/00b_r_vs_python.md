---
marp: true
paginate: true
size: 16:9
theme: default
title: R vs Python — MSCA_DF_10, Machine Learning in Finance
style: |
  section { font-size: 28px; }
  h1 { font-size: 40px; }
  table { font-size: 22px; }
  section.cover h1 { font-size: 50px; margin-bottom: 0; }
  section.cover h2 { font-size: 30px; font-weight: 400; color: #4a5568; margin-top: 6px; }
  section.cover p { font-size: 21px; color: #4a5568; margin: 6px 0; }
  section.cover p:last-of-type { position: absolute; bottom: 56px; left: 70px; margin: 0; }
  section.cover p:last-of-type img { margin-right: 44px; vertical-align: middle; }
footer: Framing · tools · R vs Python
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _footer: "" -->
<!-- cover -->
# Tools interlude
## R vs Python, without the holy war

Barbara Będowska-Sójka · Poznań University of Economics and Business

MSCA Doctoral Network Digital Finance · MSCA_DF_10 Introduction to AI for Financial Applications

![h:120](img/logo_digital.jpg)![h:88](img/logo_uep.png)

---

# R vs Python: what to expect today

Most of you code in **Python**.  
Some key finance / QuantLet pipelines (incl. Crypto Zombies) are in **R**.

**Today everything runs in Python.** If you work in R, the design carries over line by line; only the package names change.

---

# What actually matters

The scarce skill is **research design**:

label · information set · OOT validation · economic metric · leakage

Language is secondary — as long as you can reproduce the design.

---

<style scoped>
  table { font-size: 19px; }
  section p { font-size: 23px; }
</style>

# Tooling map: today vs the papers vs your thesis

| Task | Today | In the papers | In your own work |
|---|---|---|---|
| Penalised regression | `sklearn` | glmnet (R), sklearn | `sklearn` |
| Random forest, boosting | `sklearn` | H2O in R (Krauss et al.) | `lightgbm`, `xgboost` |
| Neural nets | `sklearn` MLP | TensorFlow / Keras (GKX, CPZ) | `torch` |
| Economic structure in the loss | `numpy` sketch (`04`) | TensorFlow (Chen–Pelger–Zhu) | `torch` |
| Variable importance | permutation | SHAP, gradient-based | `shap` |
| Inference on returns | `numpy` | Newey–West, bootstrap | `statsmodels`, `arch` |

Small stack on purpose: it installs in minutes and every live run ends in under two. **No conclusion today depends on the framework.**

---

# Environment hygiene

Our `requirements.txt` did not list `scipy`. Two notebooks import it; it arrived only as a **scikit-learn dependency**. Everything ran, so nothing looked wrong.

- An implicit dependency is the most common reason a replication package "works on my machine".
- The test that finds it: **fresh environment, install from the file, run everything**.
- Ship the environment file with the code, and say which Python you used.

We come back to this in Block D, where we ask what makes a result replicable.

---

# Practical split

| Lean **Python** | Lean **R** |
|-----------------|------------|
| sklearn / PyTorch workflows | glm / glmnet / ranger idioms |
| Industry & CS collaborators | Many academic finance scripts |
| APIs, dashboards, DL | Tidy diagnostics & CRAN vignettes |
| Today's live notebooks | The QuantLet package behind Block E |

---

# Where the files live

```text
notebooks/*.ipynb   ← everything we run today, in Python
data/               ← the data, with precomputed results in data/cache/
scripts/            ← the slow steps, precomputed
```

The Crypto Zombies replication package (Block E) is **R**, from QuantLet; today's classroom version of it is **Python**.

---

# Classroom rule

1. Live coding today is **Python only**.  
2. If you work in R, the design translates line by line: label, split, metric.  
3. Grade / discuss **design**, not package taste.

---

# One-liner

> Use Python for the stack you ship; use R when the literature / QuantLet already did;  
> always defend the **validation and the loss**, not the logo on the IDE.
