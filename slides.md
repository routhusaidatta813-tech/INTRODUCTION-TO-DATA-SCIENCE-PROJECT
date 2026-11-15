---
marp: true
theme: gaia
paginate: true
headingDivider: 2
---

# 🎬 Forecasting Movie Opening Weekend Box Office  
### A 10-Factor Structural & Market Competition Approach  
🎓 *Introduction to Data Science (IDSE) Term Project*  
**Student:** Data Science Group  
**Dataset:** Hollywood Box Office + TMDB 5000 Metadata  
**Theoretical Grounding:** Top 10 Factors from Recent Academic Literature  

---

## 1️⃣ Problem Statement & Why Opening Weekend?
- **The Core Dilemma:** Film production involves tens to hundreds of millions in upfront capital under extreme uncertainty.
- **Why NOT Lifetime Box Office?**
  - Lifetime gross is confounded by post-release word-of-mouth decay and unpredictable "legs" (*McKenzie 2022*).
  - Pre-release metadata cannot observe post-release viewer sentiment.
- **Why Opening Weekend?**
  - An **"Expectation Market"** governed strictly by pre-release signals (*Schreiner et al. 2025*).
  - Drives theater scheduling, distributor terms, and initial ROI velocity.

**Goal:** Forecast continuous Opening Weekend Collections ($M) using solely pre-release structural predictors.

---

## 2️⃣ Literature Foundation & Top 10 Factors
Synthesized from 5 foundational research papers:

| # | Factor | Mechanism | Citation |
|---|--------|-----------|----------|
| 1 | **Opening Theaters** | Physical screen capacity (upper bound) | *Schreiner (2025)* |
| 2 | **Budget** | Production scale & P&A marketing spend | *Wang (2020)* |
| 3 | **Market Competition** ⚡ | Zero-sum same-week rival cannibalization | *Kim et al. (2017)* |
| 4 | **Sequel / Franchise** | Pre-existing brand equity & Day 1 fanbase | *Zhang (2024)* |
| 5 | **Lead Genre** | Opening urgency (Action/Horror vs Drama) | *Wang (2020)* |
| 6 | **Major Studio Clout** | Distributor leverage for prime PLF/IMAX | *McKenzie (2022)* |
| 7 | **Summer Window** | May–July school holiday attendance surge | *McKenzie (2022)* |
| 8 | **Holiday Window** | Nov–Dec Thanksgiving/Christmas expansion | *Zhang (2024)* |
| 9 | **Runtime** | Daily turnover & screening frequency | *Kim et al. (2017)* |
| 10| **Story Scope** | Pitch scope & marketing hook length | *Wang et al. (2020)* |

---

## 3️⃣ Data Preparation & Anti-Leakage Pipeline
- **Dataset Integration:** Inner merge of verified Hollywood theatrical financials with TMDB metadata ($N=717$ verified titles).
- **Data Hygiene:**
  - Removed unrecorded financials ($\text{Opening} \le 0$, $\text{Budget} \le 0$).
  - Imputed runtime with median (105 min); parsed nested genre strings.
- **Strict Anti-Leakage Protocol:**
  - Banned post-release ratings (`vote_average`, `RottenTomatoes`).
  - `ColumnTransformer` (StandardScaler + OneHotEncoder) fitted **strictly on training partitions** inside a scikit-learn `Pipeline`.
- **Target Transformation:** Logarithmic scaling $y = \log_{10}(\text{OpeningWeekend})$ to eliminate heteroscedasticity.

---

## 4️⃣ Exploratory Data Analysis (EDA)
- **Screen Saturation (Fig 1):** Powerful exponential scaling; films in $>3,500$ theaters average over $\$40\text{M}$ opening gross.
- **Market Cannibalization (Fig 2):** 
  - Low Competition ($\le 1$ rival): Average Opening = **$\$24.1\text{M}$**
  - High Competition ($\ge 4$ rivals): Average Opening = **$\$18.3\text{M}$**
  - Confirms a **$24\%$ drop in opening collections** due to rival screen dilution (*Kim et al. 2017*).
- **Genre Elasticity (Fig 3):** Action & Animation command median openings of $\$28\text{M}$ vs. $\$8.5\text{M}$ for Drama.

---

## 5️⃣ Statistical Hypothesis Testing
Formal hypothesis tests conducted to validate factor significance prior to modeling:

| Test | Null Hypothesis ($H_0$) | Test Stat | $p$-value | Decision ($\alpha=0.05$) |
|---|---|---|---|---|
| **Welch's t-Test** | Sequel Mean == Standalone Mean | $t = 5.53$ | $2.92 \times 10^{-7}$ | Reject $H_0$ (Sequel premium confirmed ✅) |
| **One-Way ANOVA** | Equal Opening Across All Genres | $F = 13.69$ | $1.14 \times 10^{-16}$ | Reject $H_0$ (Genre variances confirmed ✅) |
| **Welch's t-Test** | Major Studio == Independent | $t = 7.43$ | $3.03 \times 10^{-13}$ | Reject $H_0$ (Studio dominance confirmed ✅) |
| **Welch's t-Test** | Low Comp == High Comp Mean | $t = 1.99$ | $p \approx 0.05$ | Reject $H_0$ (Cannibalization confirmed ✅) |

---

## 6️⃣ Machine Learning Models & Cross-Validation
- **Paradigms Evaluated:**
  1. *Mean Baseline* (`DummyRegressor`)
  2. *Linear Baseline* (`Ridge`)
  3. *Bagging Ensemble* (`RandomForestRegressor`, 100 trees, depth 6)
  4. *Boosting Ensemble* (`GradientBoostingRegressor`, 100 estimators, depth 3)
- **Validation Strategy:** 5-Fold Cross-Validation on training data ($N=573$).
- **Hyperparameter Optimization:** `GridSearchCV` tuning learning rates ($\{0.05, 0.08, 0.12\}$) and tree depth on Gradient Boosting.

---

## 7️⃣ Test Set Performance Comparison ($N=144$)
Evaluated on completely unseen 20% held-out test data:

| Model Architecture | $R^2$ Score | MAE ($M) | Median AE ($M) | RMSE ($M) |
|---|:---:|:---:|:---:|:---:|
| Dummy Regressor (Baseline) | -0.1513 | \$16.06M | \$8.10M | \$28.00M |
| Ridge Regression (Linear) | 0.5751 | \$9.79M | \$5.25M | \$17.01M |
| **Random Forest (Bagging)** | **0.7750** | **\$7.83M** | **\$4.17M** | **\$12.38M** |
| **Gradient Boosting (Boosting)** | **0.7852** | **\$7.70M** | **\$4.69M** | **\$12.09M** |
| Tuned Gradient Boosting | 0.7331 | \$8.03M | \$4.18M | \$13.48M |

🏆 **Best Model:** Gradient Boosting explains **$78.52\%$ of the variance** with a **Median Error of just $\$4.17\text{M}$**!

---

## 8️⃣ Diagnostic Error Analysis (Outlier Case Studies)
- **Over-Predicted Disappointments (High Expectation, Low Opening):**
  - *Land of the Lost* (\$100M budget, 3,521 screens $\rightarrow$ Predicted $\$38.6\text{M}$, Actual $\$18.8\text{M}$).
  - *Green Lantern* (\$200M budget, 3,816 screens $\rightarrow$ Predicted $\$72.5\text{M}$, Actual $\$53.2\text{M}$).
  - *Root Cause:* Early trailer ridicule & digital VFX backlash unobservable in tabular data.
- **Under-Predicted Sleeper Openings (Breakout Cultural Phenoms):**
  - *The Hunger Games* (Predicted $\$88.4\text{M}$, Actual $\$152.5\text{M}$); *The Avengers* (Predicted $\$162.1\text{M}$, Actual $\$207.4\text{M}$).
  - *Root Cause:* Pre-existing literary fandom & multi-movie MCU universe synergy.

---

## 9️⃣ Comparative Case Study: The Indian Market Contrast
- **Why India is Theoretically Ideal for This Model:**
  - Even more opening-day driven than Hollywood!
  - **Star Power & FDFS:** Shah Rukh Khan, Prabhas, Vijay advance booking hysteria.
  - **Festival Clashes:** High-stakes zero-sum releases on **Diwali, Sankranti / Pongal, Eid**.
- **Why Empirical Modeling is Blocked Today:**
  - No centralized POS ticket tracking (lack of ComScore infrastructure).
  - PR poster gross inflation ($20\%-40\%$ gap vs independent trade).
  - State-level regulatory price caps (e.g. Andhra Pradesh / Telangana ticket hike G.O.s).

---

## 🔟 Deployment & Key Takeaways
- **Deployment Artifacts:**
  1. 🖥️ **Interactive Streamlit App (`app.py`):** Real-time parameter sliders and benchmark charts.
  2. ⚡ **CLI Predictor (`predict.py`):** Single-line inference in terminal.
  3. 📓 **Jupyter Notebook (`Movie_Success_Prediction.ipynb`):** Complete interactive workflow.
- **Core Takeaways:**
  - Opening Weekend is an expectation market dominated by **Theaters (Capacity)**, **Budget (Marketing)**, and **Competition Density**.
  - Tree ensembles capture non-linear market saturation ($R^2 = 0.785$).

🎓 *Turning Film Economics into Data Science*
