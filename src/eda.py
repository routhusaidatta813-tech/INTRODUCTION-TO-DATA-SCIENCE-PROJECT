"""
Exploratory Data Analysis (EDA) Module
Visualizes the Top 10 Factors Influencing Opening Weekend Box Office Collections.
Cites: Schreiner et al. (2025), Kim et al. (2017), McKenzie (2022), Zhang et al. (2024).
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 11


def run_eda(input_csv='data/cleaned_opening_weekend.csv', output_dir='figures'):
    """Generates 4 publication-quality exploratory visualizations for the Top 10 factors."""
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(input_csv)
    print(f"Loaded {len(df)} records for Opening Weekend EDA.")

    # ----------------------------------------------------
    # Figure 1: Theater Saturation vs Opening Weekend Gross
    # ----------------------------------------------------
    plt.figure(figsize=(8.5, 6))
    scatter = plt.scatter(
        df['TheatersOpenWeek'],
        df['opening_weekend_mil'],
        c=df['Budget'],
        cmap='viridis',
        alpha=0.7,
        edgecolors='none',
        s=35
    )
    cbar = plt.colorbar(scatter)
    cbar.set_label('Production Budget ($ Millions)', fontsize=10)

    # Annotate top opening records
    top_films = df.sort_values(by='opening_weekend_mil', ascending=False).head(3)
    for _, r in top_films.iterrows():
        plt.annotate(
            f"{r['Movie']}\n(${r['opening_weekend_mil']:.1f}M)",
            xy=(r['TheatersOpenWeek'], r['opening_weekend_mil']),
            xytext=(r['TheatersOpenWeek'] - 650, r['opening_weekend_mil'] + 6),
            arrowprops=dict(facecolor='black', arrowstyle='->', lw=0.8),
            fontsize=8, fontweight='bold'
        )

    plt.title('Theater Screen Capacity vs. Opening Weekend Gross (Schreiner et al. 2025)', pad=12, fontweight='bold')
    plt.xlabel('Opening Theaters / Screens Count')
    plt.ylabel('Opening Weekend Collections ($ Millions)')
    plt.tight_layout()
    fig1_path = os.path.join(output_dir, 'fig1_theaters_vs_opening.png')
    plt.savefig(fig1_path, dpi=300)
    plt.close()
    print(f"Saved: {fig1_path}")

    # ----------------------------------------------------
    # Figure 2: The Competition Cannibalization Effect (Kim et al. 2017)
    # ----------------------------------------------------
    plt.figure(figsize=(8.5, 5))
    
    # Bin competition count into categories
    df['comp_bracket'] = pd.cut(
        df['competition_count'],
        bins=[-1, 1, 3, 20],
        labels=['Low Competition\n(0-1 Rivals)', 'Moderate Competition\n(2-3 Rivals)', 'Intense Competition\n(4+ Rivals)']
    )
    
    comp_stats = df.groupby('comp_bracket', observed=True)['opening_weekend_mil'].agg(['mean', 'median', 'count']).reset_index()

    bars = plt.bar(
        comp_stats['comp_bracket'],
        comp_stats['mean'],
        color=['#2ca02c', '#1f77b4', '#d62728'],
        edgecolor='black',
        linewidth=0.6,
        width=0.55
    )
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.8, f'${height:.1f}M', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.title('Market Cannibalization: Average Opening Weekend by Same-Week Rival Count (Kim et al. 2017)', pad=12, fontweight='bold')
    plt.xlabel('Concurrent Competitive Density Window (+/- 7 Days)')
    plt.ylabel('Mean Opening Weekend Gross ($ Millions)')
    plt.ylim(0, max(comp_stats['mean']) * 1.25)
    plt.tight_layout()
    fig2_path = os.path.join(output_dir, 'fig2_competition_effect.png')
    plt.savefig(fig2_path, dpi=300)
    plt.close()
    print(f"Saved: {fig2_path}")

    # ----------------------------------------------------
    # Figure 3: Opening Weekend Distribution Across Genres
    # ----------------------------------------------------
    plt.figure(figsize=(9, 5.5))
    genre_order = df.groupby('primary_genre')['opening_weekend_mil'].median().sort_values(ascending=False).index

    sns.boxplot(
        data=df,
        x='primary_genre',
        y='opening_weekend_mil',
        order=genre_order,
        palette='Set2',
        showfliers=False
    )
    plt.title('Opening Weekend Box Office Distribution by Primary Genre', pad=12, fontweight='bold')
    plt.xlabel('Primary Genre')
    plt.ylabel('Opening Weekend ($ Millions, Outliers Omitted)')
    plt.xticks(rotation=20)
    plt.tight_layout()
    fig3_path = os.path.join(output_dir, 'fig3_genre_opening_distribution.png')
    plt.savefig(fig3_path, dpi=300)
    plt.close()
    print(f"Saved: {fig3_path}")

    # ----------------------------------------------------
    # Figure 4: Feature Correlation Heatmap with Opening Weekend
    # ----------------------------------------------------
    plt.figure(figsize=(8.5, 6.5))
    corr_cols = [
        'log_opening_weekend', 'log_theaters', 'log_budget',
        'is_sequel_or_franchise', 'competition_count', 'is_major_studio',
        'is_summer_season', 'is_holiday_season', 'runtime', 'overview_words'
    ]
    
    rename_dict = {
        'log_opening_weekend': 'Log(Opening $M)',
        'log_theaters': 'Log(Theaters)',
        'log_budget': 'Log(Budget)',
        'is_sequel_or_franchise': 'Sequel/Franchise',
        'competition_count': 'Rival Competition',
        'is_major_studio': 'Major Studio',
        'is_summer_season': 'Summer Window',
        'is_holiday_season': 'Holiday Window',
        'runtime': 'Runtime (min)',
        'overview_words': 'Overview Words'
    }

    corr_matrix = df[corr_cols].rename(columns=rename_dict, index=rename_dict).corr()
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', vmin=-0.3, vmax=0.9, square=True)
    plt.title('Correlation Matrix of the Top 10 Opening Weekend Predictors', pad=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    fig4_path = os.path.join(output_dir, 'fig4_feature_correlation_heatmap.png')
    plt.savefig(fig4_path, dpi=300)
    plt.close()
    print(f"Saved: {fig4_path}")


if __name__ == '__main__':
    run_eda()
