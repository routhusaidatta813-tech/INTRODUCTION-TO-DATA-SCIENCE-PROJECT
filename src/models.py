"""
Model Training, Cross-Validation & Hyperparameter Tuning Module
Task: Predicting Opening Weekend Box Office Revenue (Regression)
Target: Log10(Opening Weekend Gross in $ Millions)
"""

import json
import logging
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV, KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

RANDOM_SEED = 42

CONTINUOUS_FEATURES = [
    'log_theaters', 'log_budget', 'competition_count', 'runtime', 'overview_words'
]
CATEGORICAL_FEATURES = ['primary_genre']
BINARY_FEATURES = [
    'is_sequel_or_franchise', 'is_major_studio', 'is_summer_season', 'is_holiday_season', 'has_homepage'
]


def build_preprocessor():
    """Builds an anti-leakage ColumnTransformer pipeline."""
    return ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), CONTINUOUS_FEATURES),
            ('cat', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'), CATEGORICAL_FEATURES),
            ('bin', 'passthrough', BINARY_FEATURES)
        ]
    )


def train_and_validate(input_csv='data/cleaned_opening_weekend.csv', output_model_dir='models'):
    """Trains regression models, evaluates with 5-fold CV, tunes with GridSearch, and serializes."""
    os.makedirs(output_model_dir, exist_ok=True)
    df = pd.read_csv(input_csv)

    feature_cols = CONTINUOUS_FEATURES + CATEGORICAL_FEATURES + BINARY_FEATURES
    X = df[feature_cols].copy()
    y = df['log_opening_weekend'].copy()

    # Train / Test split (80% train, 20% test) with fixed seed
    X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(
        X, y, df.index, test_size=0.20, random_state=RANDOM_SEED
    )
    logging.info(f"Training set: {len(X_train)} samples. Held-out test set: {len(X_test)} samples.")

    # Candidate Regression Models
    models = {
        'Dummy Regressor (Mean Baseline)': DummyRegressor(strategy='mean'),
        'Ridge Regression (Linear Baseline)': Ridge(alpha=1.0, random_state=RANDOM_SEED),
        'Random Forest Regressor (Bagging)': RandomForestRegressor(n_estimators=100, max_depth=6, random_state=RANDOM_SEED),
        'Gradient Boosting Regressor (Boosting)': GradientBoostingRegressor(n_estimators=100, max_depth=3, learning_rate=0.08, random_state=RANDOM_SEED)
    }

    cv = KFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)
    cv_results = {}

    logging.info("Running 5-Fold Cross-Validation on Training Data...")
    for name, reg in models.items():
        pipe = Pipeline(steps=[
            ('preprocessor', build_preprocessor()),
            ('regressor', reg)
        ])
        
        r2_scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring='r2')
        mae_scores = -cross_val_score(pipe, X_train, y_train, cv=cv, scoring='neg_mean_absolute_error')

        cv_results[name] = {
            'R2 (mean)': float(np.mean(r2_scores)),
            'R2 (std)': float(np.std(r2_scores)),
            'MAE_log (mean)': float(np.mean(mae_scores)),
            'MAE_log (std)': float(np.std(mae_scores))
        }
        logging.info(f"Model [{name}] CV R2: {np.mean(r2_scores):.4f} (+/- {np.std(r2_scores):.4f}), MAE_log: {np.mean(mae_scores):.4f}")

    # Hyperparameter Tuning on Gradient Boosting
    logging.info("Performing GridSearchCV on Gradient Boosting Regressor...")
    gb_pipe = Pipeline(steps=[
        ('preprocessor', build_preprocessor()),
        ('regressor', GradientBoostingRegressor(random_state=RANDOM_SEED))
    ])

    param_grid = {
        'regressor__n_estimators': [70, 100, 140],
        'regressor__max_depth': [3, 4],
        'regressor__learning_rate': [0.05, 0.08, 0.12]
    }

    grid_search = GridSearchCV(gb_pipe, param_grid, cv=cv, scoring='r2', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    best_gb_model = grid_search.best_estimator_
    logging.info(f"Best GB Parameters: {grid_search.best_params_}")
    logging.info(f"Tuned GB CV R2: {grid_search.best_score_:.4f}")

    # Fit all candidate models on full training data
    trained_pipelines = {}
    for name, reg in models.items():
        pipe = Pipeline(steps=[
            ('preprocessor', build_preprocessor()),
            ('regressor', reg)
        ])
        pipe.fit(X_train, y_train)
        trained_pipelines[name] = pipe

    trained_pipelines['Tuned Gradient Boosting Regressor'] = best_gb_model

    # Save artifacts to models/
    joblib.dump(trained_pipelines, os.path.join(output_model_dir, 'trained_pipelines.joblib'))
    joblib.dump({
        'X_train': X_train, 'X_test': X_test,
        'y_train': y_train, 'y_test': y_test,
        'indices_train': indices_train, 'indices_test': indices_test
    }, os.path.join(output_model_dir, 'split_data.joblib'))

    with open(os.path.join(output_model_dir, 'cv_results.json'), 'w') as f:
        json.dump(cv_results, f, indent=4)

    logging.info(f"Saved trained regression models to {output_model_dir}/")
    return cv_results, trained_pipelines


if __name__ == '__main__':
    train_and_validate()
