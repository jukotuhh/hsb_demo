"""
ui_theme.py — UI theme and layout helpers for the Bearing Challenge.
"""

from html import escape

import streamlit as st


HSB_PRIMARY = "#005B96"
HSB_PRIMARY_LIGHT = "#0077C8"
HSB_PRIMARY_DARK = "#003D66"

HSB_NEUTRAL_50 = "#F8F9FA"
HSB_NEUTRAL_100 = "#EEF2F5"
HSB_NEUTRAL_200 = "#D8E0E8"
HSB_NEUTRAL_300 = "#C5CED8"
HSB_NEUTRAL_700 = "#495057"
HSB_NEUTRAL_900 = "#212529"

COLOR_SUCCESS = "#2F7D4A"
COLOR_WARNING = "#B88119"
COLOR_ERROR = "#A13A38"
COLOR_INFO = "#2A6F97"

RANK_GOLD = "#D1A93A"
RANK_SILVER = "#9DA7B0"
RANK_BRONZE = "#A66A3F"

CHART_COLORS = {
    "Normal": COLOR_SUCCESS,
    "Innenring (IR)": COLOR_ERROR,
    "Außenring (OR)": HSB_PRIMARY,
    "Kugel (B)": "#B88119",
}

PLOTLY_LAYOUT = {
    "template": "plotly_white",
    "plot_bgcolor": "white",
    "paper_bgcolor": "white",
    "font": {"family": "sans-serif", "size": 13, "color": HSB_NEUTRAL_900},
    "title": {"font": {"color": HSB_NEUTRAL_900, "size": 14}},
    "legend": {"font": {"color": HSB_NEUTRAL_900, "size": 11}, "title": {"font": {"color": HSB_NEUTRAL_900}}},
    "xaxis": {"gridcolor": HSB_NEUTRAL_200, "zerolinecolor": HSB_NEUTRAL_200},
    "yaxis": {"gridcolor": HSB_NEUTRAL_200, "zerolinecolor": HSB_NEUTRAL_200},
    "margin": {"l": 40, "r": 15, "t": 50, "b": 40},
}


def get_plotly_layout(**kwargs):
    layout = PLOTLY_LAYOUT.copy()
    base_xaxis = {
        **PLOTLY_LAYOUT["xaxis"],
        "title": {"font": {"color": HSB_NEUTRAL_900}},
        "tickfont": {"color": HSB_NEUTRAL_900},
    }
    base_yaxis = {
        **PLOTLY_LAYOUT["yaxis"],
        "title": {"font": {"color": HSB_NEUTRAL_900}},
        "tickfont": {"color": HSB_NEUTRAL_900},
    }
    layout["xaxis"] = base_xaxis
    layout["yaxis"] = base_yaxis

    custom_xaxis = kwargs.pop("xaxis", None)
    custom_yaxis = kwargs.pop("yaxis", None)
    layout.update(kwargs)
    if custom_xaxis is not None:
        layout["xaxis"] = {**base_xaxis, **custom_xaxis}
    if custom_yaxis is not None:
        layout["yaxis"] = {**base_yaxis, **custom_yaxis}
    return layout


def get_class_color(class_name: str) -> str:
    return CHART_COLORS.get(class_name, HSB_PRIMARY)


def get_rank_color(rank: int) -> str:
    if rank == 1:
        return RANK_GOLD
    if rank == 2:
        return RANK_SILVER
    if rank == 3:
        return RANK_BRONZE
    return HSB_NEUTRAL_100


CUSTOM_CSS = f"""
<style>
:root {{
    --hsb-primary: {HSB_PRIMARY};
    --hsb-primary-light: {HSB_PRIMARY_LIGHT};
    --hsb-primary-dark: {HSB_PRIMARY_DARK};
    --hsb-neutral-50: {HSB_NEUTRAL_50};
    --hsb-neutral-100: {HSB_NEUTRAL_100};
    --hsb-neutral-200: {HSB_NEUTRAL_200};
    --hsb-neutral-300: {HSB_NEUTRAL_300};
    --hsb-neutral-700: {HSB_NEUTRAL_700};
    --hsb-neutral-900: {HSB_NEUTRAL_900};
    --hsb-success: {COLOR_SUCCESS};
    --hsb-warning: {COLOR_WARNING};
    --hsb-error: {COLOR_ERROR};
    --hsb-info: {COLOR_INFO};
    /* Streamlit design tokens */
    --primary-color: {HSB_PRIMARY};
}}

.stApp {{
    background:
        linear-gradient(180deg, #f3f6f8 0%, #ffffff 280px),
        linear-gradient(90deg, rgba(0,91,150,0.03) 0%, rgba(255,255,255,0) 50%);
}}

.block-container {{
    /* Reserve space for Streamlit's top toolbar ("Deploy" bar). */
    padding-top: 4.5rem;
    padding-bottom: 2rem;
    max-width: 1240px;
}}

h1, h2, h3, h4 {{
    color: var(--hsb-neutral-900);
    letter-spacing: -0.02em;
}}

p, li, label, [data-testid="stMarkdownContainer"] {{
    color: var(--hsb-neutral-900);
}}

.hsb-site-header {{
    margin-bottom: 1.5rem;
}}

.hsb-utility-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    padding: 0.55rem 1rem;
    border-radius: 14px 14px 0 0;
    background: var(--hsb-primary-dark);
    color: white;
    font-size: 0.82rem;
}}

.hsb-utility-brand,
.hsb-utility-context {{
    font-weight: 700;
    letter-spacing: 0.03em;
}}

.hsb-logo {{
    max-height: 26px;
    width: auto;
    display: inline-block;
    vertical-align: middle;
    filter: brightness(0) invert(1);
}}

.hsb-utility-motto {{
    display: inline-block;
    margin-left: 0.65rem;
    font-size: 0.75rem;
    font-weight: 400;
    letter-spacing: 0.04em;
    opacity: 0.82;
    vertical-align: middle;
}}

.page-header {{
    display: grid;
    grid-template-columns: minmax(0, 1.8fr) minmax(240px, 0.9fr);
    gap: 1.25rem;
    padding: 1.8rem 1.9rem;
    border: 1px solid var(--hsb-neutral-200);
    border-top: 0;
    border-radius: 0 0 18px 18px;
    background:
        linear-gradient(135deg, rgba(0,91,150,0.06), rgba(255,255,255,0.98) 42%),
        white;
    margin-bottom: 1.25rem;
}}

.page-header.public {{
    background:
        linear-gradient(135deg, rgba(0,91,150,0.05), rgba(255,255,255,0.99) 45%),
        white;
}}

.page-header.team {{
    background:
        linear-gradient(135deg, rgba(0,119,200,0.08), rgba(255,255,255,0.99) 45%),
        white;
}}

.page-header.admin {{
    background:
        linear-gradient(135deg, rgba(0,61,102,0.18), rgba(255,255,255,0.99) 48%),
        white;
}}

.page-header-main {{
    min-width: 0;
}}

.page-header-side {{
    border-left: 1px solid var(--hsb-neutral-200);
    padding-left: 1rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 0.9rem;
}}

.page-header.single-column {{
    grid-template-columns: 1fr;
}}

.page-header.single-column .page-header-side {{
    display: none;
}}

.page-eyebrow {{
    color: var(--hsb-primary);
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.55rem;
}}

.page-title {{
    font-size: 2.15rem;
    font-weight: 700;
    line-height: 1.15;
    margin: 0;
    word-break: break-word;
    overflow-wrap: break-word;
    hyphens: auto;
}}

.page-subtitle {{
    margin-top: 0.65rem;
    color: var(--hsb-neutral-700);
    font-size: 1rem;
    line-height: 1.55;
    max-width: 70ch;
}}

.page-tagline {{
    margin-top: 0.75rem;
    font-size: 0.96rem;
    font-weight: 700;
    color: var(--hsb-primary-dark);
}}

.page-side-label {{
    color: var(--hsb-neutral-700);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-size: 0.74rem;
    font-weight: 700;
}}

.page-side-title {{
    font-size: 1rem;
    font-weight: 700;
    color: var(--hsb-neutral-900);
}}

.page-side-copy {{
    color: var(--hsb-neutral-700);
    line-height: 1.5;
    font-size: 0.92rem;
}}

.page-side-list {{
    display: grid;
    gap: 0.45rem;
}}

.page-side-item {{
    padding: 0.55rem 0.65rem;
    border-radius: 12px;
    background: rgba(255,255,255,0.82);
    border: 1px solid var(--hsb-neutral-200);
}}

.registration-form-shell {{
    border: 1px solid var(--hsb-neutral-200);
    border-radius: 18px;
    background: white;
    padding: 1.1rem 1.15rem 0.25rem;
    box-shadow: 0 10px 26px rgba(33, 37, 41, 0.05);
    margin-bottom: 1rem;
}}

.registration-form-title {{
    font-size: 1.08rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}}

.registration-form-copy {{
    color: var(--hsb-neutral-700);
    line-height: 1.5;
    margin-bottom: 0.85rem;
}}

.section-heading {{
    margin: 1.25rem 0 0.75rem;
}}

.section-heading-title {{
    font-size: 1.15rem;
    font-weight: 700;
    margin: 0;
}}

.section-heading-subtitle {{
    color: var(--hsb-neutral-700);
    margin-top: 0.25rem;
    font-size: 0.95rem;
}}

.ui-panel {{
    border: 1px solid var(--hsb-neutral-200);
    border-radius: 14px;
    background: white;
    padding: 1rem 1.1rem;
    margin-bottom: 1rem;
    box-shadow: 0 8px 24px rgba(33, 37, 41, 0.04);
}}

.ui-panel-accent {{
    border-color: rgba(0, 91, 150, 0.25);
    background: linear-gradient(180deg, rgba(0,91,150,0.04), rgba(255,255,255,1));
}}

.ui-panel-muted {{
    background: var(--hsb-neutral-50);
}}

.ui-panel-success {{
    border-color: rgba(47, 125, 74, 0.3);
    background: linear-gradient(180deg, rgba(47,125,74,0.06), rgba(255,255,255,1));
}}

.ui-panel-warning {{
    border-color: rgba(184, 129, 25, 0.28);
    background: linear-gradient(180deg, rgba(184,129,25,0.08), rgba(255,255,255,1));
}}

.ui-panel-danger {{
    border-color: rgba(161, 58, 56, 0.28);
    background: linear-gradient(180deg, rgba(161,58,56,0.07), rgba(255,255,255,1));
}}

.ui-panel-title {{
    margin: 0 0 0.45rem;
    font-size: 1rem;
    font-weight: 700;
}}

.ui-panel-copy {{
    color: var(--hsb-neutral-700);
    margin: 0;
    line-height: 1.55;
}}

.ui-metric-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 0.85rem;
    margin: 0.75rem 0 1rem;
}}

.ui-metric-card {{
    border: 1px solid var(--hsb-neutral-200);
    border-radius: 12px;
    background: white;
    padding: 0.95rem 1rem;
}}

.ui-metric-value {{
    font-size: 1.55rem;
    font-weight: 700;
    color: var(--hsb-primary-dark);
    line-height: 1.1;
}}

.ui-metric-label {{
    margin-top: 0.25rem;
    font-size: 0.88rem;
    color: var(--hsb-neutral-700);
}}

.ui-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.28rem 0.65rem;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 700;
    border: 1px solid transparent;
}}

.ui-badge-phase {{
    background: rgba(0, 91, 150, 0.08);
    color: var(--hsb-primary-dark);
    border-color: rgba(0, 91, 150, 0.14);
}}

.ui-badge-pending {{
    background: rgba(184,129,25,0.12);
    color: #7a5410;
    border-color: rgba(184,129,25,0.2);
}}

.ui-badge-submitted {{
    background: rgba(47,125,74,0.12);
    color: #245f38;
    border-color: rgba(47,125,74,0.2);
}}

.ui-tag-list {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin-top: 0.5rem;
}}

.ui-tag {{
    display: inline-block;
    padding: 0.32rem 0.6rem;
    border-radius: 999px;
    background: var(--hsb-neutral-50);
    border: 1px solid var(--hsb-neutral-200);
    color: var(--hsb-neutral-900);
    font-size: 0.82rem;
}}

.ui-tag-accent {{
    background: rgba(0, 119, 200, 0.08);
    border-color: rgba(0, 119, 200, 0.18);
}}

.feature-card-shell {{
    margin-bottom: 0.6rem;
}}

.feature-card-shell--active {{
    /* Visual highlight is applied via st.container border override below */
}}

.feature-card-heading {{
    margin-bottom: 0.4rem;
}}

.feature-card-domain {{
    display: inline-block;
    margin-bottom: 0.35rem;
    color: var(--hsb-primary);
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

.feature-card-title {{
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}}

.feature-card-copy {{
    color: var(--hsb-neutral-700);
    font-size: 0.92rem;
    line-height: 1.45;
}}

.feature-card-cta {{
    margin-top: 0.45rem;
    font-size: 0.8rem;
    color: var(--hsb-neutral-700);
    font-style: italic;
}}

.feature-card-selected-indicator {{
    margin-top: 0.45rem;
    font-size: 0.82rem;
    font-weight: 700;
    color: var(--hsb-success);
}}

/* Checkbox styling: larger, blue accent */
div[data-testid="stCheckbox"] label {{
    font-weight: 700;
    font-size: 0.95rem;
    cursor: pointer;
    color: var(--hsb-primary-dark) !important;
    -webkit-text-fill-color: var(--hsb-primary-dark) !important;
}}

div[data-testid="stCheckbox"] input[type="checkbox"] {{
    -webkit-appearance: none;
    appearance: none;
    width: 1.35rem;
    height: 1.35rem;
    min-width: 1.35rem;
    background: white;
    border: 2px solid var(--hsb-primary-dark);
    border-radius: 4px;
    cursor: pointer;
    position: relative;
    vertical-align: middle;
    transition: background 0.15s, border-color 0.15s;
}}

div[data-testid="stCheckbox"] input[type="checkbox"]:checked {{
    background: var(--hsb-primary);
    border-color: var(--hsb-primary);
}}

div[data-testid="stCheckbox"] input[type="checkbox"]:checked::after {{
    content: "";
    display: block;
    position: absolute;
    top: 1px;
    left: 4px;
    width: 5px;
    height: 10px;
    border: 2.5px solid white;
    border-top: none;
    border-left: none;
    transform: rotate(45deg);
}}

.leaderboard-list {{
    display: grid;
    gap: 0.75rem;
    margin-top: 0.6rem;
}}

.leaderboard-row {{
    display: grid;
    grid-template-columns: 68px minmax(140px, 1.4fr) minmax(90px, 110px) minmax(90px, 110px) minmax(90px, 110px);
    gap: 0.8rem;
    align-items: center;
    border: 1px solid var(--hsb-neutral-200);
    border-radius: 14px;
    padding: 0.95rem 1rem;
    background: white;
}}

.leaderboard-row.top-1 {{
    border-color: rgba(209, 169, 58, 0.4);
    background: rgba(209, 169, 58, 0.08);
}}

.leaderboard-row.top-2 {{
    border-color: rgba(157, 167, 176, 0.45);
    background: rgba(157, 167, 176, 0.09);
}}

.leaderboard-row.top-3 {{
    border-color: rgba(166, 106, 63, 0.4);
    background: rgba(166, 106, 63, 0.08);
}}

.leaderboard-rank {{
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--hsb-primary-dark);
}}

.leaderboard-team {{
    font-weight: 700;
    color: var(--hsb-neutral-900);
}}

.leaderboard-meta-label {{
    font-size: 0.74rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--hsb-neutral-700);
}}

.leaderboard-meta-value {{
    font-size: 0.98rem;
    font-weight: 700;
    color: var(--hsb-neutral-900);
}}

.state-card {{
    text-align: center;
    padding: 1.5rem 1.2rem;
}}

.state-card-title {{
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 0.45rem;
}}

.state-card-copy {{
    color: var(--hsb-neutral-700);
    line-height: 1.55;
    margin-bottom: 0.9rem;
}}

.stButton > button {{
    border-radius: 12px;
    min-height: 2.8rem;
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: var(--hsb-neutral-900) !important;
    -webkit-text-fill-color: var(--hsb-neutral-900) !important;
    font-weight: 700;
    border: 1px solid rgba(0,91,150,0.16);
}}

.stButton > button:hover {{
    background: var(--hsb-neutral-50) !important;
    background-color: var(--hsb-neutral-50) !important;
    color: var(--hsb-neutral-900) !important;
    -webkit-text-fill-color: var(--hsb-neutral-900) !important;
    border-color: rgba(0,91,150,0.35);
    box-shadow: 0 10px 22px rgba(0, 91, 150, 0.10);
}}

.stFormSubmitButton > button {{
    border-radius: 14px;
    min-height: 3rem;
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: var(--hsb-neutral-900) !important;
    -webkit-text-fill-color: var(--hsb-neutral-900) !important;
    font-weight: 700;
}}

/* Primary actions (e.g. "Team beitreten") in HSB blue instead of default red */
.stButton > button[kind="primary"],
.stFormSubmitButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] button,
button[kind="primaryFormSubmit"] {{
    background: var(--hsb-primary) !important;
    background-color: var(--hsb-primary) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border: 1px solid var(--hsb-primary) !important;
}}

.stButton > button[kind="primary"]:hover,
.stFormSubmitButton > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] button:hover,
button[kind="primaryFormSubmit"]:hover {{
    background: var(--hsb-primary-light) !important;
    background-color: var(--hsb-primary-light) !important;
    border-color: var(--hsb-primary-light) !important;
    color: #ffffff !important;
}}

.stButton > button[kind="primary"] *,
.stFormSubmitButton > button[kind="primary"] *,
div[data-testid="stFormSubmitButton"] button *,
button[kind="primaryFormSubmit"] * {{
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}}

div[data-testid="stTextInputRootElement"] input,
div[data-testid="stNumberInput"] input {{
    width: 100%;
    box-sizing: border-box;
    border-radius: 14px;
    border: 1.5px solid var(--hsb-neutral-300);
    background: #fbfcfd;
    color: var(--hsb-neutral-900) !important;
    -webkit-text-fill-color: var(--hsb-neutral-900) !important;
    caret-color: var(--hsb-neutral-900);
    min-height: 3.15rem;
    padding-left: 0.9rem;
    font-size: 1rem;
}}

div[data-testid="stTextInputRootElement"] input::placeholder,
div[data-testid="stNumberInput"] input::placeholder {{
    color: var(--hsb-neutral-700) !important;
    opacity: 1;
}}

div[data-testid="stTextInputRootElement"] input:focus,
div[data-testid="stNumberInput"] input:focus {{
    border-color: var(--hsb-primary-light);
    box-shadow: 0 0 0 3px rgba(0, 119, 200, 0.12);
}}

/* Selektoren fuer Dropdowns (Selectbox, Optionen, aktive Auswahl) */
div[data-baseweb="select"] > div {{
    background: #fbfcfd !important;
    color: var(--hsb-neutral-900) !important;
    border-color: var(--hsb-neutral-300) !important;
}}

div[data-baseweb="select"] span,
div[data-baseweb="select"] input {{
    color: var(--hsb-neutral-900) !important;
    -webkit-text-fill-color: var(--hsb-neutral-900) !important;
}}

ul[role="listbox"] li,
ul[role="listbox"] div {{
    color: var(--hsb-neutral-900) !important;
    background: white !important;
}}

/* Teamnamen und sonstige Textknoten in Streamlit-Listen lesbar halten */
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span {{
    color: var(--hsb-neutral-900) !important;
}}

[data-testid="stWidgetLabel"] {{
    font-weight: 600;
}}

div[data-testid="stForm"] {{
    border: 0;
    padding: 0;
    background: transparent;
}}

div[data-testid="stProgressBar"] > div > div {{
    background-color: var(--hsb-primary);
}}

div[data-testid="stMetric"] {{
    border: 1px solid var(--hsb-neutral-200);
    border-radius: 12px;
    padding: 0.75rem 0.85rem;
    background: white;
}}

details {{
    border: 2px solid var(--hsb-primary) !important;
    border-radius: 12px;
    background: white !important;
}}

details summary {{
    font-weight: 700;
    color: var(--hsb-primary) !important;
    -webkit-text-fill-color: var(--hsb-primary) !important;
    background: white !important;
    border-left: 3px solid var(--hsb-primary);
    padding-left: 0.6rem;
    border-radius: 10px 10px 0 0;
}}

details summary:hover {{
    color: var(--hsb-primary-light) !important;
    -webkit-text-fill-color: var(--hsb-primary-light) !important;
}}

details[open] summary {{
    border-bottom: 1px solid var(--hsb-neutral-100);
    margin-bottom: 0.5rem;
    border-radius: 10px 10px 0 0;
}}

details summary > * {{
    color: var(--hsb-primary) !important;
    -webkit-text-fill-color: var(--hsb-primary) !important;
}}

details summary p {{
    color: var(--hsb-primary) !important;
    -webkit-text-fill-color: var(--hsb-primary) !important;
}}

/* Ensure expander inner content is always dark-on-white */
details > div,
details > section,
[data-testid="stExpanderDetails"] {{
    background: white !important;
    color: var(--hsb-neutral-900) !important;
}}

/* Fix st.code dark blocks inside expanders */
details pre,
details code,
[data-testid="stExpanderDetails"] pre,
[data-testid="stExpanderDetails"] code {{
    background: var(--hsb-neutral-50) !important;
    color: var(--hsb-neutral-900) !important;
    border: 1px solid var(--hsb-neutral-200);
    border-radius: 8px;
}}

/* Hard override for Plotly text contrast (axes, labels, legend). */
.js-plotly-plot .plotly .xtick text,
.js-plotly-plot .plotly .ytick text,
.js-plotly-plot .plotly .xaxislayer-above text,
.js-plotly-plot .plotly .yaxislayer-above text,
.js-plotly-plot .plotly .g-xtitle text,
.js-plotly-plot .plotly .g-ytitle text,
.js-plotly-plot .plotly .gtitle text,
.js-plotly-plot .plotly .legend text,
.js-plotly-plot .plotly .annotation text {{
    fill: #212529 !important;
    color: #212529 !important;
}}

@media (max-width: 900px) {{
    .page-header {{
        grid-template-columns: 1fr;
    }}
    .page-header-side {{
        border-left: 0;
        padding-left: 0;
        border-top: 1px solid var(--hsb-neutral-200);
        padding-top: 1rem;
    }}
    .leaderboard-row {{
        grid-template-columns: 48px 1fr !important;
        gap: 0.4rem 0.6rem;
    }}
    .leaderboard-row > *:nth-child(n+3) {{
        grid-column: 2;
    }}
    .page-title {{
        font-size: 1.6rem;
    }}
    .ui-metric-grid {{
        grid-template-columns: 1fr 1fr;
    }}
}}

@media (max-width: 600px) {{
    .page-title {{
        font-size: 1.25rem;
    }}
    .block-container {{
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}
    .ui-metric-grid {{
        grid-template-columns: 1fr;
    }}
    .leaderboard-row {{
        grid-template-columns: 1fr !important;
        gap: 0.25rem;
    }}
    /* Reduce Plotly chart font sizes on small screens */
    .js-plotly-plot .plotly .xtick text,
    .js-plotly-plot .plotly .ytick text {{
        font-size: 9px !important;
    }}
    .js-plotly-plot .plotly .gtitle {{
        font-size: 11px !important;
    }}
    .js-plotly-plot .plotly .g-xtitle text,
    .js-plotly-plot .plotly .g-ytitle text {{
        font-size: 10px !important;
    }}
    /* Hide modebar on touch devices */
    .js-plotly-plot .plotly .modebar {{
        display: none !important;
    }}
    /* Reduce padding in expanders */
    details summary {{
        font-size: 0.95rem;
    }}
    /* Utility-bar: hide motto on very small screens */
    .hsb-utility-motto {{
        display: none;
    }}
}}

@media (min-width: 1400px) {{
    [data-testid="stMetricValue"] {{
        font-size: 2.6rem !important;
    }}
}}
</style>
"""


def inject_custom_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_page_header(
    title: str,
    subtitle: str = "",
    eyebrow: str = "Hochschule Bremen",
    tagline: str = "",
    side_label: str = "Quicklinks",
    side_title: str = "",
    side_copy: str = "",
    side_items: list[str] | None = None,
    variant: str = "public",
    utility_context: str = "",
) -> str:
    subtitle_html = f'<div class="page-subtitle">{escape(subtitle)}</div>' if subtitle else ""
    side_items_html = ""
    if side_items:
        side_items_html = '<div class="page-side-list">' + "".join(
            f'<div class="page-side-item">{escape(item)}</div>' for item in side_items
        ) + "</div>"
    side_title_html = f'<div class="page-side-title">{escape(side_title)}</div>' if side_title else ""
    side_copy_html = f'<div class="page-side-copy">{escape(side_copy)}</div>' if side_copy else ""
    has_side = bool(side_label or side_title or side_copy or side_items)
    header_class = f"page-header {escape(variant)}"
    if not has_side:
        header_class += " single-column"
    utility_context_html = (
        f'<div class="hsb-utility-context">{escape(utility_context)}</div>' if utility_context else ""
    )
    _HSB_LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/f/fd/Logo_HSB_Hochschule_Bremen.png"
    return (
        '<section class="hsb-site-header">'
        '<div class="hsb-utility-bar">'
        '<div class="hsb-utility-brand">'
        f'<img src="{_HSB_LOGO_URL}" alt="HSB Hochschule Bremen" '
        'class="hsb-logo" onerror="this.style.display=\'none\';this.nextSibling.style.display=\'inline\'">'
        '<span class="hsb-logo-fallback" style="display:none">HSB Hochschule Bremen</span>'
        '<span class="hsb-utility-motto">Science for the real World</span>'
        '</div>'
        f"{utility_context_html}"
        "</div>"
        f'<section class="{header_class}">'
        '<div class="page-header-main">'
        f'<div class="page-eyebrow">{escape(eyebrow)}</div>'
        f'<h1 class="page-title">{escape(title)}</h1>'
        f"{subtitle_html}"
        "</div>"
        '<aside class="page-header-side">'
        f'<div class="page-side-label">{escape(side_label)}</div>'
        f"{side_title_html}{side_copy_html}{side_items_html}"
        "</aside>"
        "</section>"
        "</section>"
    )


def render_section_heading(title: str, subtitle: str = "") -> str:
    subtitle_html = f'<div class="section-heading-subtitle">{escape(subtitle)}</div>' if subtitle else ""
    return (
        f'<div class="section-heading">'
        f'<div class="section-heading-title">{escape(title)}</div>'
        f"{subtitle_html}"
        f"</div>"
    )


def render_panel(title: str, body: str, tone: str = "default") -> str:
    tone_class = {
        "default": "",
        "accent": " ui-panel-accent",
        "muted": " ui-panel-muted",
        "success": " ui-panel-success",
        "warning": " ui-panel-warning",
        "danger": " ui-panel-danger",
    }.get(tone, "")
    title_html = f'<div class="ui-panel-title">{escape(title)}</div>' if title else ""
    return f'<section class="ui-panel{tone_class}">{title_html}{body}</section>'


def render_metric_grid(items: list[dict]) -> str:
    cards = []
    for item in items:
        cards.append(
            '<div class="ui-metric-card">'
            f'<div class="ui-metric-value">{escape(str(item["value"]))}</div>'
            f'<div class="ui-metric-label">{escape(item["label"])}</div>'
            "</div>"
        )
    return '<div class="ui-metric-grid">' + "".join(cards) + "</div>"


def render_tag_list(values: list[str], variant: str = "neutral") -> str:
    if not values:
        return ""
    variant_class = " ui-tag-accent" if variant == "accent" else ""
    tags = "".join(f'<span class="ui-tag{variant_class}">{escape(value)}</span>' for value in values)
    return f'<div class="ui-tag-list">{tags}</div>'


def render_phase_badge(phase: str) -> str:
    phase_labels = {
        "registration": "📋 Registrierung",
        "feature_selection": "🔬 Phase 1: Feature-Auswahl",
        "training": "⚙️ Phase 2: Training",
        "results": "🏆 Phase 3: Ergebnisse",
    }
    label = phase_labels.get(phase, phase.replace("_", " ").title())
    return f'<span class="ui-badge ui-badge-phase">{label}</span>'


def render_status_badge(submitted: bool) -> str:
    if submitted:
        return '<span class="ui-badge ui-badge-submitted">Abgegeben</span>'
    return '<span class="ui-badge ui-badge-pending">Ausstehend</span>'


def render_rank_label(rank: int) -> str:
    if rank == 1:
        return "🏆"
    if rank == 2:
        return "🥈"
    if rank == 3:
        return "🥉"
    return str(rank)


def render_leaderboard(entries: list[dict], include_time: bool = True, include_features: bool = False) -> str:
    if not entries:
        return render_panel(
            "Leaderboard",
            '<p class="ui-panel-copy">Noch keine Ergebnisse vorhanden.</p>',
            tone="muted",
        )

    rows = []
    for entry in entries:
        row_class = ""
        if entry["rank"] <= 3:
            row_class = f" top-{entry['rank']}"
        time_col = ""
        if include_time:
            time_col = (
                '<div>'
                '<div class="leaderboard-meta-label">Zeit</div>'
                f'<div class="leaderboard-meta-value">{entry["train_time"]:.2f} s</div>'
                "</div>"
            )
        features_html = ""
        if include_features and entry.get("features"):
            feature_tags = " ".join(
                f'<span class="ui-tag ui-tag-accent" style="font-size:0.75rem;padding:0.2rem 0.45rem;">{escape(f)}</span>'
                for f in entry["features"]
            )
            features_html = (
                '<div style="grid-column:1/-1;margin-top:0.3rem;">'
                '<div class="leaderboard-meta-label">Features</div>'
                f'<div style="display:flex;flex-wrap:wrap;gap:0.3rem;margin-top:0.25rem;">{feature_tags}</div>'
                "</div>"
            )
        rows.append(
            f'<div class="leaderboard-row{row_class}">'
            f'<div class="leaderboard-rank">{render_rank_label(entry["rank"])}</div>'
            f'<div class="leaderboard-team">{escape(entry["team_name"])}</div>'
            '<div>'
            '<div class="leaderboard-meta-label">F1-Score</div>'
            f'<div class="leaderboard-meta-value">{entry["f1_macro"]*100:.2f} %</div>'
            "</div>"
            '<div>'
            '<div class="leaderboard-meta-label">Accuracy</div>'
            f'<div class="leaderboard-meta-value">{entry["accuracy"]*100:.2f} %</div>'
            "</div>"
            f"{time_col}"
            f"{features_html}"
            "</div>"
        )
    return '<div class="leaderboard-list">' + "".join(rows) + "</div>"
