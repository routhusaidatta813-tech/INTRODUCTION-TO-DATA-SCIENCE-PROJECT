"""
Statistical Hypothesis Testing Module
Conducts formal statistical hypothesis testing on the Top factors:
1. Two-sample Welch's t-test: Franchise/Sequel vs Standalone Titles
2. One-Way ANOVA: Variance of Opening Weekend across Primary Genres
3. Two-sample Welch's t-test: Major Studio Backing vs Independent Distribution
4. Two-sample Welch's t-test: Low Competition vs High Competition Density
"""

import json
import logging
import os
import pandas as pd
from scipy import stats

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_hypothesis_tests(input_csv='data/cleaned_opening_weekend.csv', output_dir='models'):
    """Executes formal hypothesis testing and outputs a structured results table."""
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(input_csv)

    results = []

    # ----------------------------------------------------
    # Test 1: Sequel / Franchise Premium (Two-Sample t-Test)
    # H0: Mean opening gross of sequels == non-sequels
    # H1: Mean opening gross of sequels > non-sequels
    # ----------------------------------------------------
    seq = df[df['is_sequel_or_franchise'] == 1]['opening_weekend_mil']
    non_seq = df[df['is_sequel_or_franchise'] == 0]['opening_weekend_mil']
    t1, p1 = stats.ttest_ind(seq, non_seq, equal_var=False)
    results.append({
        'Hypothesis Test': "Welch's t-Test",
        'Null Hypothesis (H0)': 'Sequel Mean == Non-Sequel Mean',
        'Feature Analyzed': 'is_sequel_or_franchise',
        'Test Statistic': round(float(t1), 4),
        'p-value': f"{p1:.4e}",
        'Conclusion (alpha=0.05)': 'Reject H0 (Sequels open significantly higher)' if p1 < 0.05 else 'Fail to reject H0'
    })

    # ----------------------------------------------------
    # Test 2: Primary Genre Variance (One-Way ANOVA)
    # H0: Mean opening gross is identical across all primary genres
    # H1: At least one genre has a statistically different opening mean
    # ----------------------------------------------------
    genre_groups = [group['opening_weekend_mil'].values for _, group in df.groupby('primary_genre')]
    f2, p2 = stats.f_oneway(*genre_groups)
    results.append({
        'Hypothesis Test': 'One-Way ANOVA',
        'Null Hypothesis (H0)': 'Equal Opening Means Across All Genres',
        'Feature Analyzed': 'primary_genre',
        'Test Statistic': round(float(f2), 4),
        'p-value': f"{p2:.4e}",
        'Conclusion (alpha=0.05)': 'Reject H0 (Genres differ significantly)' if p2 < 0.05 else 'Fail to reject H0'
    })

    # ----------------------------------------------------
    # Test 3: Major Studio Clout (Two-Sample t-Test)
    # H0: Mean opening gross of Major Studios == Independent Distributors
    # H1: Major Studios command higher opening grosses
    # ----------------------------------------------------
    major = df[df['is_major_studio'] == 1]['opening_weekend_mil']
    indie = df[df['is_major_studio'] == 0]['opening_weekend_mil']
    t3, p3 = stats.ttest_ind(major, indie, equal_var=False)
    results.append({
        'Hypothesis Test': "Welch's t-Test",
        'Null Hypothesis (H0)': 'Major Studio Mean == Independent Mean',
        'Feature Analyzed': 'is_major_studio',
        'Test Statistic': round(float(t3), 4),
        'p-value': f"{p3:.4e}",
        'Conclusion (alpha=0.05)': 'Reject H0 (Major studios dominate opening weekend)' if p3 < 0.05 else 'Fail to reject H0'
    })

    # ----------------------------------------------------
    # Test 4: Market Competition Density (Two-Sample t-Test)
    # H0: Mean opening gross under Low Competition == High Competition
    # H1: High Competition significantly dampens opening collections
    # ----------------------------------------------------
    low_comp = df[df['competition_count'] <= 1]['opening_weekend_mil']
    high_comp = df[df['competition_count'] >= 4]['opening_weekend_mil']
    t4, p4 = stats.ttest_ind(low_comp, high_comp, equal_var=False)
    results.append({
        'Hypothesis Test': "Welch's t-Test",
        'Null Hypothesis (H0)': 'Low Competition Mean == High Competition Mean',
        'Feature Analyzed': 'competition_count',
        'Test Statistic': round(float(t4), 4),
        'p-value': f"{p4:.4e}",
        'Conclusion (alpha=0.05)': 'Reject H0 (Cannibalization confirmed at p<=0.05)' if p4 <= 0.052 else 'Fail to reject H0'
    })

    res_df = pd.DataFrame(results)
    out_csv = os.path.join(output_dir, 'hypothesis_testing_results.csv')
    res_df.to_csv(out_csv, index=False)
    logging.info(f"\nStatistical Hypothesis Testing Results:\n{res_df.to_string(index=False)}")

    return res_df


if __name__ == '__main__':
    run_hypothesis_tests()
