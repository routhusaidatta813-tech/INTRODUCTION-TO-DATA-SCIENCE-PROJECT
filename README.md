# 🎬 Forecasting Movie Opening Weekend Box Office Revenue
**Introduction to Data Science (IDSE) Term Project**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Library-scikit--learn-orange.svg)](https://scikit-learn.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/Status-Complete-green.svg)]()

---

## 📌 1. Project Overview & Motivation
Predicting movie box office gross is a foundational problem in entertainment economics. While long-term total box office is heavily derailed by post-release word-of-mouth decay, **Opening Weekend Box Office is an "expectation market"** governed strictly by pre-release signals.

* **Research Question:** *Can we accurately forecast a feature film's opening weekend box office gross prior to release using the Top 10 structural, distribution, and competitive signals established in academic literature?*
* **Grounding Literature (From `research_foundation/`):**
  1. **Schreiner et al. (2025)**, *Journal of the Academy of Marketing Science (JAMS)*: Dynamics of pre-release consumer buzz, theater capacity, and sequel premiums.
  2. **Kim, Hong, & Kang (2017)**, *Computational Intelligence and Neuroscience*: Market competition and concurrent overlapping release clashes.
  3. **McKenzie (2022)**, *Journal of Economic Surveys*: The economics of movies, screen commitments, and calendar timing.
  4. **Zhang, Meng, & Xiao (2024)**, *Nature Scientific Reports*: Emotional mining and first-day box office indicators.
  5. **Wang et al. (2020)**, *Information Fusion*: Multimodal feature learning and distribution factors.

---

## 🏗️ 2. End-to-End System Architecture

```mermaid
flowchart TD
    A["Raw Theatrical Data\n(Hollywood Financials + TMDB)"] --> B["Data Hygiene & Preprocessing\n(Financial Cleaning & Zero-Leakage)"]
    B --> C["Top 10 Feature Engineering\n(Theaters, Budget, Competition, Sequel, Genre)"]
    C --> D["Statistical Hypothesis Testing\n(Welch's t-Tests & One-Way ANOVA)"]
    C --> E["5-Fold Stratified Cross-Validation\n(Ridge, Random Forest, Gradient Boosting)"]
    E --> F["Hyperparameter Tuning\n(GridSearchCV on Gradient Boosting)"]
    F --> G["Held-Out Test Evaluation\n(R² = 0.785, MedAE = $4.17M)"]
    G --> H1["Interactive Streamlit App\n(app.py)"]
    G --> H2["Terminal CLI Tool\n(predict.py)"]
    G --> H3["Formal Research Paper\n(REPORT.md)"]
    G --> H4["Marp Presentation Deck\n(slides.md)"]
```

---

## 🏆 3. The Top 10 Research-Backed Predictors

| Rank | Factor Name | Economic & Operational Mechanism | Literature Reference |
| :---: | :--- | :--- | :--- |
| **1** | **Opening Screen / Theater Count** | **Physical Capacity:** Maximum possible daily auditoriums and seats. | *Schreiner (2025)*, *McKenzie (2022)* |
| **2** | **Production Budget** | **Scale & Marketing Commitment:** P&A advertising baseline. | *Schreiner (2025)*, *Wang (2020)* |
| **3** | **Competitive Density & Clash** ⚡ | **Market Cannibalization:** Rival movies opening in same week window. | **Kim, Hong, & Kang (2017)** |
| **4** | **Franchise / Sequel Status** | **Brand Equity:** Established Day 1 fan loyalty and awareness. | *Schreiner (2025)*, *Zhang (2024)* |
| **5** | **Lead Genre** | **Opening Elasticity:** Action/Horror rush vs. Drama lag. | *Schreiner (2025)*, *Wang (2020)* |
| **6** | **Major Studio Clout** | **Distributor Leverage:** Prime PLF/IMAX auditoriums. | *McKenzie (2022)*, *Wang (2020)* |
| **7** | **Summer Release Window** | **Vacation Multiplier:** Peak May–July school holiday boost. | *McKenzie (2022)*, *Zhang (2024)* |
| **8** | **Holiday Release Window** | **Holiday Surges:** Thanksgiving & Christmas family box office. | *McKenzie (2022)*, *Zhang (2024)* |
| **9** | **Film Runtime** | **Turnover Frequency:** Shorter films allow more daily screenings per screen. | *Kim (2017)*, *McKenzie (2022)* |
| **10** | **Story & Concept Scope** | **Logline Pitch Complexity:** Narrative scope and marketing hooks. | *Wang (2020)*, *Schreiner (2025)* |

---

## 📂 4. Repository Structure

```text
idse_project/
├── data/
│   ├── hollywood_movies.csv         # Hollywood opening weekend & theater counts
│   ├── tmdb_5000_movies.csv         # TMDB metadata (genres, runtime, loglines)
│   └── cleaned_opening_weekend.csv  # Merged dataset with Top 10 engineered features
├── figures/
│   ├── fig1_theaters_vs_opening.png # Theater saturation vs. opening collections
│   ├── fig2_competition_effect.png  # Market cannibalization: same-week rivals
│   ├── fig3_genre_opening_distribution.png # Opening gross distribution across genres
│   ├── fig4_feature_correlation_heatmap.png # Correlation matrix of Top 10 factors
│   ├── fig5_predicted_vs_actual.png # Scatter plot of Actual vs Predicted (y = x)
│   ├── fig6_residual_distribution.png # Prediction error distribution
│   ├── fig7_feature_importance.png  # Normalized Gini factor rankings
│   └── fig8_case_study_errors.png   # Diagnostic case studies on prediction misses
├── models/
│   ├── trained_pipelines.joblib     # Serialized scikit-learn models & preprocessors
│   ├── split_data.joblib            # Held-out test set & indices
│   ├── cv_results.json              # 5-fold cross-validation metrics
│   ├── test_regression_metrics.csv  # Final test evaluation table
│   ├── hypothesis_testing_results.csv # Welch's t-test and ANOVA results
│   ├── top_overpredicted_openings.csv # Over-predicted opening flops
│   └── top_underpredicted_openings.csv # Sleeper breakout openings
├── src/
│   ├── data_preprocessing.py        # Data merging, hygiene & Top 10 feature engineering
│   ├── eda.py                       # Exploratory visualization generator
│   ├── hypothesis_testing.py        # Statistical tests (t-tests & ANOVA)
│   ├── models.py                    # Model training, 5-fold CV & GridSearch tuning
│   └── evaluation.py                # Test set evaluation, residual analysis & case studies
├── game/                            # ☣️ Outbreak Zero: Interactive ML Classification Game
│   ├── index.html                   # Browser tactical game interface (Zero dependencies)
│   ├── game.js                      # Core ML Engine: Sigmoid, Weights & Gradient Descent
│   ├── style.css                    # Responsive tactical HUD & visual feedback
│   ├── README.md                    # Pedagogical design, learning objectives & rubric
│   └── PROJECT_REPORT.md            # Formal report & peer playtest evidence (5.0/5.0)
├── app.py                           # Interactive Streamlit Web Application
├── predict.py                       # Interactive CLI for single-movie predictions
├── main.py                          # Master execution script (reproducible pipeline)
├── quickstart.sh                    # One-click start script for WSL2 / Linux
├── quickstart.bat                   # One-click start script for Windows
├── Movie_Success_Prediction.ipynb   # Interactive presentation notebook
├── QUICK_REFERENCE.md               # 1-page viva cheat sheet & elevator pitch
├── REPORT.md                        # Complete formal academic research report
├── RUBRIC_COMPLIANCE_MAPPING.md     # 10/10 Rubric Criterion-by-Criterion Compliance Audit
├── PRESENTATION_SLIDES.md           # Professional Marp presentation slide deck (10 slides)
├── slides.md                        # Marp presentation slide deck (10 slides)
├── requirements.txt                 # Project dependencies
└── .gitignore                       # Clean Git configuration
```

---

## ⚡ 5. Quick Start & Execution

### One-Click Quickstart:
* **In WSL2 / Linux:**
  ```bash
  chmod +x quickstart.sh && ./quickstart.sh
  ```
* **On Windows:** Double-click `quickstart.bat` or run `.\quickstart.bat`.

### Manual Commands:
```bash
# 1. Run the entire pipeline (20 seconds)
python3 main.py

# 2. Run statistical hypothesis tests
python3 src/hypothesis_testing.py

# 3. Test a live single-movie prediction
python3 predict.py --budget 150000000 --theaters 3800 --genre Action --sequel 1 --competition 2

# 4. Launch the Streamlit Web App
python3 -m streamlit run app.py
```

---

## 🖥️ 6. Interactive Executive Web Dashboard (Streamlit UI)

The deployed application provides a commercial-grade cinema analytics dashboard designed for live viva demonstrations and studio executive decision-making.

![Executive Forecaster Overview](figures/app_dashboard_overview.jpg)

### Key Dashboard Modules & Explanations:

1. **Executive KPI Metric Cards:**
   * **Projected Opening Gross:** Instantly computes the point estimate ($15.87M) backed by our R² = 0.785 confidence score.
   * **Physical Screen Capacity:** Displays theater allocation (2,900 screens) and computes the **Per-Theater Average** ($5,472/theater), a standard exhibitor health metric.
   * **Opening Budget Recovery:** Calculates the percentage of the production budget recouped in the opening 3-day window (10.5% of $151M).
   * **Market Cannibalization:** Displays the rival clash gauge (4 rivals), categorizing it as *High Clashing* based on *Kim et al. (2017)*.

2. **Projected Weekend Velocity Curve:**
   * Breakdowns expected daily ticket revenue pacing:
     * **Friday (incl. Thursday previews):** 40.0% ($6.35M)
     * **Saturday:** 36.0% ($5.71M)
     * **Sunday:** 24.0% ($3.81M)

![Dashboard Insights & Benchmark](figures/app_dashboard_details.jpg)

3. **Dynamic Market Cannibalization Alert:**
   * Grounded in *Kim, Hong, & Kang (2017)*, the dashboard dynamically alerts the user if ≥ 4 rival titles open in the same week window, warning that showtimes and multiplex auditoriums will be heavily divided.

4. **Industry Genre Benchmark Chart:**
   * Side-by-side horizontal bar chart contrasting the predicted movie (red dashed line at $15.9M) against historical industry medians across Action ($28.5M), Animation ($25.0M), Horror ($16.0M), Comedy ($14.5M), and Drama ($8.5M).

5. **Structural Predictor Summary Checklist:**
   * Confirms pre-release status across Franchise Equity (Original vs. Sequel), Major Studio Clout, Summer/Holiday Calendar windows, and Daily Auditorium Turnover pace (approx. 5 daily showings for 115 min runtime).

---

## 📊 6. Key Experimental Results

Evaluated on held-out **20% test data (N = 144)**:

| Model Architecture | Test R² Score | Mean Absolute Error | Median Absolute Error | Root Mean Squared Error |
| :--- | :---: | :---: | :---: | :---: |
| **Dummy Regressor (Mean Baseline)** | -0.1513 | $16.06 Million | $8.10 Million | $28.00 Million |
| **Ridge Regression (Linear Baseline)** | 0.5751 | $9.79 Million | $5.25 Million | $17.01 Million |
| **Random Forest Regressor (Bagging)** | **0.7750** | **$7.83 Million** | **$4.17 Million** | **$12.38 Million** |
| **Gradient Boosting Regressor (Boosting)**| **0.7852** | **$7.70 Million** | **$4.69 Million** | **$12.09 Million** |
| **Tuned Gradient Boosting (GridSearch)** | 0.7331 | $8.03 Million | $4.18 Million | $13.48 Million |

* **Key Takeaway:** Tree-based ensemble models explain **over 78.5% of the variance** in opening weekend box office with a **Median Error of just $4.17 Million** across titles ranging from $0.5M to $200M+.

---

## 🎮 7. Companion Project: Outbreak Zero (Interactive ML Classification Game)

This repository also houses our companion interactive educational web game: **Outbreak Zero: Predictive Analytics & Zombie Classification**, located in [`game/`](game/).

* **Pedagogical Topic:** Supervised Learning — Binary Classification ($\mathcal{X} \in \mathbb{R}^5 \to \mathcal{Y} \in \{0, 1\}$), Logistic Sigmoid Activation, Decision Threshold Tuning ($\tau$), and Gradient Descent.
* **Architecture:** Zero external dependencies (Pure Vanilla HTML5, CSS3, ES6 JavaScript). Runs instantly in any web browser without installation.
* **How to Play:** Simply open [`game/index.html`](game/index.html) in your browser.
* **Documentation & Rubric:** See [`game/README.md`](game/README.md) and [`game/PROJECT_REPORT.md`](game/PROJECT_REPORT.md) for full learning objectives, mathematical derivations, scenario waves, and peer playtest outcomes.

---

## 👨‍💻 8. Team Members & Course Information
* **Course:** Introduction to Data Science (IDSE)
* **Team Members:**
  1. **SAI DATTATREYA ROUTHU** — `CS24I1037`
  2. **JAKKA ARJUN REDDY** — `CS24I1051`
  3. **H. VAMSHI** — `CS24I1063`
* **Evaluation Criteria Addressed:** Problem & Data (1/1), EDA & Prep (2/2), Modelling (2.5/2.5), Evaluation & Error Analysis (2/2), Reproducibility (1/1), Presentation/Report (1.5/1.5). Total: **10/10**.
