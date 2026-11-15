"""
Evaluation, Residual Analysis & Diagnostic Module
Task: Opening Weekend Box Office Revenue Regression
Visualizes model accuracy, feature importances, and error case studies.
"""

import json
import logging
import os
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10


def evaluate_models(models_dir='models', figures_dir='figures', data_csv='data/cleaned_opening_weekend.csv'):
    """Evaluates candidate regression models on held-out test set and produces diagnostic figures."""
    os.makedirs(figures_dir, exist_ok=True)
    
    trained_pipelines = joblib.load(os.path.join(models_dir, 'trained_pipelines.joblib'))
    split_data = joblib.load(os.path.join(models_dir, 'split_data.joblib'))
    df = pd.read_csv(data_csv)

    X_test = split_data['X_test']
    y_test_log = split_data['y_test']
    indices_test = split_data['indices_test']
    test_df = df.loc[indices_test].copy()

    # Actual dollar values ($ Millions)
    actual_dollars = test_df['opening_weekend_mil'].values

    logging.info(f"Loaded test set with {len(test_df)} movies.")

    # 1. Performance Metric Comparison
    metrics_list = []
    predictions_dict = {}

    for name, pipe in trained_pipelines.items():
        pred_log = pipe.predict(X_test)
        pred_dollars = 10 ** pred_log
        predictions_dict[name] = pred_dollars

        r2 = r2_score(actual_dollars, pred_dollars)
        mae = mean_absolute_error(actual_dollars, pred_dollars)
        med_ae = median_absolute_error(actual_dollars, pred_dollars)
        rmse = np.sqrt(mean_squared_error(actual_dollars, pred_dollars))

        metrics_list.append({
            'Model': name,
            'R2 Score': round(r2, 4),
            'MAE ($M)': round(mae, 2),
            'Median AE ($M)': round(med_ae, 2),
            'RMSE ($M)': round(rmse, 2)
        })

    metrics_df = pd.DataFrame(metrics_list)
    metrics_csv_path = os.path.join(models_dir, 'test_regression_metrics.csv')
    metrics_df.to_csv(metrics_csv_path, index=False)
    logging.info(f"\nTest Set Performance Comparison:\n{metrics_df.to_string(index=False)}")

    best_model_name = 'Random Forest Regressor (Bagging)'
    best_preds = predictions_dict[best_model_name]
    test_df['predicted_opening_mil'] = best_preds
    test_df['absolute_error_mil'] = np.abs(actual_dollars - best_preds)
    test_df['error_ratio'] = test_df['predicted_opening_mil'] / test_df['opening_weekend_mil']

    # ----------------------------------------------------
    # Figure 5: Predicted vs Actual Opening Weekend Gross
    # ----------------------------------------------------
    plt.figure(figsize=(8, 6.5))
    plt.scatter(actual_dollars, best_preds, color='#2b5c8f', alpha=0.7, edgecolors='black', linewidth=0.5, s=40)
    
    max_val = max(np.max(actual_dollars), np.max(best_preds)) * 1.05
    plt.plot([0, max_val], [0, max_val], 'r--', lw=1.5, label='Perfect Prediction (y = x)')

    # Annotate top test blockbusters
    top_3 = test_df.sort_values(by='opening_weekend_mil', ascending=False).head(3)
    for _, r in top_3.iterrows():
        plt.annotate(
            f"{r['Movie']}\nAct: ${r['opening_weekend_mil']:.1f}M | Pred: ${r['predicted_opening_mil']:.1f}M",
            xy=(r['opening_weekend_mil'], r['predicted_opening_mil']),
            xytext=(r['opening_weekend_mil'] - 50, r['predicted_opening_mil'] + 10),
            arrowprops=dict(facecolor='black', arrowstyle='->', lw=0.8),
            fontsize=8, fontweight='bold'
        )

    plt.title(f'Actual vs. Predicted Opening Weekend Collections ({best_model_name})', pad=12, fontweight='bold')
    plt.xlabel('Actual Opening Weekend Gross ($ Millions)')
    plt.ylabel('Model Predicted Opening Weekend Gross ($ Millions)')
    plt.xlim(0, max_val)
    plt.ylim(0, max_val)
    plt.legend(loc='upper left')
    plt.tight_layout()
    fig5_path = os.path.join(figures_dir, 'fig5_predicted_vs_actual.png')
    plt.savefig(fig5_path, dpi=300)
    plt.close()
    logging.info(f"Saved: {fig5_path}")

    # ----------------------------------------------------
    # Figure 6: Residual Error Distribution
    # ----------------------------------------------------
    plt.figure(figsize=(8, 5))
    residuals = actual_dollars - best_preds
    sns.histplot(residuals, bins=25, kde=True, color='#4575b4', edgecolor='black')
    plt.axvline(0, color='red', linestyle='--', linewidth=1.5, label='Zero Error Baseline')
    plt.title(f'Residual Error Distribution in Millions of Dollars ({best_model_name})', pad=12, fontweight='bold')
    plt.xlabel('Prediction Error (Actual - Predicted, $ Millions)')
    plt.ylabel('Movie Count')
    plt.legend()
    plt.tight_layout()
    fig6_path = os.path.join(figures_dir, 'fig6_residual_distribution.png')
    plt.savefig(fig6_path, dpi=300)
    plt.close()
    logging.info(f"Saved: {fig6_path}")

    # ----------------------------------------------------
    # Figure 7: Top Feature Importances (From Random Forest)
    # ----------------------------------------------------
    rf_pipe = trained_pipelines[best_model_name]
    reg = rf_pipe.named_steps['regressor']
    preproc = rf_pipe.named_steps['preprocessor']

    cat_cols = list(preproc.named_transformers_['cat'].get_feature_names_out(['primary_genre']))
    continuous_cols = ['Theaters Count (log)', 'Budget (log)', 'Competition Count', 'Runtime', 'Overview Words']
    binary_cols = ['Sequel / Franchise', 'Major Studio', 'Summer Window', 'Holiday Window', 'Has Homepage']
    feature_names = continuous_cols + cat_cols + binary_cols

    if hasattr(reg, 'feature_importances_'):
        feat_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': reg.feature_importances_
        }).sort_values(by='Importance', ascending=False).head(10)

        plt.figure(figsize=(9, 5.5))
        sns.barplot(data=feat_df, x='Importance', y='Feature', hue='Feature', palette='viridis', legend=False, edgecolor='black', linewidth=0.5)
        plt.title('Top 10 Most Predictive Factors for Opening Weekend Gross (Gini Importance)', pad=12, fontweight='bold')
        plt.xlabel('Normalized Feature Importance')
        plt.ylabel('Predictor')
        plt.tight_layout()
        fig7_path = os.path.join(figures_dir, 'fig7_feature_importance.png')
        plt.savefig(fig7_path, dpi=300)
        plt.close()
        logging.info(f"Saved: {fig7_path}")

    # ----------------------------------------------------
    # Figure 8 & Tables: Error Case Studies (Over vs Under Predictions)
    # ----------------------------------------------------
    # Over-predictions (High expectation, opening flop)
    over_df = test_df[test_df['predicted_opening_mil'] > test_df['opening_weekend_mil']].sort_values(by='absolute_error_mil', ascending=False)
    # Under-predictions (Low expectation, breakout opening hit)
    under_df = test_df[test_df['opening_weekend_mil'] > test_df['predicted_opening_mil']].sort_values(by='absolute_error_mil', ascending=False)

    cols_show = ['Movie', 'TheatersOpenWeek', 'Budget', 'opening_weekend_mil', 'predicted_opening_mil', 'absolute_error_mil', 'primary_genre']
    over_df[cols_show].head(5).to_csv(os.path.join(models_dir, 'top_overpredicted_openings.csv'), index=False)
    under_df[cols_show].head(5).to_csv(os.path.join(models_dir, 'top_underpredicted_openings.csv'), index=False)

    plt.figure(figsize=(9, 5))
    sample_cases = pd.concat([over_df.head(4), under_df.head(4)])
    sample_cases['Error Type'] = ['Over-Predicted (Opening Disappointment)'] * 4 + ['Under-Predicted (Breakout Sleeper Open)'] * 4

    sns.barplot(data=sample_cases, x='Movie', y='absolute_error_mil', hue='Error Type', palette=['#d9534f', '#5cb85c'])
    plt.title('Diagnostic Case Studies: Highest Prediction Residuals ($ Millions)', pad=12, fontweight='bold')
    plt.xlabel('Movie Title')
    plt.ylabel('Absolute Error ($ Millions)')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    fig8_path = os.path.join(figures_dir, 'fig8_case_study_errors.png')
    plt.savefig(fig8_path, dpi=300)
    plt.close()
    logging.info(f"Saved: {fig8_path}")

    return metrics_df, over_df, under_df


if __name__ == '__main__':
    evaluate_models()
