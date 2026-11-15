"""
🎬 Executive Cinema Analytics Dashboard: Movie Opening Weekend Forecaster
Interactive deployment for live viva demonstration and investor decision support.
Launch with: streamlit run app.py
"""

import os
import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

MODEL_PATH = 'models/trained_pipelines.joblib'


def set_custom_styling():
    """Injects high-end, modern typography and cinema dashboard CSS styling."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #1e3a8a 100%);
        padding: 24px 30px;
        border-radius: 14px;
        color: #ffffff;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 28px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        color: #94a3b8;
        font-size: 14px;
        margin: 6px 0 0 0;
    }
    
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 800;
        color: #2563eb;
        margin: 4px 0;
    }
    
    .metric-label {
        font-size: 13px;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .highlight-badge {
        background: #dbeafe;
        color: #1e40af;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
    }
    
    .comp-alert-low {
        background: #ecfdf5;
        border-left: 4px solid #10b981;
        padding: 10px 14px;
        border-radius: 6px;
        color: #065f46;
        font-size: 13px;
    }
    
    .comp-alert-high {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        padding: 10px 14px;
        border-radius: 6px;
        color: #991b1b;
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    if not HAS_STREAMLIT:
        print("Streamlit is not installed in the current environment.")
        print("Please run: pip install streamlit")
        return

    st.set_page_config(
        page_title="Movie Box Office Intelligence",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    set_custom_styling()

    # Executive Banner Header
    st.markdown("""
    <div class="main-header">
        <h1>🎬 Box Office Intelligence: Opening Weekend Forecaster</h1>
        <p>Grounded in Foundational Literature: <i>Schreiner et al. (JAMS 2025)</i> • <i>Kim, Hong, & Kang (CIN 2017)</i> • <i>McKenzie (2022)</i></p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar: Scenario Presets & Inputs
    st.sidebar.markdown("### ⚡ Quick Scenario Presets")
    preset = st.sidebar.selectbox(
        "Load Industry Archetype:",
        [
            "Custom Parameters",
            "🚀 Summer Superhero Tentpole (e.g. Marvel/DC)",
            "👻 Low-Budget Halloween Horror (e.g. Blumhouse)",
            "🧸 Family Holiday Animation (e.g. Disney/Illumination)",
            "🎭 Prestige Mid-Budget Drama"
        ]
    )

    # Default parameters based on preset
    if preset == "🚀 Summer Superhero Tentpole (e.g. Marvel/DC)":
        d_budget, d_theaters, d_comp, d_genre, d_seq, d_studio, d_season, d_runtime = (
            200.0, 4200, 1, "Action", True, True, "Summer Blockbuster (May-Jul)", 130
        )
    elif preset == "👻 Low-Budget Halloween Horror (e.g. Blumhouse)":
        d_budget, d_theaters, d_comp, d_genre, d_seq, d_studio, d_season, d_runtime = (
            12.0, 2800, 3, "Horror", False, True, "Standard Window (Jan-Apr, Aug-Oct)", 95
        )
    elif preset == "🧸 Family Holiday Animation (e.g. Disney/Illumination)":
        d_budget, d_theaters, d_comp, d_genre, d_seq, d_studio, d_season, d_runtime = (
            90.0, 3900, 2, "Animation", True, True, "Holiday Window (Nov-Dec)", 100
        )
    elif preset == "🎭 Prestige Mid-Budget Drama":
        d_budget, d_theaters, d_comp, d_genre, d_seq, d_studio, d_season, d_runtime = (
            35.0, 1800, 4, "Drama", False, False, "Standard Window (Jan-Apr, Aug-Oct)", 135
        )
    else:
        d_budget, d_theaters, d_comp, d_genre, d_seq, d_studio, d_season, d_runtime = (
            100.0, 3500, 2, "Action", True, True, "Summer Blockbuster (May-Jul)", 115
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Pre-Release Control Sliders")

    budget_m = st.sidebar.slider("Production Budget ($ Millions)", 1.0, 300.0, d_budget, 5.0)
    theaters = st.sidebar.slider("Opening Screen / Theater Count", 100, 4500, d_theaters, 50)
    competition = st.sidebar.slider("Rival Releases in Same Week (+/- 7 Days)", 0, 7, d_comp, 1)

    genres = ['Action', 'Animation', 'Adventure', 'Comedy', 'Horror', 'Drama', 'Thriller', 'Other']
    genre = st.sidebar.selectbox("Primary Genre", genres, index=genres.index(d_genre) if d_genre in genres else 0)

    col_s1, col_s2 = st.sidebar.columns(2)
    is_sequel = col_s1.checkbox("Franchise / Sequel", value=d_seq)
    is_major = col_s2.checkbox("Major Studio Backing", value=d_studio)

    seasons = ["Summer Blockbuster (May-Jul)", "Holiday Window (Nov-Dec)", "Standard Window (Jan-Apr, Aug-Oct)"]
    release_season = st.sidebar.selectbox("Release Window", seasons, index=seasons.index(d_season) if d_season in seasons else 0)
    is_summer = 1 if "Summer" in release_season else 0
    is_holiday = 1 if "Holiday" in release_season else 0

    runtime = st.sidebar.slider("Film Runtime (Minutes)", 80, 180, d_runtime, 5)

    # Model Inference Pipeline
    if not os.path.exists(MODEL_PATH):
        st.error("Model artifacts not found! Run 'python main.py' to generate.")
        return

    models = joblib.load(MODEL_PATH)
    model_name = 'Random Forest Regressor (Bagging)'
    pipe = models.get(model_name, list(models.values())[2])

    input_df = pd.DataFrame([{
        'log_theaters': np.log10(theaters),
        'log_budget': np.log10(budget_m),
        'competition_count': competition,
        'runtime': float(runtime),
        'overview_words': 50.0,
        'primary_genre': genre,
        'is_sequel_or_franchise': int(is_sequel),
        'is_major_studio': int(is_major),
        'is_summer_season': is_summer,
        'is_holiday_season': is_holiday,
        'has_homepage': 1
    }])

    pred_log = pipe.predict(input_df)[0]
    forecast_m = float(10 ** pred_log)

    # Day-by-Day Theatrical Velocity Breakdown
    # In Hollywood analytics: Friday ~40% (incl previews), Saturday ~35%, Sunday ~25%
    fri_gross = forecast_m * 0.40
    sat_gross = forecast_m * 0.36
    sun_gross = forecast_m * 0.24

    # Top KPI Metrics Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Projected Opening Gross</div>
            <div class="metric-value">${forecast_m:.2f}M</div>
            <span class="highlight-badge">R² = 0.785 Confidence</span>
        </div>
        """, unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Physical Screen Capacity</div>
            <div class="metric-value">{theaters:,}</div>
            <span class="highlight-badge">${(forecast_m*1e6/theaters):,.0f} / Theater Avg</span>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Opening Budget Recovery</div>
            <div class="metric-value">{(forecast_m/budget_m)*100:.1f}%</div>
            <span class="highlight-badge">${budget_m:.0f}M Production Budget</span>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Market Cannibalization</div>
            <div class="metric-value">{competition} Rivals</div>
            <span class="highlight-badge">{"Low Threat" if competition <= 1 else ("High Clashing" if competition >= 4 else "Moderate Clashing")}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed Analysis Columns
    c_left, c_right = st.columns([1, 1])

    with c_left:
        st.markdown("### 📅 Projected Weekend Velocity Curve")
        velocity_table_html = f"""
        <table style="width:100%; border-collapse: collapse; margin-top: 6px; margin-bottom: 14px; background:#ffffff; border-radius: 8px; overflow: hidden; border: 1px solid #e2e8f0;">
            <thead>
                <tr style="background:#f8fafc; border-bottom: 2px solid #e2e8f0;">
                    <th style="padding:10px 14px; text-align:left; color:#1e293b; font-size:13px;">Release Day</th>
                    <th style="padding:10px 14px; text-align:right; color:#1e293b; font-size:13px;">Collections ($M)</th>
                    <th style="padding:10px 14px; text-align:right; color:#1e293b; font-size:13px;">Share of Weekend</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding:9px 14px; color:#334155; font-size:13px;"><b>Friday (incl. Previews)</b></td>
                    <td style="padding:9px 14px; text-align:right; color:#2563eb; font-weight:700; font-size:14px;">${fri_gross:.2f}M</td>
                    <td style="padding:9px 14px; text-align:right; color:#64748b; font-size:13px;">40.0%</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9; background:#fafbfc;">
                    <td style="padding:9px 14px; color:#334155; font-size:13px;"><b>Saturday</b></td>
                    <td style="padding:9px 14px; text-align:right; color:#2563eb; font-weight:700; font-size:14px;">${sat_gross:.2f}M</td>
                    <td style="padding:9px 14px; text-align:right; color:#64748b; font-size:13px;">36.0%</td>
                </tr>
                <tr>
                    <td style="padding:9px 14px; color:#334155; font-size:13px;"><b>Sunday</b></td>
                    <td style="padding:9px 14px; text-align:right; color:#2563eb; font-weight:700; font-size:14px;">${sun_gross:.2f}M</td>
                    <td style="padding:9px 14px; text-align:right; color:#64748b; font-size:13px;">24.0%</td>
                </tr>
            </tbody>
        </table>
        """
        st.markdown(velocity_table_html, unsafe_allow_html=True)

        if competition >= 4:
            st.markdown(f"""
            <div class="comp-alert-high">
                ⚠️ <b>High Competitive Dilution:</b> Facing {competition} rival movies opening the same week. 
                Grounded in <i>Kim et al. (2017)</i>, expect theater showtimes to be heavily split.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="comp-alert-low">
                ✅ <b>Optimal Release Window:</b> Facing only {competition} rival releases. Strong auditorium retention guaranteed.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🎯 Structural Predictor Summary")
        st.markdown(f"""
        * **Franchise Equity:** {'✅ Sequel/Franchise (+Built-in Fandom)' if is_sequel else '⭕ Original Property'}
        * **Distributor Muscle:** {'✅ Big-6 Major Studio (Prime IMAX & PLF Allocations)' if is_major else '⭕ Independent Distribution'}
        * **Calendar Benefit:** {'☀️ Summer Blockbuster Window' if is_summer else ('🎄 Holiday Family Window' if is_holiday else 'Standard Release Window')}
        * **Turnover Pace:** {runtime} mins (~{max(2, int(720 / (runtime + 25)))} showings/auditorium daily)
        """)

    with c_right:
        st.markdown("### 📊 Benchmark Against Industry Genre Medians")
        genre_medians = {
            'Action': 28.5, 'Animation': 25.0, 'Adventure': 24.2,
            'Comedy': 14.5, 'Horror': 16.0, 'Thriller': 12.8,
            'Drama': 8.5, 'Other': 9.2
        }
        fig, ax = plt.subplots(figsize=(6, 3.8))
        g_names = list(genre_medians.keys())
        g_vals = list(genre_medians.values())
        b_colors = ['#2563eb' if g == genre else '#cbd5e1' for g in g_names]

        bars = ax.barh(g_names, g_vals, color=b_colors, edgecolor='#64748b', linewidth=0.5)
        ax.axvline(forecast_m, color='#ef4444', linestyle='--', linewidth=1.8, label=f'Your Movie (${forecast_m:.1f}M)')
        
        ax.set_xlabel('Opening Gross ($ Millions)', fontsize=10, fontweight='bold')
        ax.set_title('Industry Median Opening vs. Predicted Film', fontsize=11, fontweight='bold')
        ax.legend(loc='lower right', frameon=True)
        ax.grid(axis='x', linestyle=':', alpha=0.6)
        plt.tight_layout()
        st.pyplot(fig)

    st.markdown("---")
    st.caption("🎓 **IDSE Project Team:** SAI DATTATREYA ROUTHU (CS24I1037) • JAKKA ARJUN REDDY (CS24I1051) • H. VAMSHI (CS24I1063) | Evaluated on 717 verified historical theatrical titles.")


if __name__ == '__main__':
    main()
