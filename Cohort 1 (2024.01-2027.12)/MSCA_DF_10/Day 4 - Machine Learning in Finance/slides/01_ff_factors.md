---
marp: true
paginate: true
size: 16:9
theme: default
title: Module A opener — FF factors on 50 names
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
footer: Module A · Fama–French factors · real 50-name panel
---

<!-- _class: cover -->
<!-- _paginate: false -->
<!-- _footer: "" -->
<!-- cover -->
# Module A (opener)
## Fama–French factors on a 50-name panel

Barbara Będowska-Sójka · Poznań University of Economics and Business

MSCA Doctoral Network Digital Finance · MSCA_DF_10 Introduction to AI for Financial Applications

![h:120](img/logo_digital.jpg)![h:88](img/logo_uep.png)

---

<!-- _class: card -->
<!-- card:ff -->
# Paper card: Fama & French (2015)

| | *Journal of Financial Economics* 116: 1–22 |
|---|---|
| **Question** | Do profitability (RMW) and investment (CMA) factors, added to the three-factor model, explain average stock returns better? |
| **Data** | US stocks, July 1963 – December 2013 (606 months); portfolios sorted on size, B/M, profitability and investment (25 or 32 per sort). |
| **Method** | Time-series regressions of portfolio excess returns on the factors. |
| **How it is tested** | Intercepts, not $R^2$: the GRS test, the average absolute intercept, and the share of the cross-section of expected returns left unexplained. |
| **Main result** | The five-factor model beats FF3 and explains 71–94% of the cross-section variance of expected returns, yet GRS rejects every model. HML becomes redundant. Main failure: small stocks that invest a lot despite low profitability. |
| **Watch for** | The model is judged on average returns (intercepts), not on explained variance. In our notebook: does a 50-stock daily panel have the power to reject? |
| **Code & data** | Factors and portfolios are free in Ken French's data library. |

---

# Fama–French as a **factor** model

Fama, E. F., & French, K. R. (1993). *Common risk factors in the returns on stocks and bonds.* *JFE*, 33(1), 3–56.

Fama, E. F., & French, K. R. (2015). *A five-factor asset pricing model.* *JFE*, 116(1), 1–22.

This uses factor returns, not firm-level book-to-market.

**Live:** `notebooks/01_ff_factors_real.ipynb`
**Data:** `krauss_sp500_daily.csv` + `ff_daily_factors.csv`

---

# One factor path, 50 betas

$$
r_{i,t}-r_{f,t} = \alpha_i + \beta_i'\mathrm{FF}_t + \varepsilon_{i,t}
$$

| Same for all stocks | Stock-specific |
|---------------------|----------------|
| Mkt-RF, SMB, HML, … | $\alpha_i,\ \beta_i$ |

Ken French library → one row per **day**.

---

# Not the Gu target

| `01a` / `01b` | `01` |
|---------------|------|
| Predict $r_{t+1}$ from characteristics | Explain $r_t$ with **today's** factors |
| Predictive OOS $R^2$ | Explanatory $R^2$ (betas frozen) |

Do not mix the two $R^2$.

---

# How FF judge a model: intercepts, not $R^2$

$R^2$ measures variance explained. An asset pricing model is judged on **average returns** explained, so FF (2015) test whether all $\alpha_i = 0$:

$$
\mathrm{GRS} = \frac{T-N-L}{N}\,
\frac{\hat{\alpha}'\hat{\Sigma}^{-1}\hat{\alpha}}{1+\bar{\mu}'\hat{\Omega}^{-1}\bar{\mu}}
\sim F(N,\,T-N-L)
$$

Report GRS **and** mean $|\hat{\alpha}_i|$. In our notebook GRS does **not** reject (FF3: $p \approx 0.05$ in 2015–19, $0.28$ in 2020–23), yet mean $|\hat{\alpha}_i| \approx 8\%$ a year. Daily returns are noisy: large alphas can be jointly insignificant.

---

# Frozen protocol (still)

- Calendar train / test split (e.g. through 2019 / from 2020)
- Estimate $\beta$ on the training period only
- Test: $\widehat{r-r_f}=\hat\beta_{\mathrm{train}}'\mathrm{FF}_t$
- FF3 vs FF5: compare **GRS** and mean $|\alpha|$ in the **test** period, not only $R^2$

---

# Who are the 50 names?

Today's large S&P 500 firms, downloaded from Yahoo.

We picked them **because they survived and grew**, so their $\hat{\alpha}_i$ are biased upward.

This has nothing to do with the factor model. It is **survivorship**, and we meet it again in Krauss.

---

# Then the ML (same notebook, §8)

The features are known **yesterday**: lagged FF factors + own return lags.
One pooled model: OLS → Ridge → RF.

Predictive $R^2$ vs a forecast of 0: $\approx 0$.
Contemporaneous FF $R^2$: $\approx 0.45$.

A high $R^2$ with today's factors is **not** a forecast.

---

# Takeaway

FF OLS is attribution, judged by intercepts. Ridge/RF on lags is the ML forecast.
Gu's next move is a **characteristic zoo** and a monthly horizon, not a deeper fit of today's SMB.

**Next:** `01a` (Gu)
