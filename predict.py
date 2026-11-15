"""
Interactive CLI for Movie Opening Weekend Box Office Prediction
Based on the Top 10 Research-Backed Pre-Release Factors
"""

import argparse
import os
import joblib
import numpy as np
import pandas as pd

MODEL_PATH = 'models/trained_pipelines.joblib'


def predict_opening(
    budget_dollars,
    theaters_count,
    competition_count=2,
    is_sequel=1,
    primary_genre='Action',
    is_major_studio=1,
    release_month=6,
    runtime_mins=115,
    overview_word_count=50,
    has_homepage=1,
    model_name='Random Forest Regressor (Bagging)'
):
    """Forecasts opening weekend collections in Millions of USD."""
    if not os.path.exists(MODEL_PATH):
        print("Model file not found. Running training pipeline...")
        import main
        main.main()

    try:
        models = joblib.load(MODEL_PATH)
    except Exception as e:
        print("\n[Notice] Detected Python/NumPy version mismatch across OS environments.")
        print(f"Details: {e}")
        print("Retraining models natively inside your current environment (takes ~15s)...")
        from src.models import train_and_validate
        train_and_validate()
        models = joblib.load(MODEL_PATH)
        print("✓ Models retrained and loaded natively!\n")

    if model_name not in models:
        model_name = list(models.keys())[2]  # Default to Random Forest
    pipe = models[model_name]

    # Convert inputs to model feature space
    budget_m = budget_dollars / 1e6
    log_budget = np.log10(max(budget_m, 0.1))
    log_theaters = np.log10(max(theaters_count, 1))
    is_summer = int(release_month in [5, 6, 7])
    is_holiday = int(release_month in [11, 12])

    input_df = pd.DataFrame([{
        'log_theaters': log_theaters,
        'log_budget': log_budget,
        'competition_count': int(competition_count),
        'runtime': float(runtime_mins),
        'overview_words': float(overview_word_count),
        'primary_genre': primary_genre,
        'is_sequel_or_franchise': int(is_sequel),
        'is_major_studio': int(is_major_studio),
        'is_summer_season': is_summer,
        'is_holiday_season': is_holiday,
        'has_homepage': int(has_homepage)
    }])

    pred_log = pipe.predict(input_df)[0]
    pred_dollars_mil = float(10 ** pred_log)

    return {
        'forecast_opening_mil': pred_dollars_mil,
        'forecast_opening_str': f"${pred_dollars_mil:.2f} Million",
        'theaters': f"{theaters_count:,} theaters",
        'budget': f"${budget_m:.1f} Million",
        'genre': primary_genre,
        'competition': f"{competition_count} rival films",
        'sequel': 'Yes' if is_sequel else 'No',
        'studio': 'Major Studio' if is_major_studio else 'Independent',
        'model_used': model_name
    }


def main():
    parser = argparse.ArgumentParser(description="Predict Movie Opening Weekend Box Office Gross (Top 10 Pre-Release Model)")
    parser.add_argument('--budget', type=float, default=150000000, help="Production budget in USD (e.g. 150000000)")
    parser.add_argument('--theaters', type=int, default=3800, help="Number of opening screens/theaters (e.g. 3800)")
    parser.add_argument('--competition', type=int, default=2, help="Number of rival movies opening same week (e.g. 2)")
    parser.add_argument('--sequel', type=int, default=1, choices=[0, 1], help="Is it a franchise sequel? (1=Yes, 0=No)")
    parser.add_argument('--genre', type=str, default='Action', choices=['Action', 'Comedy', 'Drama', 'Horror', 'Animation', 'Adventure', 'Thriller', 'Other'], help="Primary genre")
    parser.add_argument('--studio', type=int, default=1, choices=[0, 1], help="Major studio backing (1=Yes, 0=No)")
    parser.add_argument('--month', type=int, default=6, help="Release month (1-12)")
    parser.add_argument('--runtime', type=float, default=125, help="Movie runtime in minutes")

    args = parser.parse_args()

    print("=" * 68)
    print("🎬 MOVIE OPENING WEEKEND BOX OFFICE FORECASTER")
    print("   Target: North American Opening Weekend Collections")
    print("   Grounding: Top 10 Factors from Schreiner 2025, Kim 2017, McKenzie 2022")
    print("=" * 68)
    print("Inputs:")
    print(f"  • Production Budget    : ${args.budget:,.0f} (${args.budget/1e6:.1f}M)")
    print(f"  • Opening Screen Count : {args.theaters:,} theaters")
    print(f"  • Competing Releases   : {args.competition} rival movies opening same week")
    print(f"  • Sequel / Franchise   : {'Yes' if args.sequel else 'No'}")
    print(f"  • Primary Genre        : {args.genre}")
    print(f"  • Major Studio Backing : {'Yes' if args.studio else 'No'}")
    print(f"  • Release Month        : {args.month}")
    print(f"  • Runtime              : {args.runtime} mins")
    print("-" * 68)

    res = predict_opening(
        budget_dollars=args.budget,
        theaters_count=args.theaters,
        competition_count=args.competition,
        is_sequel=args.sequel,
        primary_genre=args.genre,
        is_major_studio=args.studio,
        release_month=args.month,
        runtime_mins=args.runtime
    )

    print("Forecast Result:")
    print(f"  🌟 Projected Opening Weekend Gross : {res['forecast_opening_str']}")
    print(f"     Model Architecture Used         : {res['model_used']}")
    print("=" * 68)


if __name__ == '__main__':
    main()
