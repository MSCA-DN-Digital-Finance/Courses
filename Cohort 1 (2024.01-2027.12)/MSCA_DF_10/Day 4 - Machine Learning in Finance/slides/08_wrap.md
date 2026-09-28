---
marp: true
paginate: true
size: 16:9
theme: default
title: Wrap — seven moves
style: |
  section { font-size: 28px; }
  h1 { font-size: 40px; }
  table { font-size: 22px; }
  section.cover h1 { font-size: 50px; margin-bottom: 0; }
  section.cover h2 { font-size: 30px; font-weight: 400; color: #4a5568; margin-top: 6px; }
  section.cover p { font-size: 21px; color: #4a5568; margin: 6px 0; }
  section.cover p:last-of-type { position: absolute; bottom: 56px; left: 70px; margin: 0; }
  section.cover p:last-of-type img { margin-right: 44px; vertical-align: middle; }
footer: MSCA_DF_10 · Machine Learning in Finance · wrap
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _footer: "" -->
<!-- cover -->
# Wrap
## Seven moves

Barbara Będowska-Sójka · Poznań University of Economics and Business

MSCA Doctoral Network Digital Finance · MSCA_DF_10 Introduction to AI for Financial Applications

![h:120](img/logo_digital.jpg)![h:88](img/logo_uep.png)

---

# Day synthesis: seven moves

1. **Opener:** a prediction is not a test until you say what it would reject
2. **FF → Gu:** validation and economic metrics ≥ fancy models
3. **Avramov et al.:** *where* the alpha lives is part of the result
4. **Krauss:** a classifier is not a strategy without a label, a portfolio rule and frictions
5. **Lessmann / Fuster:** protocols make claims credible; accuracy ≠ welfare
6. **Chen–Pelger–Zhu:** put the economics into the loss
7. **Replication:** fix what counts as success before you run it

---

# One-liner wall

| Paper | One line |
|-------|----------|
| Gu | validation + economic metrics ≥ fancy models |
| Krauss | classifier ≠ strategy without a trading rule |
| Lessmann | boring protocols make claims credible |
| Fuster | a better prediction can be a worse outcome for some borrowers |
| Chen | constraints can beat a pure predictive loss |
| KMZ vs Nagel | ask what the model is actually doing |
| Zombies | label → information set → OOT → costs → explain → replicate |

---

# Homework options (pick one)

**A.** A 1–2 page deconstruction note on one core paper, with the **hypothesis** stated
**B.** A half-page Lessmann-style protocol for your dataset
**C.** Re-run `06_kmz_nagel` with $T = 60$ and $T = 120$
**D.** A sketch (bullets or code stub): add a finance penalty inside training (`04`)

---

# Thank you

Materials: your course folder (`notebooks/`, `data/`, `Reading_list.pdf`) · the slides are in slides/

Questions · office hours · next steps for your thesis designs
