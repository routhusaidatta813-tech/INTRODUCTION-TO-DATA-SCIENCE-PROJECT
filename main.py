"""
End-to-End Pipeline Runner
Predicting Movie Opening Weekend Box Office Revenue
Grounding: Top 10 Factors from Recent Academic Literature
(Schreiner et al. 2025, Kim et al. 2017, McKenzie 2022, Zhang et al. 2024, Wang et al. 2020)
"""

import sys
import time
from src.data_preprocessing import preprocess_data
from src.eda import run_eda
from src.models import train_and_validate
from src.evaluation import evaluate_models


def main():
    print("=" * 72)
    print("🎬 DATA SCIENCE PROJECT: FORECASTING MOVIE OPENING WEEKEND BOX OFFICE")
    print("   Problem Formulation: Supervised Regression")
    print("   Predictors: Top 10 Research-Backed Structural & Market Signals")
    print("=" * 72)

    start_total = time.time()

    # Step 1: Preprocessing & Top 10 Feature Engineering
    print("\n[Step 1/4] Running Data Cleaning & Merging Hollywood + TMDB Datasets...")
    t0 = time.time()
    df_clean = preprocess_data(
        hollywood_path='data/hollywood_movies.csv',
        tmdb_path='data/tmdb_5000_movies.csv',
        output_path='data/cleaned_opening_weekend.csv'
    )
    print(f"✓ Step 1 Complete: {len(df_clean)} cleaned movies with Top 10 features ({time.time() - t0:.2f}s)")

    # Step 2: Exploratory Data Analysis
    print("\n[Step 2/4] Generating Visualizations for Top 10 Determinants (Figures 1-4)...")
    t0 = time.time()
    run_eda(input_csv='data/cleaned_opening_weekend.csv', output_dir='figures')
    print(f"✓ Step 2 Complete: Figures 1-4 saved to figures/ ({time.time() - t0:.2f}s)")

    # Step 3: Model Training & 5-Fold Cross-Validation
    print("\n[Step 3/4] Training Baseline, Random Forest & Gradient Boosting Regressors...")
    t0 = time.time()
    cv_results, _ = train_and_validate(input_csv='data/cleaned_opening_weekend.csv', output_model_dir='models')
    print(f"✓ Step 3 Complete: Models trained, tuned, and serialized ({time.time() - t0:.2f}s)")

    # Step 4: Test Set Evaluation & Error Analysis
    print("\n[Step 4/4] Evaluating on Held-Out 20% Test Set & Error Analysis (Figures 5-8)...")
    t0 = time.time()
    metrics_df, over_df, under_df = evaluate_models(models_dir='models', figures_dir='figures', data_csv='data/cleaned_opening_weekend.csv')
    print(f"✓ Step 4 Complete: Figures 5-8 and Error Diagnostics generated ({time.time() - t0:.2f}s)")

    total_duration = time.time() - start_total
    print("\n" + "=" * 72)
    print(f"🎉 PIPELINE COMPLETED SUCCESSFULLY IN {total_duration:.2f} SECONDS!")
    print("=" * 72)
    print("\nFinal Test Set Performance Comparison:")
    print(metrics_df.to_string(index=False))
    print("\nGenerated Project Deliverables:")
    print("  • Cleaned Dataset : data/cleaned_opening_weekend.csv")
    print("  • Trained Models  : models/trained_pipelines.joblib")
    print("  • Metric Table    : models/test_regression_metrics.csv")
    print("  • Error Audits    : models/top_overpredicted_openings.csv, top_underpredicted_openings.csv")
    print("  • Figures (1-8)   : figures/fig1_*.png to fig8_*.png")
    print("=" * 72)


if __name__ == '__main__':
    main()
