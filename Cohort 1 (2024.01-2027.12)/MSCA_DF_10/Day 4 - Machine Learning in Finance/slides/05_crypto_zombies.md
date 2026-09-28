---
marp: true
paginate: true
size: 16:9
theme: default
title: Block E — Crypto Zombies (capstone)
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
footer: Block E · capstone · Będowska-Sójka, Wójcik, Pele · NAJEF
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _footer: "" -->
<!-- cover -->
# Block E: capstone (author case)
## Predicting crypto “zombies”

Barbara Będowska-Sójka · Poznań University of Economics and Business

MSCA Doctoral Network Digital Finance · MSCA_DF_10 Introduction to AI for Financial Applications

![h:120](img/logo_digital.jpg)![h:88](img/logo_uep.png)

---

# Papers and materials

Będowska-Sójka, B., Wójcik, P., & Pele, D. T. (2025).  
*Early warning systems for cryptocurrency markets: Predicting ‘zombie’ assets using machine learning.*  
*The North American Journal of Economics and Finance*, 81, 102543.  
DOI [10.1016/j.najef.2025.102543](https://doi.org/10.1016/j.najef.2025.102543)

---

<!-- _class: card -->
<!-- card:zombies -->
# Paper card: Będowska-Sójka, Wójcik & Pele (2025)

| | *North American Journal of Economics and Finance* 81: 102543 |
|---|---|
| **Question** | Which cryptocurrencies will become "zombies" (still listed but untradable) within the next 28 days? |
| **Data** | Weekly snapshots of cryptocurrencies listed for at least 210 days, 2015–2022; return, volume and market-cap features. |
| **Method** | Classical econometric baselines vs tree-based ML (random forests, boosting), with class-imbalance handling (downsampling, ROSE, SMOTE) and explainable-AI tools (permutation importance, partial dependence). |
| **How it is tested** | Out-of-time, walk-forward evaluation; balanced accuracy. |
| **Main result** | Random forests beat the classical models, with balanced accuracy of about 84% out of time. Volumes and past returns matter most. |
| **Watch for** | An early warning, not a price forecast: which error costs more, a missed zombie or a false alarm? |
| **Code & data** | Quantinar course and QuantLet code with the weekly snapshot CSV; some auxiliary files are not public. |

---

# Why this module closes the day

- Block D treated replication **from the outside**; here we see it **from the author's side**
- Live **author** paper: design choices you can defend
- Classification → **risk decision** (not alpha long–short)
- **Replicability**: Quantinar + QuantLet (public code; some aux files are not public)
- Adds **XAI** (importance, PDPs). Remember the opener: importance is not $\hat{\beta}$

---

# Economic question

Which cryptocurrencies are about to become **zombies** — still “existing” but **untradable** long enough that investors cannot exit?

Early warning ≠ price forecast.

---

# Label (paper)

- Horizon: zombie within the next **28 days**  
- Sample spirit: assets listed long enough to learn history (paper: ≥210 days; 2015–2022)  
- Discuss: definition of untradable / exchange coverage / delisting

---

# Features

- Return statistics  
- Trading volume  
- Market capitalisation  
- Asset-specific characteristics  

**Information set:** known before the warning window.

Paper finding to preview: **volumes** and **past returns** matter most.

---

# Validation & results (headline)

- **Out-of-time** evaluation  
- **Balanced accuracy** ≈ 84% OOT (paper)  
- Tree-based models (esp. **random forests**) beat classical econometrics  
- Imbalance handling appears in the QuantLet scripts (downsampling / ROSE / SMOTE)

---

# Model ladder → XAI

```
classical baselines → RF / boosting (xgb) → explain best model
```

QuantLet highlights:

- `Code/` — training variants + `04_summarize_the_results.R`  
- `5_XAI_for_best*.R` — permutation importance / PDP-style analysis

---

# Decision costs (discussion)

| Error | Investor / desk consequence |
|-------|-----------------------------|
| False negative | capital stuck in untradable asset |
| False positive | unnecessary exit / missed upside |

Same Lessmann lesson: pick the metric that matches the **loss**.

---

# Live materials

| Where | What |
|-------|------|
| [Quantinar · Cryptos Zombies](https://quantinar.com/course/749/cryptos-zombies) | PDF + video (optional backdrop) |
| `notebooks/05_crypto_zombies_csv_only.ipynb` | **Live classroom demo (CSV only)** |
| `experiments/Crypto_Zombies/workdir/.../all_symbols.csv` | public QuantLet data |
| Full `Code/*.R` | skip live (needs aux files) |

---

# Map to the rest of the day

| Earlier module | Bridge |
|----------------|--------|
| Krauss | classification scores → action |
| Credit (C) | default / early-warning flavour |
| Lessmann | fixed protocol + baseline discipline |
| Gu / Chen | different object (returns / SDF) |
| Replication (D) | what the public code reproduces, and what it does not |

---

# Replication from the author's side

| Question | This paper |
|----------|------------|
| What is public? | QuantLet: training variants, result summary, XAI scripts; weekly snapshot CSV |
| Does it run end to end? | No: the aux xlsx and `F_summary_*.R` are not in the public archive |
| Robustness in the package? | Not packaged separately |
| Where will classroom numbers differ? | single OOT window vs walk-forward |

**Exercise (5 min):** design the robustness appendix this replication package should contain.

---

# Do differently

1. 14 vs 28 vs 60-day zombie horizon  
2. Explicit cost-sensitive threshold  
3. Size / exchange filters  
4. Require stable XAI stories before model changes

---

# Takeaway

Crypto zombies are still the craft of the day:

**label → information set → out-of-time test → decision costs → explain → replicate.**

**Next:** Cakici (`07_cakici.md`), then wrap (`08_wrap.md`)
