"""
Data Preprocessing & Feature Engineering Module
Target: Opening Weekend Box Office Revenue (in $ Millions)
Incorporates the Top 10 Factors Identified in Recent Academic Literature:
(Schreiner et al. 2025, McKenzie 2022, Zhang et al. 2024, Kim et al. 2017, Wang et al. 2020)
"""

import json
import logging
import os
import re
import numpy as np
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MAJOR_STUDIOS = ['sony', 'paramount', 'warner', 'universal', 'disney', 'fox', 'columbia', 'buena vista', 'marvel']
TOP_GENRES = ['Action', 'Comedy', 'Drama', 'Horror', 'Animation', 'Adventure', 'Thriller']


def parse_tmdb_genre(val):
    """Extract first genre from TMDB JSON structure."""
    try:
        items = json.loads(val)
        if items and len(items) > 0:
            return items[0].get('name', 'Other')
    except (ValueError, TypeError):
        pass
    return 'Other'


def detect_sequel_or_franchise(title):
    """Identifies sequel, prequel, or franchise brand markers in title."""
    if not isinstance(title, str):
        return 0
    t = title.lower()
    # Check for sequel numbers, roman numerals, or colon subtitle patterns
    pattern = r'\b(2|3|4|5|6|ii|iii|iv|v|vi|part|chapter|returns|rises|reloaded|revolution|forever)\b'
    return int(bool(re.search(pattern, t)) or (':' in t))


def compute_competition(df, date_col='release_date', window_days=7):
    """
    Computes Competitive Density (Kim, Hong, & Kang 2017):
    Counts the number of rival commercial films opening within +/- 7 days.
    """
    dates = df[date_col].values
    n = len(df)
    comp_counts = np.zeros(n, dtype=int)
    window = pd.Timedelta(days=window_days)

    for i in range(n):
        d_i = dates[i]
        if pd.isnull(d_i):
            comp_counts[i] = 2  # Median fallback
            continue
        # Count overlapping releases excluding the movie itself
        diffs = np.abs(dates - d_i)
        overlapping = (diffs <= window) & (np.arange(n) != i)
        comp_counts[i] = np.sum(overlapping)

    return comp_counts


def preprocess_data(
    hollywood_path='data/hollywood_movies.csv',
    tmdb_path='data/tmdb_5000_movies.csv',
    output_path='data/cleaned_opening_weekend.csv'
):
    """
    Merges Hollywood opening weekend financial data with TMDB metadata,
    cleans missing values, and constructs the Top 10 research-backed predictors.
    """
    logging.info(f"Loading datasets: '{hollywood_path}' and '{tmdb_path}'...")
    df_h = pd.read_csv(hollywood_path, encoding='latin1')
    df_tmdb = pd.read_csv(tmdb_path)

    # Normalize titles for robust inner join
    df_h['title_clean'] = df_h['Movie'].astype(str).str.strip().str.lower()
    df_tmdb['title_clean'] = df_tmdb['title'].astype(str).str.strip().str.lower()

    merged = pd.merge(df_h, df_tmdb, on='title_clean', how='inner')
    logging.info(f"Successfully joined {len(merged)} titles across datasets.")

    # 1. Financial & Operational Filtering (Non-zero positive values)
    valid_mask = (
        (merged['OpeningWeekend'] > 0.05) & 
        (merged['Budget'] > 0.5) & 
        (merged['TheatersOpenWeek'] >= 10)
    )
    df_clean = merged[valid_mask].copy()
    logging.info(f"Retained {len(df_clean)} records with verified Opening Weekend, Budget, and Theater counts.")

    # 2. Parse & Impute Core Variables
    # Parse release date for seasonality & competition
    df_clean['release_date'] = pd.to_datetime(df_clean['release_date'], errors='coerce')
    median_date = df_clean['release_date'].dropna().median()
    df_clean['release_date'] = df_clean['release_date'].fillna(median_date)

    df_clean['release_month'] = df_clean['release_date'].dt.month
    df_clean['release_year'] = df_clean['release_date'].dt.year

    # Runtime imputation
    median_runtime = df_clean['runtime'].median()
    df_clean['runtime'] = df_clean['runtime'].fillna(median_runtime)

    # Genre synthesis (Fill Hollywood missing genres with TMDB genres)
    df_clean['tmdb_primary_genre'] = df_clean['genres'].apply(parse_tmdb_genre)
    df_clean['final_genre'] = df_clean['Genre'].fillna(df_clean['tmdb_primary_genre'])
    df_clean['primary_genre'] = df_clean['final_genre'].apply(
        lambda g: g if g in TOP_GENRES else 'Other'
    )

    # ========================================================
    # TOP 10 RESEARCH-BACKED PREDICTORS (Opening Weekend Drivers)
    # ========================================================
    # 1. Screen Capacity (TheatersOpenWeek - Log scaled)
    df_clean['log_theaters'] = np.log10(df_clean['TheatersOpenWeek'])

    # 2. Production Budget (Budget in $M - Log scaled)
    df_clean['log_budget'] = np.log10(df_clean['Budget'])

    # 3. Competitive Density (Kim, Hong, & Kang 2017)
    df_clean['competition_count'] = compute_competition(df_clean, date_col='release_date', window_days=7)

    # 4. Franchise / Sequel Indicator (Schreiner et al. 2025)
    df_clean['is_sequel_or_franchise'] = df_clean['Movie'].apply(detect_sequel_or_franchise)

    # 5. Major Studio Clout (McKenzie 2022)
    df_clean['is_major_studio'] = df_clean['LeadStudio'].fillna('').apply(
        lambda s: int(any(m in s.lower() for m in MAJOR_STUDIOS))
    )

    # 6. Summer Blockbuster Window (May, June, July) (McKenzie 2022)
    df_clean['is_summer_season'] = df_clean['release_month'].isin([5, 6, 7]).astype(int)

    # 7. Holiday Window (November, December) (Zhang et al. 2024)
    df_clean['is_holiday_season'] = df_clean['release_month'].isin([11, 12]).astype(int)

    # 8. Runtime in Minutes (Showtime frequency constraint) (Kim et al. 2017)
    df_clean['runtime'] = df_clean['runtime'].astype(float)

    # 9. Story & Concept Complexity (Overview Word Count) (Wang et al. 2020)
    df_clean['overview_words'] = df_clean['overview'].fillna('').apply(lambda t: len(t.split()))

    # 10. Digital Campaign Footprint (Official studio web presence) (Schreiner 2025)
    df_clean['has_homepage'] = df_clean['homepage'].notnull().astype(int)

    # Target: Opening Weekend collections in $ Millions
    df_clean['opening_weekend_mil'] = df_clean['OpeningWeekend'].astype(float)
    df_clean['log_opening_weekend'] = np.log10(df_clean['opening_weekend_mil'])

    # Retain structured columns
    output_cols = [
        'Movie', 'release_year', 'release_date', 'release_month',
        'opening_weekend_mil', 'log_opening_weekend',
        'TheatersOpenWeek', 'log_theaters',
        'Budget', 'log_budget',
        'competition_count',
        'is_sequel_or_franchise',
        'primary_genre',
        'is_major_studio',
        'is_summer_season',
        'is_holiday_season',
        'runtime',
        'overview_words',
        'has_homepage'
    ]

    df_output = df_clean[output_cols].copy()
    df_output.to_csv(output_path, index=False)
    logging.info(f"Preprocessing complete: Saved {len(df_output)} records to '{output_path}'.")
    return df_output


if __name__ == '__main__':
    preprocess_data()
