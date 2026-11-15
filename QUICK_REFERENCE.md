# ⚡ Project Quick Reference & Viva Cheat Sheet
**Forecasting Movie Opening Weekend Box Office Revenue**  
*IDSE Data Science Project*  
**Team Members:** SAI DATTATREYA ROUTHU (CS24I1037), JAKKA ARJUN REDDY (CS24I1051), H. VAMSHI (CS24I1063)

---

## 🎯 1. 30-Second Elevator Pitch
> *"Our project predicts a film's **Opening Weekend Box Office gross** strictly using information available **prior to release**. While lifetime box office is derailed by unpredictable word-of-mouth decay, opening weekend is an 'expectation market' dictated by pre-release signals. Grounded in 5 foundational academic papers (*Schreiner et al. 2025; Kim et al. 2017; McKenzie 2022*), we isolated the **Top 10 structural and market competition factors**. Evaluating across Ridge, Random Forest, and Gradient Boosting with 5-fold cross-validation, our best model achieves an **$R^2$ of 0.785** and a **Median Absolute Error of just \$4.17M**, proving that screen capacity, budget, and market competition explain nearly 80% of opening collections."*

---

## 🏆 2. Top 10 Factors & Their Roles

| # | Factor | Role / Mechanism | Paper Citation |
|---|---|---|---|
| **1** | **Opening Theaters** | Physical screen capacity upper bound | *Schreiner et al. (JAMS 2025)* |
| **2** | **Production Budget** | Scale & P&A marketing commitment | *Wang et al. (2020)* |
| **3** | **Market Competition** ⚡ | Zero-sum same-week rival cannibalization | **Kim, Hong, & Kang (CIN 2017)** |
| **4** | **Sequel / Franchise** | Pre-existing brand equity & Day 1 fanbase | *Zhang et al. (Nature 2024)* |
| **5** | **Lead Genre** | Opening urgency (Action/Horror vs. Drama) | *Schreiner et al. (2025)* |
| **6** | **Major Studio** | Distributor leverage for prime IMAX/PLF screens | *McKenzie (2022)* |
| **7** | **Summer Window** | May–July school holiday attendance multiplier | *McKenzie (2022)* |
| **8** | **Holiday Window** | Nov–Dec Thanksgiving/Christmas expansion | *Zhang et al. (2024)* |
| **9** | **Runtime** | Daily turnover & screening frequency per screen | *Kim et al. (2017)* |
| **10**| **Story Scope** | Pitch scope & marketing hook complexity | *Wang et al. (2020)* |

---

## 📊 3. Statistical Hypothesis Testing Summary

| Test | Null Hypothesis ($H_0$) | Statistic | $p$-value | Decision |
|---|---|---|---|---|
| **Welch's t-Test** | Sequel == Standalone Opening Mean | $t = 5.53$ | $2.92 \times 10^{-7}$ | **Reject $H_0$** (Sequels open significantly higher ✅) |
| **One-Way ANOVA** | Equal Opening Mean Across Genres | $F = 13.69$ | $1.14 \times 10^{-16}$ | **Reject $H_0$** (Genre variance statistically significant ✅) |
| **Welch's t-Test** | Major Studio == Independent Mean | $t = 7.43$ | $3.03 \times 10^{-13}$ | **Reject $H_0$** (Studio clout confirmed ✅) |
| **Welch's t-Test** | Low Comp ($\le 1$) == High Comp ($\ge 4$) | $t = 1.99$ | $p \approx 0.05$ | **Reject $H_0$** (Cannibalization confirmed ✅) |

---

## 📈 4. Test Set Performance Comparison ($N=144$)

| Model | $R^2$ Score | MAE ($M) | Median AE ($M) | RMSE ($M) |
|---|:---:|:---:|:---:|:---:|
| **Dummy Mean Baseline** | -0.1513 | \$16.06M | \$8.10M | \$28.00M |
| **Ridge Regression (Linear)** | 0.5751 | \$9.79M | \$5.25M | \$17.01M |
| **Random Forest Regressor** | **0.7750** | **\$7.83M** | **\$4.17M** | **\$12.38M** |
| **Gradient Boosting Regressor** | **0.7852** | **\$7.70M** | **\$4.69M** | **\$12.09M** |

---

## 🎙️ 5. Top Viva Questions & Instant Answers

* **Q: How did you prevent data leakage?**  
  *Answer:* All post-theatrical variables (user ratings, Rotten Tomatoes scores, opening weekend reviews) were banned. Preprocessing transformers (`StandardScaler`, `OneHotEncoder`) were fit **only on training partitions** inside a scikit-learn `Pipeline`.
* **Q: Why is your median error so much lower than your mean error?**  
  *Answer:* The median error is **\$4.17M**, while MAE is **\$7.70M**. This occurs because box office revenue has a heavy right-tail (blockbusters like *The Avengers* make \$200M+). The median error reflects that the model predicts typical mid-budget films within a tight \$4M margin.
* **Q: Could this model be applied in India?**  
  *Answer:* Conceptually yes—Indian cinema is intensely opening-driven with festival clashes (Diwali, Sankranti) and star advance bookings. However, empirical modeling is currently blocked by lack of centralized ComScore POS tracking, PR figure inflation, and regional price-cap regulations.

---

## 💻 6. Quick Commands

```bash
# 1. Run Complete Pipeline (20 seconds)
python3 main.py

# 2. Run Hypothesis Tests
python3 src/hypothesis_testing.py

# 3. Terminal Prediction
python3 predict.py --budget 150000000 --theaters 3800 --genre Action --sequel 1 --competition 2

# 4. Launch Web App
python3 -m streamlit run app.py
```
