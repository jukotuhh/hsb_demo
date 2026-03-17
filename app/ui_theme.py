"""
ui_theme.py — UI Theme & Design Tokens für die Bearing Challenge
================================================================

Dieses Modul definiert das visuelle Erscheinungsbild der Challenge-App,
basierend auf dem öffentlich sichtbaren HSB-Webauftritt (web-inspiriert).

Design-Prinzipien:
    - HSB-Identität: seriös, technisch, klar, akademisch
    - Funktionalität vor Dekoration
    - Dualer Kontext: Smartphone (Studierende) + Beamer (Dozent)
    - Barrierefreiheit: Kontraste, lesbare Schriftgrößen
"""

import streamlit as st


# ============================================================
# Farbpalette (HSB-inspiriert)
# ============================================================

# Primärfarben (basierend auf HSB-Website)
HSB_PRIMARY = "#005B96"          # Hauptfarbe: Buttons, Akzente
HSB_PRIMARY_LIGHT = "#0077C8"    # Hover-Zustände, Links
HSB_PRIMARY_DARK = "#003D66"     # Aktive/Gedrückte Zustände

# Neutrale Farben
HSB_NEUTRAL_50 = "#F8F9FA"       # Hintergrund (hell)
HSB_NEUTRAL_100 = "#E9ECEF"      # Kartenhintergründe
HSB_NEUTRAL_200 = "#DEE2E6"      # Borders, Divider
HSB_NEUTRAL_700 = "#495057"      # Sekundärtext
HSB_NEUTRAL_900 = "#212529"      # Primärtext

# Funktionsfarben
COLOR_SUCCESS = "#28A745"        # Erfolg
COLOR_WARNING = "#FFC107"        # Warnung
COLOR_ERROR = "#DC3545"          # Fehler
COLOR_INFO = "#17A2B8"           # Info

# Leaderboard-Farben
RANK_GOLD = "#FFD700"
RANK_SILVER = "#C0C0C0"
RANK_BRONZE = "#CD7F32"

# Chart-Farben (Klassen)
CHART_COLORS = {
    "Normal": COLOR_SUCCESS,          # Grün — gesunder Zustand
    "Innenring (IR)": COLOR_ERROR,    # Rot — kritischer Fehler
    "Außenring (OR)": HSB_PRIMARY,    # HSB-Blau — mittlerer Fehler
    "Kugel (B)": COLOR_WARNING,       # Gelb — variabler Fehler
}

CHART_PRIMARY = HSB_PRIMARY
CHART_SECONDARY = HSB_PRIMARY_LIGHT
CHART_HIGHLIGHT = COLOR_SUCCESS


# ============================================================
# Spacing & Layout (8px-Grid)
# ============================================================

SPACE_XS = "4px"
SPACE_SM = "8px"
SPACE_MD = "16px"
SPACE_LG = "24px"
SPACE_XL = "32px"
SPACE_XXL = "48px"

RADIUS_SM = "4px"
RADIUS_MD = "8px"
RADIUS_LG = "12px"


# ============================================================
# Plotly Layout-Template
# ============================================================

PLOTLY_LAYOUT = {
    "plot_bgcolor": HSB_NEUTRAL_50,
    "paper_bgcolor": "white",
    "font": {"family": "sans-serif", "size": 14, "color": HSB_NEUTRAL_900},
    "xaxis": {"gridcolor": HSB_NEUTRAL_200},
    "yaxis": {"gridcolor": HSB_NEUTRAL_200},
}


def get_plotly_layout(**kwargs):
    """
    Gibt ein Plotly-Layout-Dict mit HSB-Theme zurück.
    
    Beispiel:
        fig.update_layout(**get_plotly_layout(title="Mein Chart", height=400))
    """
    layout = PLOTLY_LAYOUT.copy()
    layout.update(kwargs)
    return layout


def get_class_color(class_name: str) -> str:
    """Gibt die Farbe für eine Fehlerklasse zurück."""
    return CHART_COLORS.get(class_name, HSB_PRIMARY)


def get_rank_color(rank: int) -> str:
    """Gibt die Farbe für einen Leaderboard-Rang zurück."""
    if rank == 1:
        return RANK_GOLD
    elif rank == 2:
        return RANK_SILVER
    elif rank == 3:
        return RANK_BRONZE
    else:
        return HSB_NEUTRAL_100


# ============================================================
# Custom CSS
# ============================================================

CUSTOM_CSS = f"""
<style>
/* ============================================================
   Allgemein
   ============================================================ */

/* Entferne überschüssige Padding */
.block-container {{
    padding-top: 2rem;
    padding-bottom: 2rem;
}}

/* ============================================================
   Feature-Karten
   ============================================================ */

.feature-card {{
    border: 1px solid {HSB_NEUTRAL_200};
    border-radius: {RADIUS_MD};
    padding: {SPACE_MD};
    background-color: {HSB_NEUTRAL_50};
    transition: all 0.2s ease;
    margin-bottom: {SPACE_MD};
}}

.feature-card:hover {{
    box-shadow: 0 4px 8px rgba(0, 91, 150, 0.1);
    transform: translateY(-2px);
}}

.feature-card.selected {{
    border: 2px solid {HSB_PRIMARY};
    background-color: rgba(0, 119, 200, 0.05);
}}

.feature-card.locked {{
    opacity: 0.6;
    cursor: not-allowed;
}}

/* ============================================================
   Status-Badges
   ============================================================ */

.badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: {RADIUS_SM};
    font-size: 0.875rem;
    font-weight: 600;
}}

.badge-pending {{
    background-color: rgba(255, 193, 7, 0.2);
    color: #856404;
}}

.badge-submitted {{
    background-color: rgba(40, 167, 69, 0.2);
    color: #155724;
}}

.badge-locked {{
    background-color: {HSB_NEUTRAL_200};
    color: {HSB_NEUTRAL_700};
}}

/* ============================================================
   Leaderboard
   ============================================================ */

.leaderboard-row {{
    padding: {SPACE_MD};
    border-radius: {RADIUS_MD};
    margin-bottom: {SPACE_SM};
}}

.rank-1 {{
    background-color: rgba(255, 215, 0, 0.1);
    border-left: 4px solid {RANK_GOLD};
}}

.rank-2 {{
    background-color: rgba(192, 192, 192, 0.1);
    border-left: 4px solid {RANK_SILVER};
}}

.rank-3 {{
    background-color: rgba(205, 127, 50, 0.1);
    border-left: 4px solid {RANK_BRONZE};
}}

/* ============================================================
   QR-Code Container
   ============================================================ */

.qr-container {{
    background-color: white;
    padding: {SPACE_LG};
    border-radius: {RADIUS_LG};
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    text-align: center;
}}

/* ============================================================
   Responsive: Mobile
   ============================================================ */

@media (max-width: 768px) {{
    /* Feature-Karten: volle Breite auf Mobile */
    [data-testid="stHorizontalBlock"] {{
        flex-direction: column;
    }}
    
    .feature-card {{
        width: 100% !important;
    }}
    
    /* Reduzierte Schriftgröße auf Mobile */
    h1 {{
        font-size: 1.75rem !important;
    }}
    
    h2 {{
        font-size: 1.5rem !important;
    }}
}}

/* ============================================================
   Responsive: Beamer (große Schrift)
   ============================================================ */

@media (min-width: 1400px) {{
    /* Größere Metriken für Beamer */
    [data-testid="stMetricValue"] {{
        font-size: 3rem !important;
    }}
    
    h1 {{
        font-size: 3rem !important;
    }}
    
    h2 {{
        font-size: 2.5rem !important;
    }}
    
    /* Größere Tabellenschrift */
    table {{
        font-size: 1.25rem !important;
    }}
}}

/* ============================================================
   Phase-Badge (Admin)
   ============================================================ */

.phase-badge {{
    display: inline-block;
    padding: 8px 20px;
    border-radius: {RADIUS_MD};
    font-size: 1.25rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

.phase-registration {{
    background-color: rgba(23, 162, 184, 0.2);
    color: #0c5460;
}}

.phase-feature-selection {{
    background-color: rgba(255, 193, 7, 0.2);
    color: #856404;
}}

.phase-training {{
    background-color: rgba(0, 91, 150, 0.2);
    color: {HSB_PRIMARY_DARK};
}}

.phase-results {{
    background-color: rgba(40, 167, 69, 0.2);
    color: #155724;
}}

/* ============================================================
   Buttons (Streamlit Override)
   ============================================================ */

.stButton > button {{
    border-radius: {RADIUS_MD};
    font-weight: 600;
    transition: all 0.2s ease;
}}

.stButton > button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 91, 150, 0.2);
}}

/* ============================================================
   Expander (Akkordeons)
   ============================================================ */

.streamlit-expanderHeader {{
    background-color: {HSB_NEUTRAL_50};
    border-radius: {RADIUS_MD};
    font-weight: 600;
}}

</style>
"""


def inject_custom_css():
    """
    Injiziert das Custom CSS in die Streamlit-App.
    
    Sollte in der App einmalig aufgerufen werden (nach st.set_page_config).
    """
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================
# Helper-Funktionen für UI-Komponenten
# ============================================================

def render_phase_badge(phase: str) -> str:
    """
    Rendert einen HTML-Badge für die aktuelle Challenge-Phase.
    
    Returns:
        HTML-String (für st.markdown(..., unsafe_allow_html=True))
    """
    phase_labels = {
        "registration": "🎫 Registrierung",
        "feature_selection": "🔧 Feature-Auswahl",
        "training": "⚙️ Training",
        "results": "🏆 Ergebnisse",
    }
    
    label = phase_labels.get(phase, phase.upper())
    css_class = f"phase-{phase.replace('_', '-')}"
    
    return f'<div class="phase-badge {css_class}">{label}</div>'


def render_status_badge(submitted: bool) -> str:
    """
    Rendert einen Status-Badge (Ausstehend / Abgegeben).
    
    Returns:
        HTML-String
    """
    if submitted:
        return '<span class="badge badge-submitted">✅ Abgegeben</span>'
    else:
        return '<span class="badge badge-pending">⏳ Ausstehend</span>'


def render_rank_emoji(rank: int) -> str:
    """Gibt das Emoji für einen Leaderboard-Rang zurück."""
    if rank == 1:
        return "🥇"
    elif rank == 2:
        return "🥈"
    elif rank == 3:
        return "🥉"
    else:
        return f"{rank}."
