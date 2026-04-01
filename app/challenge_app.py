"""
challenge_app.py — Bearing Challenge: Interaktive Classroom-App
===============================================================

Streamlit-App für eine Echtzeit-Challenge, bei der Teams von Studierenden
gegeneinander antreten, indem sie 4 aus 11 Features auswählen und ein
ML-Modell trainiert wird. Ein Live-Leaderboard zeigt die Ergebnisse.

Routing:
    /?admin=<SECRET>    → Admin-Panel (Dozent)
    /?team=<team_id>    → Team-Ansicht (Studierende)
    /                   → Registrierung

Phasen:
    1. registration      → Teams registrieren sich
    2. feature_selection → Teams wählen 4 Features
    3. training          → Dozent startet Training
    4. results           → Leaderboard & Analyse
"""

import os
import sys
import hmac
import time
from html import escape
from io import BytesIO
from urllib.parse import unquote

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Projektverzeichnis zum Pfad hinzufügen
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# QR-Code
try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False
    print("qrcode-Library nicht installiert. QR-Code wird nicht angezeigt.")

# Auto-Refresh
try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False
    print("streamlit-autorefresh nicht installiert. Auto-Refresh deaktiviert.")

# Eigene Module
from src.data_loader import prepare_dataset, generate_demo_data, CLASS_NAMES
from src.features import FEATURE_NAMES, _compute_spectrum, extract_all_features
from src.feature_info import FEATURE_INFO
from src import challenge_state
from app.ui_theme import (
    inject_custom_css,
    get_plotly_layout,
    get_class_color,
    render_leaderboard,
    render_metric_grid,
    render_page_header,
    render_panel,
    render_phase_badge,
    render_section_heading,
    render_status_badge,
    render_tag_list,
    CHART_COLORS,
    HSB_PRIMARY,
    HSB_PRIMARY_LIGHT,
    HSB_NEUTRAL_900,
)


# ============================================================
# Konfiguration
# ============================================================

st.set_page_config(
    page_title="Hörsaalübung Mustererkennung | HSB",
    layout="wide",
    initial_sidebar_state="collapsed",  # Sidebar auf Mobile verstecken
)

inject_custom_css()

# Admin-Secret aus Umgebungsvariable
ADMIN_SECRET = os.environ.get("CHALLENGE_ADMIN_SECRET", "hsb2026")

# App-URL (für QR-Code)
APP_URL = os.environ.get("CHALLENGE_APP_URL", "http://localhost:8501")


# ============================================================
# Daten laden (gecacht)
# ============================================================

@st.cache_data(show_spinner="Daten werden geladen...")
def load_data():
    """Lädt Modell- und Explorationsdaten (normalisiert + roh)."""
    data_dir = os.path.join(PROJECT_DIR, "data")
    try:
        # Wichtig: prepare_dataset/load_mat_files sucht rekursiv unterhalb von data_dir.
        # Daher hier kein top-level .mat-Check, sonst faellt die App faelschlich
        # auf Demo-Daten zurueck, wenn die Dateien z.B. in data/archive/raw liegen.
        model_data = prepare_dataset(data_dir, segment_length=1024, overlap=0.5, normalize=True)
        explore_data = prepare_dataset(data_dir, segment_length=1024, overlap=0.5, normalize=False)
        return model_data, explore_data, False
    except (FileNotFoundError, ValueError):
        model_data = generate_demo_data(n_per_class=500, segment_length=1024, normalize=True)
        explore_data = generate_demo_data(n_per_class=500, segment_length=1024, normalize=False)
        return model_data, explore_data, True


# Daten laden
model_data, explore_data, is_demo = load_data()
X_train = model_data["X_train"]
X_test = model_data["X_test"]
y_train = model_data["y_train"]
y_test = model_data["y_test"]
X_train_explore = explore_data["X_train"]
X_test_explore = explore_data["X_test"]
y_train_explore = explore_data["y_train"]
y_test_explore = explore_data["y_test"]
X_all = np.concatenate([X_train_explore, X_test_explore], axis=0)
y_all = np.concatenate([y_train_explore, y_test_explore], axis=0)


@st.cache_data(show_spinner=False)
def get_feature_overview():
    """Berechnet alle 11 Features fuer den gesamten Datensatz (Train + Test)."""
    feature_df = extract_all_features(X_all).copy()
    y_source = y_all
    feature_df["class_name"] = [CLASS_NAMES[idx] for idx in y_source]
    return feature_df


@st.cache_data(show_spinner=False)
def get_feature_projection():
    """Erzeugt eine 2D-PCA-Projektion ueber alle 11 Features."""
    feature_df = get_feature_overview().copy()
    X_features = feature_df[FEATURE_NAMES].values
    X_scaled = StandardScaler().fit_transform(X_features)
    pca = PCA(n_components=2, random_state=42)
    projected = pca.fit_transform(X_scaled)

    feature_df["pc1"] = projected[:, 0]
    feature_df["pc2"] = projected[:, 1]
    explained = pca.explained_variance_ratio_
    return feature_df, explained.tolist()


# ============================================================
# Helper-Funktionen
# ============================================================

def get_app_url_for_qr():
    """Gibt die App-URL für den QR-Code zurück."""
    # Versuche, die URL aus Streamlit zu extrahieren (wenn deployed)
    try:
        from streamlit.web import cli as stcli
        return APP_URL
    except:
        return APP_URL


def generate_qr_code(url: str) -> bytes:
    """Generiert einen QR-Code als PNG-Bytes."""
    if not HAS_QRCODE:
        return None
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def plot_signal_and_fft(signal, title="", color=HSB_PRIMARY, fs=12000):
    """Plottet Zeitsignal und FFT gestapelt (mobile-freundlich)."""
    t_ms = np.arange(len(signal)) / fs * 1000
    freqs, mag = _compute_spectrum(signal, fs)

    _axis_font = dict(color=HSB_NEUTRAL_900)

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=["Zeitsignal", "Frequenzspektrum (FFT)"],
        vertical_spacing=0.22,
    )

    fig.add_trace(go.Scatter(
        x=t_ms, y=signal, mode="lines",
        line=dict(color=color, width=1.5),
        name="Signal",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=freqs, y=mag, mode="lines", fill="tozeroy",
        line=dict(color=color, width=1.5),
        fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)",
        name="Spektrum",
    ), row=2, col=1)

    fig.update_xaxes(title_text="Zeit (ms)", title_font=_axis_font, tickfont=_axis_font, row=1, col=1)
    fig.update_xaxes(title_text="Frequenz (Hz)", title_font=_axis_font, tickfont=_axis_font, range=[0, 6000], row=2, col=1)
    fig.update_yaxes(title_text="Amplitude", title_font=_axis_font, tickfont=_axis_font, row=1, col=1)
    fig.update_yaxes(title_text="Amplitude", title_font=_axis_font, tickfont=_axis_font, row=2, col=1)

    for ann in fig.layout.annotations:
        ann.font.color = HSB_NEUTRAL_900

    fig.update_layout(**get_plotly_layout(title=title, height=580))
    return fig


_CM_SHORT_NAMES = ["Normal", "IR", "OR", "Kugel"]


def plot_confusion_matrix(cm, title="Konfusionsmatrix"):
    """Plottet die Konfusionsmatrix (mobile-optimiert)."""
    cm_array = np.asarray(cm, dtype=float)
    row_sums = cm_array.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1.0
    cm_percent = (cm_array / row_sums) * 100.0
    cm_text = [
        [f"{int(cm_array[r, c])}<br>{cm_percent[r, c]:.0f}%" for c in range(cm_array.shape[1])]
        for r in range(cm_array.shape[0])
    ]
    fig = go.Figure(data=go.Heatmap(
        z=cm_percent, x=_CM_SHORT_NAMES, y=_CM_SHORT_NAMES,
        text=cm_text, texttemplate="%{text}",
        textfont={"size": 15},
        colorscale=[[0.0, "#F8F9FA"], [0.5, "#0077C8"], [1.0, "#003D66"]],
        showscale=False,
        zmin=0,
        zmax=100,
    ))
    fig.update_layout(
        **get_plotly_layout(
            title=title,
            height=370,
            margin=dict(l=50, r=10, t=50, b=50),
            xaxis=dict(
                title=dict(text="Vorhersage", font=dict(color="#212529", size=13)),
                tickfont=dict(color="#212529", size=13),
                side="bottom",
            ),
            yaxis=dict(
                autorange="reversed",
                title=dict(text="Wahrheit", font=dict(color="#212529", size=13)),
                tickfont=dict(color="#212529", size=13),
            ),
        )
    )
    return fig


def plot_feature_importances(importances, feature_names, title="Feature Importances"):
    """Plottet Feature Importances als horizontales Balkendiagramm."""
    importances = np.asarray(importances, dtype=float)
    feature_names = np.asarray(feature_names)
    sorted_idx = np.argsort(importances)
    fig = go.Figure(go.Bar(
        x=importances[sorted_idx],
        y=feature_names[sorted_idx],
        orientation="h",
        marker_color=HSB_PRIMARY,
        text=[f"{v:.3f}" for v in importances[sorted_idx]],
        textposition="auto",
    ))
    fig.update_layout(**get_plotly_layout(
        title=title,
        xaxis_title="Wichtigkeit",
        height=max(300, len(feature_names) * 30),
        margin=dict(l=200, r=20, t=50, b=40),
    ))
    return fig


def format_percent(value: float) -> str:
    """Formatiert einen Wert als Prozent-String."""
    return f"{value * 100:.2f} %"


def render_message_panel(title: str, text: str, tone: str = "default"):
    """Rendert eine kurze Hinweisbox im Theme-Stil."""
    body = f'<p class="ui-panel-copy">{escape(text)}</p>'
    st.markdown(render_panel(title, body, tone=tone), unsafe_allow_html=True)


def render_team_submission_cards(teams: dict):
    """Rendert den Status aller Teams als Kartenliste."""
    if not teams:
        render_message_panel("Noch keine Teams", "Aktuell sind keine Teams registriert.", tone="muted")
        return

    for team in teams.values():
        features = team.get("selected_features") or []
        feature_html = (
            render_tag_list(features, variant="accent")
            if features
            else '<p class="ui-panel-copy">Noch keine Features ausgewählt.</p>'
        )
        body = (
            f"{render_status_badge(team['submitted'])}"
            f"{feature_html}"
        )
        st.markdown(render_panel(team["name"], body), unsafe_allow_html=True)


# ============================================================
# Routing
# ============================================================

query_params = st.query_params


def _recover_query_value(param_name: str) -> str | None:
    """
    Liest Query-Parameter robust aus und faengt auch falsch codierte Varianten ab.

    Beispiel einer fehlerhaften URL:
        ?admin%3Dhsb2026
    In diesem Fall liefert Streamlit keinen "admin"-Key, sondern den Key "admin=hsb2026".
    """
    direct_value = query_params.get(param_name, None)
    if direct_value:
        return direct_value

    token = f"{param_name}="
    for raw_key in query_params.keys():
        decoded_key = unquote(str(raw_key))
        if decoded_key.startswith(token):
            value = decoded_key[len(token):]
            if "&" in value:
                value = value.split("&", 1)[0]
            return value or None
    return None


admin_key = _recover_query_value("admin")
team_id = _recover_query_value("team")
dozent_flag = _recover_query_value("dozent")
is_teacher_entry = (
    dozent_flag is not None
    and str(dozent_flag).strip().lower() not in {"0", "false", "no", "off"}
)

# Admin-Authentifizierung
is_admin = False
if admin_key:
    is_admin = hmac.compare_digest(admin_key, ADMIN_SECRET)
    if not is_admin:
        render_message_panel("Zugriff verweigert", "Das Admin-Passwort ist ungültig.", tone="danger")
        st.stop()
    st.session_state["admin_mode"] = True

# Separate Dozenten-URL: /?dozent=1
if is_teacher_entry and not is_admin:
    st.markdown(
        render_page_header(
            "Dozenten-Zugang",
            "Bitte melden Sie sich mit dem Admin-Passwort an, um das Challenge Control Panel zu oeffnen.",
            eyebrow="Dozent",
            tagline="Zukunft gemeinsam gestalten",
            side_label="Lehransicht",
            side_title="Admin-Login",
            side_copy="Diese URL ist fuer Lehrpersonen vorgesehen und fuehrt direkt in den geschuetzten Admin-Bereich.",
            side_items=["Phase steuern", "Abgaben pruefen", "Team-Training ausloesen"],
            variant="admin",
            utility_context="Probevorlesung - Julian Koch",
        ),
        unsafe_allow_html=True,
    )

    with st.form("teacher_login_form", clear_on_submit=False):
        entered_secret = st.text_input(
            "Admin-Passwort",
            type="password",
            placeholder="Passwort eingeben",
        )
        login_submitted = st.form_submit_button("Admin-Panel oeffnen", type="primary", width="stretch")

    if login_submitted:
        if not entered_secret.strip():
            render_message_panel("Passwort fehlt", "Bitte geben Sie das Admin-Passwort ein.", tone="warning")
        elif hmac.compare_digest(entered_secret.strip(), ADMIN_SECRET):
            st.query_params.clear()
            st.query_params["admin"] = entered_secret.strip()
            st.rerun()
        else:
            render_message_panel("Login fehlgeschlagen", "Das Admin-Passwort ist ungueltig.", tone="danger")

    if st.button("Zur Team-Startseite", width="stretch"):
        st.query_params.clear()
        st.rerun()
    st.stop()

# Falls diese Browser-Session bereits im Admin-Modus war, nicht versehentlich
# in die Team-/Registrierungsansicht springen lassen.
if st.session_state.get("admin_mode", False) and not is_admin:
    render_message_panel(
        "Admin-Modus aktiv",
        "Diese Sitzung ist als Dozentenansicht markiert. Oeffnen Sie das Admin-Panel oder verlassen Sie den Admin-Modus.",
        tone="warning",
    )
    if st.button("Zum Admin-Panel", type="primary", width="stretch"):
        st.query_params["admin"] = ADMIN_SECRET
        st.rerun()
    if st.button("Admin-Modus verlassen", width="stretch"):
        st.session_state["admin_mode"] = False
        st.query_params.clear()
        st.rerun()
    st.stop()


# ============================================================
# VIEW: Admin-Panel
# ============================================================

if is_admin:
    st.markdown(
        render_page_header(
            "Challenge Control Panel",
            "Dozentenansicht fuer Start, Monitoring und Auswertung der Classroom-Challenge.",
            eyebrow="Admin",
            tagline="Zukunft gemeinsam gestalten",
            side_label="Lehransicht",
            side_title="Projektorbereit",
            side_copy="Die Admin-Ansicht ist fuer Moderation, Statuskontrolle und die gemeinsame Ergebnisbesprechung ausgelegt.",
            side_items=["QR-Code teilen", "Phase freigeben", "Abgaben pruefen", "Ergebnisse praesentieren"],
            variant="admin",
            utility_context="Probevorlesung - Julian Koch",
        ),
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # Top row: QR code  |  Status + Reset
    # ------------------------------------------------------------------
    col_qr, col_status = st.columns([1, 2])

    with col_qr:
        qr_url = get_app_url_for_qr()
        st.markdown(
            render_panel(
                "App-Zugang",
                (
                    '<p class="ui-panel-copy">QR-Code oder URL mit der Gruppe teilen.</p>'
                    f'<p class="ui-panel-copy"><code>{escape(qr_url)}</code></p>'
                ),
                tone="accent",
            ),
            unsafe_allow_html=True,
        )
        if HAS_QRCODE:
            qr_bytes = generate_qr_code(qr_url)
            if qr_bytes:
                st.image(qr_bytes, width=300)
        else:
            render_message_panel("QR-Code nicht verfuegbar", "Die URL kann direkt im Browser geteilt werden.", tone="warning")

    with col_status:
        _all_teams_top = challenge_state.get_all_teams()
        _n_submitted = sum(1 for t in _all_teams_top.values() if t.get("submitted"))
        _n_trained = sum(1 for tid in _all_teams_top if challenge_state.get_team_result(tid) is not None)
        st.markdown(
            render_metric_grid([
                {"label": "Teams registriert", "value": len(_all_teams_top)},
                {"label": "Features abgegeben", "value": _n_submitted},
                {"label": "Modelle trainiert", "value": _n_trained},
            ]),
            unsafe_allow_html=True,
        )
        if st.button("🔄 Challenge zurücksetzen (Neue Runde)", key="admin_reset"):
            if st.session_state.get("confirm_reset", False):
                challenge_state.reset()
                st.session_state["confirm_reset"] = False
                st.rerun()
            else:
                st.session_state["confirm_reset"] = True
                render_message_panel(
                    "Bestaetigung erforderlich",
                    "Bitte erneut klicken, um alle Daten zu loeschen und eine neue Runde zu starten.",
                    tone="warning",
                )

    if HAS_AUTOREFRESH:
        st_autorefresh(interval=4000, key="admin_refresh")

    # ------------------------------------------------------------------
    # Team-Übersicht — always visible
    # ------------------------------------------------------------------
    st.markdown(
        render_section_heading("👥 Team-Übersicht", "Aktueller Stand aller registrierten Teams."),
        unsafe_allow_html=True,
    )
    all_teams = challenge_state.get_all_teams()
    if not all_teams:
        render_message_panel("Warten auf Teams", "Sobald Teams registriert sind, erscheinen sie hier automatisch.", tone="muted")
    else:
        _phase_label = {
            "feature_selection": "🔬 Phase 1: Feature-Auswahl",
            "training": "⚙️ Phase 2: Training",
            "results": "🏆 Phase 3: Ergebnisse",
        }
        header_cols = st.columns([2, 2, 3, 2, 1])
        header_cols[0].markdown("**Team**")
        header_cols[1].markdown("**Phase**")
        header_cols[2].markdown("**Features**")
        header_cols[3].markdown("**F1-Score**")
        header_cols[4].markdown("**Aktion**")
        st.divider()
        for tid, team in sorted(all_teams.items(), key=lambda kv: kv[1]["name"].lower()):
            result = challenge_state.get_team_result(tid)
            if not team.get("submitted"):
                team_phase = "feature_selection"
            elif result is None:
                team_phase = "training"
            else:
                team_phase = "results"
            features = team.get("selected_features") or []
            f1_display = format_percent(result["f1_macro"]) if result else "—"
            row_cols = st.columns([2, 2, 3, 2, 1])
            row_cols[0].markdown(f'<div style="padding:0.4rem 0;font-weight:600;">{escape(team["name"])}</div>', unsafe_allow_html=True)
            row_cols[1].markdown(f'<div style="padding:0.4rem 0;font-size:0.88rem;">{_phase_label.get(team_phase, team_phase)}</div>', unsafe_allow_html=True)
            if features:
                row_cols[2].markdown(render_tag_list(features, variant="accent"), unsafe_allow_html=True)
            else:
                row_cols[2].markdown('<div style="padding:0.4rem 0;color:#888;font-size:0.88rem;">noch keine Auswahl</div>', unsafe_allow_html=True)
            row_cols[3].markdown(f'<div style="padding:0.4rem 0;font-weight:700;">{f1_display}</div>', unsafe_allow_html=True)
            if row_cols[4].button("🗑️", key=f"del_team_{tid}", help=f"Team '{team['name']}' löschen"):
                challenge_state.delete_team(tid)
                st.rerun()

    # ------------------------------------------------------------------
    # Training — visible when teams have submitted features
    # ------------------------------------------------------------------
    submitted_teams = [
        (tid, t) for tid, t in (all_teams or {}).items()
        if t.get("submitted") and t.get("selected_features")
    ]
    if submitted_teams:
        st.markdown(
            render_section_heading(
                "⚙️ Training",
                "Modelle pro Team trainieren. Alle oder einzeln.",
            ),
            unsafe_allow_html=True,
        )
        trained_count = sum(1 for tid, _ in submitted_teams if challenge_state.get_team_result(tid) is not None)
        open_count = len(submitted_teams) - trained_count
        st.markdown(
            render_metric_grid([
                {"label": "Bereit zum Trainieren", "value": len(submitted_teams)},
                {"label": "Bereits trainiert", "value": trained_count},
                {"label": "Offen", "value": open_count},
            ]),
            unsafe_allow_html=True,
        )
        if open_count > 0:
            if st.button("Alle offenen Teams trainieren", type="primary", width="stretch", key="train_all_open"):
                open_team_ids = [tid for tid, _ in submitted_teams if challenge_state.get_team_result(tid) is None]
                progress_bar = st.progress(0)
                status_text = st.empty()
                with st.spinner("Teammodelle werden trainiert..."):
                    for idx, tid in enumerate(open_team_ids, start=1):
                        status_text.text(f"Trainiere {all_teams[tid]['name']} ({idx}/{len(open_team_ids)})...")
                        challenge_state.run_team_training(tid, X_train, y_train, X_test, y_test)
                        progress_bar.progress(idx / len(open_team_ids))
                    challenge_state.train_optimal_model(X_train, y_train, X_test, y_test)
                render_message_panel("Training abgeschlossen", f"{len(open_team_ids)} Team(s) trainiert.", tone="success")
                st.rerun()
        else:
            if st.button("Referenzmodell neu trainieren", width="stretch", key="train_optimal"):
                with st.spinner("Trainiere Referenzmodell..."):
                    challenge_state.train_optimal_model(X_train, y_train, X_test, y_test)
                st.rerun()

        with st.expander("Einzelne Teams trainieren", expanded=False):
            for tid, team in submitted_teams:
                result = challenge_state.get_team_result(tid)
                features = team.get("selected_features") or []
                result_text = (
                    f'<p class="ui-panel-copy">F1: {format_percent(result["f1_macro"])}, Accuracy: {format_percent(result["accuracy"])}</p>'
                    if result else '<p class="ui-panel-copy">Noch nicht trainiert.</p>'
                )
                body = (
                    f"{render_status_badge(result is not None)}"
                    f"{render_tag_list(features, variant='accent')}"
                    f"{result_text}"
                )
                st.markdown(render_panel(f"Team: {team['name']}", body), unsafe_allow_html=True)
                if st.button(
                    "Erneut trainieren" if result else "Trainieren",
                    width="stretch",
                    key=f"train_team_{tid}",
                ):
                    with st.spinner(f"Trainiere {team['name']}..."):
                        challenge_state.run_team_training(tid, X_train, y_train, X_test, y_test)
                    render_message_panel("Team trainiert", f"{team['name']} wurde erfolgreich trainiert.", tone="success")
                    st.rerun()

    # ------------------------------------------------------------------
    # Leaderboard — visible when results exist
    # ------------------------------------------------------------------
    leaderboard = challenge_state.get_leaderboard()
    if leaderboard:
        best_entry = leaderboard[0]
        st.markdown(
            render_section_heading("🏆 Leaderboard", "Projektorfreundliche Ergebnisansicht fuer den Klassenraum."),
            unsafe_allow_html=True,
        )
        st.markdown(
            render_metric_grid([
                {"label": "Bestes Team", "value": best_entry["team_name"]},
                {"label": "Bester F1-Score", "value": format_percent(best_entry["f1_macro"])},
                {"label": "Teams mit Ergebnis", "value": len(leaderboard)},
            ]),
            unsafe_allow_html=True,
        )
        st.markdown(render_leaderboard(leaderboard, include_time=True, include_features=True), unsafe_allow_html=True)

        # Cross-team Feature Importance
        with st.expander("📊 Feature-Analyse & Team-Auswertung", expanded=False):
            st.markdown(render_section_heading("📈 Feature-Haeufigkeit"), unsafe_allow_html=True)
            feature_counts = {f: 0 for f in FEATURE_NAMES}
            for t_item in (all_teams or {}).values():
                for feat in (t_item.get("selected_features") or []):
                    if feat in feature_counts:
                        feature_counts[feat] += 1

            sorted_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)
            fig_freq = go.Figure(go.Bar(
                x=[count for _, count in sorted_features],
                y=[name for name, _ in sorted_features],
                orientation="h",
                marker_color=HSB_PRIMARY,
                text=[f"{count}×" for _, count in sorted_features],
                textposition="auto",
            ))
            fig_freq.update_layout(**get_plotly_layout(
                xaxis_title="Anzahl Teams",
                height=450,
                margin=dict(l=200, r=20, t=30, b=40),
            ))
            st.plotly_chart(fig_freq, width="stretch")

            # Aggregate feature importances across all teams
            st.markdown(render_section_heading("🌟 Mittlere Feature-Wichtigkeit über alle Teams"), unsafe_allow_html=True)
            importance_by_feature: dict[str, list[float]] = {f: [] for f in FEATURE_NAMES}
            for tid_lb in (all_teams or {}):
                res = challenge_state.get_team_result(tid_lb)
                if res and res.get("feature_importances") is not None and res.get("feature_names"):
                    for fname, fimp in zip(res["feature_names"], res["feature_importances"]):
                        if fname in importance_by_feature:
                            importance_by_feature[fname].append(float(fimp))
            mean_importances = {f: (sum(vals) / len(vals)) for f, vals in importance_by_feature.items() if vals}
            if mean_importances:
                sorted_imp = sorted(mean_importances.items(), key=lambda x: x[1], reverse=True)
                fig_imp = go.Figure(go.Bar(
                    x=[v for _, v in sorted_imp],
                    y=[k for k, _ in sorted_imp],
                    orientation="h",
                    marker_color=HSB_PRIMARY_LIGHT,
                    text=[f"{v*100:.1f}%" for _, v in sorted_imp],
                    textposition="auto",
                ))
                fig_imp.update_layout(**get_plotly_layout(
                    title="Durschnittliche Feature-Wichtigkeit (über alle trainierten Teams)",
                    xaxis_title="Mittlere Wichtigkeit",
                    height=450,
                    margin=dict(l=200, r=20, t=50, b=40),
                ))
                st.plotly_chart(fig_imp, width="stretch")
                top_feature = sorted_imp[0][0]
                st.markdown(
                    render_panel(
                        "Diskussionspunkt",
                        f'<p class="ui-panel-copy">Das im Durchschnitt wichtigste Merkmal über alle Teams ist '
                        f"<strong>{escape(top_feature)}</strong>. "
                        "Hatten die Studierenden dieses Feature auch in ihren Boxplot-Analysen als trennscharf identifiziert?</p>",
                        tone="accent",
                    ),
                    unsafe_allow_html=True,
                )
            else:
                render_message_panel("Keine Importances verfuegbar", "Bitte zuerst mindestens ein Team trainieren.", tone="muted")

            st.markdown(render_section_heading("🎯 Optimales Feature-Set", "Referenzmodell mit allen 11 Features."), unsafe_allow_html=True)
            optimal = challenge_state.get_optimal_result()
            if optimal:
                st.markdown(
                    render_metric_grid([
                        {"label": "F1-Score", "value": format_percent(optimal["f1_macro"])},
                        {"label": "Accuracy", "value": format_percent(optimal["accuracy"])},
                        {"label": "Trainingszeit", "value": f"{optimal['train_time']:.2f} s"},
                    ]),
                    unsafe_allow_html=True,
                )
                fig_opt = plot_feature_importances(
                    np.array(optimal["feature_importances"]),
                    optimal["feature_names"],
                    "Feature Importances (optimales Modell)",
                )
                st.plotly_chart(fig_opt, width="stretch")
            else:
                render_message_panel("Referenzmodell ausstehend", "Das optimale Modell wurde noch nicht trainiert.", tone="muted")

        with st.expander("💡 Zusammenfassung & Takeaways", expanded=False):
            st.markdown(
                render_section_heading("💡 Was haben wir gelernt?", "Kernerkenntnisse aus dieser Challenge-Runde."),
                unsafe_allow_html=True,
            )
            teams_admin = challenge_state.get_all_teams()
            feature_counts_admin = {f: 0 for f in FEATURE_NAMES}
            for t_item in teams_admin.values():
                for feat in (t_item.get("selected_features") or []):
                    if feat in feature_counts_admin:
                        feature_counts_admin[feat] += 1
            most_popular = max(feature_counts_admin, key=feature_counts_admin.get) if any(feature_counts_admin.values()) else "-"
            least_popular = (
                min((f for f, c in feature_counts_admin.items() if c > 0), key=feature_counts_admin.get, default="-")
                if any(c > 0 for c in feature_counts_admin.values()) else "-"
            )
            optimal_admin = challenge_state.get_optimal_result()
            takeaway_items = [
                f"Beliebtestes Feature: <strong>{escape(most_popular)}</strong> ({feature_counts_admin.get(most_popular, 0)}× gewaehlt).",
                f"Am seltensten gewaehlt: <strong>{escape(least_popular)}</strong> ({feature_counts_admin.get(least_popular, 0)}×).",
            ]
            if leaderboard:
                takeaway_items.append(
                    f"Bestes Team: <strong>{escape(leaderboard[0]['team_name'])}</strong> mit F1 = {leaderboard[0]['f1_macro']*100:.2f}%."
                )
            if optimal_admin:
                takeaway_items.append(
                    f"Referenzmodell (alle 11 Features): F1 = {optimal_admin['f1_macro']*100:.2f}%. "
                    "Dies zeigt, wie viel Leistung mit einer guten Teilmenge erreichbar ist."
                )
            takeaway_items.extend([
                "Feature-Auswahl ist entscheidend: Wenige, aber gut trennende Features koennen fast so gut sein wie alle zusammen.",
                "Die Konfusionsmatrix zeigt, <em>welche</em> Klassen problematisch sind &ndash; nicht nur <em>ob</em> Fehler auftreten.",
            ])
            takeaway_html = "".join(f"<li>{item}</li>" for item in takeaway_items)
            st.markdown(
                render_panel(
                    "",
                    f'<ul class="ui-panel-copy" style="padding-left:1.1rem;margin:0;">{takeaway_html}</ul>',
                    tone="accent",
                ),
                unsafe_allow_html=True,
            )

    st.stop()


# ============================================================
# VIEW: Team-Ansicht (mit Query-Parameter ?team=<id>)
# ============================================================

if team_id:
    team = challenge_state.get_team(team_id)

    if team is None:
        render_message_panel("Team nicht gefunden", "Diese Team-ID ist nicht mehr gueltig. Bitte registrieren Sie sich erneut.", tone="danger")
        if st.button("Zur Registrierung"):
            st.query_params.clear()
            st.rerun()
        st.stop()

    # Teamgesteuerter Ablauf: Der Team-Fortschritt wird nicht mehr global freigeschaltet,
    # sondern aus dem individuellen Teamstatus abgeleitet.
    team_result = challenge_state.get_team_result(team_id)
    if not team.get("submitted"):
        current_phase = "feature_selection"
    elif team_result is None:
        current_phase = "training"
    else:
        current_phase = "results"
    _PHASE_DISPLAY = {
        "feature_selection": "🔬 Phase 1: Feature-Auswahl",
        "training":          "⚙️ Phase 2: Training",
        "results":           "🏆 Phase 3: Ergebnisse",
    }
    _PHASE_HINTS = {
        "feature_selection": "Erkunde die Daten und wähle 4 Features",
        "training":          "Starte das Training deines Modells",
        "results":           "Sieh dir deine Ergebnisse an",
    }
    phase_display = _PHASE_DISPLAY.get(current_phase, current_phase)
    phase_hint = _PHASE_HINTS.get(current_phase, "")
    st.markdown(
        render_page_header(
            "Hörsaalübung\nMustererkennung",
            f"Team {team['name']} ist für die Classroom-Challenge angemeldet.",
            eyebrow="Teamansicht",
            side_label="Ihr Team",
            side_title=team["name"],
            side_copy="Diese Ansicht führt das Team Schritt für Schritt durch die Challenge.",
            side_items=[
                phase_display,
                phase_hint,
            ],
            variant="team",
            utility_context="Probevorlesung - Julian Koch",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        render_metric_grid(
            [
                {"label": "Team", "value": team["name"]},
                {"label": "Aktuelle Phase", "value": phase_display},
            ]
        ),
        unsafe_allow_html=True,
    )

    should_team_autorefresh = False
    if should_team_autorefresh and HAS_AUTOREFRESH:
        st_autorefresh(interval=3000, key="team_refresh")

    if current_phase == "feature_selection":
        st.markdown(
            render_panel(
                "🎯 Lernziel",
                (
                    '<p class="ui-panel-copy">'
                    "Verstehen, warum die <strong>Feature-Auswahl</strong> die Modellqualität bestimmt. "
                    "Untersuchen Sie die Verteilungen der Features &ndash; ein gutes Feature zeigt "
                    "<strong>klar unterschiedliche Werte je Fehlerklasse</strong>."
                    "</p>"
                    '<p class="ui-panel-copy" style="margin-top:0.6rem;">'
                    "<strong>Tipp:</strong> Schauen Sie sich an, bei welchem Feature welcher Fehler "
                    "erkennbar ist &ndash; und versuchen Sie, mit Ihren vier Features möglichst "
                    "<em>alle</em> Fehlerklassen abzudecken. Wählen Sie nicht vier Features, die alle "
                    "nur denselben Fehler erkennen. Jedes Feature sollte idealerweise eine andere "
                    "Klasse klar vom Rest trennen."
                    "</p>"
                ),
                tone="accent",
            ),
            unsafe_allow_html=True,
        )

        if team["submitted"]:
            submitted_body = (
                '<div class="state-card">'
                '<div class="state-card-title">Auswahl eingereicht</div>'
                '<div class="state-card-copy">Die Merkmalsauswahl wurde gespeichert. Die Ansicht aktualisiert sich automatisch, sobald die naechste Phase beginnt.</div>'
                "</div>"
                f"{render_tag_list(team['selected_features'], variant='accent')}"
            )
            st.markdown(render_panel("Gespeicherte Features", submitted_body, tone="success"), unsafe_allow_html=True)
        else:
            st.markdown(
                render_section_heading(
                    "🎯 Feature-Auswahl",
                    "Waehlen Sie genau vier Merkmale fuer das Teammodell aus.",
                ),
                unsafe_allow_html=True,
            )
            st.markdown(
                render_panel(
                    "Hinweis",
                    '<p class="ui-panel-copy">Die Auswahl kann erst abgesendet werden, wenn genau vier Features markiert sind.</p>',
                    tone="muted",
                ),
                unsafe_allow_html=True,
            )

            # ----------------------------------------------------------
            # Schritt 1: Daten erkunden (vor der Auswahl)
            # ----------------------------------------------------------
            with st.expander("Schritt 1: Daten und Features erkunden", expanded=True):
                X_source = X_all
                y_source = y_all

                st.markdown(
                    render_metric_grid(
                        [
                            {"label": "Datensatz", "value": "Gesamt (Train + Test)"},
                            {"label": "Segmente", "value": len(X_source)},
                            {"label": "Features gesamt", "value": len(FEATURE_NAMES)},
                        ]
                    ),
                    unsafe_allow_html=True,
                )

                st.markdown(
                    render_section_heading(
                        "📡 Rohdaten anschauen",
                        "Signal und FFT eines gewaehlten Segments aus dem Gesamtdatensatz.",
                    ),
                    unsafe_allow_html=True,
                )
                st.markdown(
                    render_panel(
                        "Was zeigen diese Signale?",
                        (
                            '<p class="ui-panel-copy">'
                            "Der Datensatz stammt aus dem <strong>CWRU Bearing Dataset</strong> "
                            "(Case Western Reserve University). Ein Beschleunigungssensor am "
                            "<strong>Antriebsende des Motors</strong> misst Vibrationen mit "
                            "<strong>12 000 Abtastwerten pro Sekunde</strong>.<br><br>"
                            "<strong>Normal</strong> – intaktes Lager: das Signal ist gleichmäßiges Rauschen ohne markante Muster.<br>"
                            "<strong>Innenring (IR)</strong> – Schaden auf dem inneren Laufring: periodische Impulse "
                            "treten auf, wenn der Wälzkörper über den Fehler rollt.<br>"
                            "<strong>Außenring (OR)</strong> – Schaden auf dem äußeren Laufring: ähnliche Impulse, "
                            "aber mit anderer Wiederholrate, die von der Lagergeometrie abhängt.<br>"
                            "<strong>Kugel (B)</strong> – Schaden am Wälzkörper selbst: unregelmäßigere Impulsmuster, "
                            "da jede Kugel abwechselnd den inneren und äußeren Laufring berührt.<br><br>"
                            "<em>Tipp:</em> Vergleichen Sie Normal mit einer Fehlerklasse – "
                            "achten Sie auf Ausreißer im Zeitsignal und auf Frequenzspitzen in der FFT."
                            "</p>"
                        ),
                        tone="accent",
                    ),
                    unsafe_allow_html=True,
                )
                st.caption(
                    "💡 Ein **Segment** ist ein kurzer Ausschnitt (1 024 Messpunkte ≈ 85 ms) "
                    "aus der langen Vibrationsmessung. Pro Fehlerklasse gibt es viele solcher "
                    "Ausschnitte — mit dem Slider können Sie durch verschiedene Segmente blättern."
                )
                _filter_col1, _filter_col2 = st.columns(2)
                with _filter_col1:
                    selected_class = st.selectbox(
                        "Fehlerklasse:",
                        CLASS_NAMES,
                        key=f"explore_class_{team_id}",
                    )
                class_idx = CLASS_NAMES.index(selected_class)
                class_segments = X_source[y_source == class_idx]
                with _filter_col2:
                    segment_idx = st.slider(
                        "Segment-Nr.:",
                        0,
                        len(class_segments) - 1,
                        0,
                        key=f"explore_seg_{team_id}",
                    )
                signal = class_segments[segment_idx]
                color = get_class_color(selected_class)
                fig_explore = plot_signal_and_fft(
                    signal,
                    f"{selected_class} (Gesamt)",
                    color,
                )
                st.plotly_chart(fig_explore, width="stretch")

                with st.expander("Featurewerte fuer dieses Segment", expanded=False):
                    segment_features = extract_all_features(signal.reshape(1, -1)).iloc[0]
                    segment_table = [
                        {"Feature": feat, "Wert": float(segment_features[feat])}
                        for feat in FEATURE_NAMES
                    ]
                    st.dataframe(segment_table, width="stretch", hide_index=True)

                st.markdown(
                    render_section_heading(
                        "📊 Alle Features vergleichen",
                        "Verteilung eines Features ueber alle Klassen im Gesamtdatensatz.",
                    ),
                    unsafe_allow_html=True,
                )
                feature_df = get_feature_overview()
                feature_to_compare = st.selectbox(
                    "Feature fuer Klassenvergleich:",
                    FEATURE_NAMES,
                    key=f"feature_compare_{team_id}",
                )

                fig_feature = go.Figure()
                for class_name in CLASS_NAMES:
                    class_values = feature_df.loc[
                        feature_df["class_name"] == class_name,
                        feature_to_compare,
                    ]
                    fig_feature.add_trace(
                        go.Box(
                            y=class_values,
                            name=class_name,
                            boxmean=True,
                            marker_color=CHART_COLORS.get(class_name, HSB_PRIMARY),
                            line_color=CHART_COLORS.get(class_name, HSB_PRIMARY),
                        )
                    )
                fig_feature.update_layout(
                    **get_plotly_layout(
                        title=f"{feature_to_compare} nach Klasse",
                        yaxis_title=feature_to_compare,
                        height=430,
                        showlegend=True,
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="center",
                            x=0.5,
                            font=dict(size=13),
                        ),
                    )
                )
                st.plotly_chart(fig_feature, width="stretch")

                st.markdown(
                    render_section_heading(
                        "🔬 Notebook-Ansicht: Alle Features",
                        "Verteilungen aller 11 Features nach Klassen als Grundlage für die Auswahl.",
                    ),
                    unsafe_allow_html=True,
                )
                _mpl_colors = {cn: CHART_COLORS.get(cn, HSB_PRIMARY) for cn in CLASS_NAMES}
                _n_feat = len(FEATURE_NAMES)
                fig_mpl, axes = plt.subplots(
                    _n_feat, 1,
                    figsize=(6, 2.4 * _n_feat),
                )
                for feat_idx, feature_name in enumerate(FEATURE_NAMES):
                    ax = axes[feat_idx]
                    for class_name in CLASS_NAMES:
                        vals = feature_df.loc[
                            feature_df["class_name"] == class_name,
                            feature_name,
                        ].values
                        ax.hist(vals, bins=30, histtype="step", linewidth=1.8,
                                label=class_name, color=_mpl_colors[class_name])
                    ax.set_title(feature_name, fontsize=11, fontweight="bold",
                                 pad=6)
                    ax.tick_params(labelsize=9)
                handles, labels = axes[0].get_legend_handles_labels()
                fig_mpl.legend(handles, labels, loc="upper center",
                               ncol=len(CLASS_NAMES), fontsize=10,
                               frameon=True, bbox_to_anchor=(0.5, 1.0),
                               edgecolor="#D8E0E8", fancybox=True)
                fig_mpl.tight_layout(rect=[0, 0, 1, 0.98])
                st.pyplot(fig_mpl)
                plt.close(fig_mpl)

                st.markdown(
                    render_section_heading(
                        "🗺️ Notebook-Ansicht: 2D-Feature-Projektion",
                        "PCA-Projektion aller 11 Features zur Klassen-Trennung.",
                    ),
                    unsafe_allow_html=True,
                )
                pca_df, explained = get_feature_projection()
                fig_pca = go.Figure()
                for class_name in CLASS_NAMES:
                    class_points = pca_df[pca_df["class_name"] == class_name]
                    fig_pca.add_trace(
                        go.Scatter(
                            x=class_points["pc1"],
                            y=class_points["pc2"],
                            mode="markers",
                            name=class_name,
                            marker=dict(size=7, opacity=0.65),
                        )
                    )
                fig_pca.update_layout(
                    **get_plotly_layout(
                        title=f"PCA (Gesamt) - Varianz: PC1 {explained[0]*100:.1f}%, PC2 {explained[1]*100:.1f}%",
                        xaxis_title="PC1",
                        yaxis_title="PC2",
                        height=460,
                    )
                )
                st.plotly_chart(fig_pca, width="stretch")

            # ----------------------------------------------------------
            # Schritt 2: Features auswaehlen
            # ----------------------------------------------------------
            st.markdown(
                render_section_heading(
                    "✅ Schritt 2: Features auswaehlen",
                    "Waehlen Sie auf Basis Ihrer Analyse genau vier Merkmale aus.",
                ),
                unsafe_allow_html=True,
            )

            selection_key = f"selected_features_{team_id}"
            if selection_key not in st.session_state:
                st.session_state[selection_key] = []
            elif isinstance(st.session_state[selection_key], set):
                # Rueckwaertskompatibel: alte Session-Daten von set -> list.
                st.session_state[selection_key] = sorted(st.session_state[selection_key])

            persisted_selected = set(st.session_state[selection_key])
            for feat_name in FEATURE_NAMES:
                feat_key = f"feat_{team_id}_{feat_name}"
                if feat_key not in st.session_state:
                    st.session_state[feat_key] = feat_name in persisted_selected

            selected = [
                feat_name for feat_name in FEATURE_NAMES
                if st.session_state.get(f"feat_{team_id}_{feat_name}", False)
            ]
            selected_set = set(selected)
            selected_count = len(selected)
            st.session_state[selection_key] = selected
            st.markdown(
                render_metric_grid(
                    [
                        {"label": "Ausgewaehlt", "value": selected_count},
                        {"label": "Noch offen", "value": max(0, 4 - selected_count)},
                        {"label": "Verfuegbar", "value": len(FEATURE_NAMES)},
                    ]
                ),
                unsafe_allow_html=True,
            )
            if selected:
                st.markdown(render_tag_list(selected, variant="accent"), unsafe_allow_html=True)
            st.progress(min(1.0, selected_count / 4))

            cols_per_row = 2
            feature_list = FEATURE_NAMES
            for i in range(0, len(feature_list), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx >= len(feature_list):
                        break
                    
                    feat_name = feature_list[idx]
                    feat_info = FEATURE_INFO[feat_name]
                    redundancy_hint = ""
                    with col:
                        is_selected = feat_name in selected_set
                        selected_indicator = (
                            '<div class="feature-card-selected-indicator">✅ Ausgewählt</div>'
                            if is_selected
                            else '<div class="feature-card-cta">☑ Zum Auswählen anklicken</div>'
                        )
                        with st.container(border=True):
                            st.markdown(
                                (
                                    f'<div class="feature-card-shell{" feature-card-shell--active" if is_selected else ""}">'
                                    '<div class="feature-card-heading">'
                                    f'<div class="feature-card-domain">{escape(feat_info["domain"])}</div>'
                                    f'<div class="feature-card-title">{escape(feat_name)}</div>'
                                    f'<div class="feature-card-copy">{escape(feat_info["description"])}</div>'
                                    f'{redundancy_hint}'
                                    f'{selected_indicator}'
                                    "</div>"
                                    "</div>"
                                ),
                                unsafe_allow_html=True,
                            )
                            checked = st.checkbox(
                                "Feature für mein Modell wählen",
                                key=f"feat_{team_id}_{feat_name}",
                                disabled=(selected_count >= 4 and not is_selected),
                            )
                            with st.expander("Details", expanded=False):
                                st.markdown(f"**{feat_info['name_de']}**")
                                st.caption(feat_info["domain"])
                                st.latex(feat_info["formula"])
                                st.caption(feat_info["intuition"])
                                st.caption(f"Geeignet fuer: {feat_info['useful_for']}")
                        # checked wird absichtlich nicht inkrementell verarbeitet.
                        # Die Auswahl wird robust aus st.session_state rekonstruiert.
                        _ = checked

            selected = [
                feat_name for feat_name in FEATURE_NAMES
                if st.session_state.get(f"feat_{team_id}_{feat_name}", False)
            ]
            st.session_state[selection_key] = selected

            if len(selected) == 4:
                if st.button("Auswahl abschicken", type="primary", width="stretch"):
                    try:
                        chosen_features = list(selected)
                        challenge_state.submit_features(team_id, chosen_features)
                        st.session_state.pop(selection_key, None)
                        for feat_name in FEATURE_NAMES:
                            st.session_state.pop(f"feat_{team_id}_{feat_name}", None)
                        render_message_panel("Auswahl gespeichert", "Die vier Features wurden erfolgreich uebermittelt.", tone="success")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        render_message_panel("Fehler bei der Abgabe", str(e), tone="danger")
            else:
                render_message_panel(
                    "Auswahl unvollstaendig",
                    f"Bitte waehlen Sie genau vier Features aus. Aktuell sind {len(selected)} markiert.",
                    tone="warning",
                )

    elif current_phase == "training":
        training_body = (
            '<div class="state-card">'
            '<div class="state-card-title">Bereit fuer Training</div>'
            '<div class="state-card-copy">Sobald Sie trainieren, werden Ihre Ergebnisse berechnet und direkt angezeigt.</div>'
            "</div>"
        )
        st.markdown(render_panel("Status", training_body, tone="accent"), unsafe_allow_html=True)
        st.markdown(
            render_panel(
                "Modell-Info",
                (
                    '<p class="ui-panel-copy">'
                    "Ihr Team-Modell ist ein Random-Forest-Klassifikator. Es nutzt genau die vier von Ihnen gewaehlten Features."
                    "</p>"
                    '<p class="ui-panel-copy" style="margin-top:0.55rem;">'
                    "Trainingsdaten und Testdaten sind fest vorgegeben, damit alle Teams unter denselben Bedingungen verglichen werden."
                    "</p>"
                    '<p class="ui-panel-copy" style="margin-top:0.55rem;">'
                    "Ausgegeben werden F1-Score, Accuracy, Konfusionsmatrix und Feature-Importances."
                    "</p>"
                ),
                tone="muted",
            ),
            unsafe_allow_html=True,
        )
        with st.expander("Was passiert mit den Daten?", expanded=True):
            st.markdown(
                render_panel(
                    "",
                    (
                        '<ol class="ui-panel-copy" style="margin:0; padding-left:1.1rem;">'
                        '<li>Aus den Rohsignalen werden die ausgewaehlten Features berechnet.</li>'
                        '<li>Das Modell wird auf dem Trainingsdatensatz trainiert (gleiche Einstellungen fuer alle Teams).</li>'
                        '<li>Danach erfolgt die Bewertung auf getrennten Testdaten.</li>'
                        '<li>Die Ergebnisse werden teamweise gespeichert und im Leaderboard angezeigt.</li>'
                        '</ol>'
                    ),
                    tone="muted",
                ),
                unsafe_allow_html=True,
            )

        teams_all = challenge_state.get_all_teams()
        submitted_teams = [
            tid for tid, team_item in teams_all.items()
            if team_item.get("submitted") and team_item.get("selected_features")
        ]
        trained_teams = [
            tid for tid in submitted_teams
            if challenge_state.get_team_result(tid) is not None
        ]
        st.markdown(
            render_metric_grid(
                [
                    {"label": "Abgegeben (gesamt)", "value": len(submitted_teams)},
                    {"label": "Schon trainiert", "value": len(trained_teams)},
                    {"label": "Ihr Status", "value": "Ausstehend"},
                ]
            ),
            unsafe_allow_html=True,
        )

        if st.button("Eigenes Modell jetzt trainieren", type="primary", width="stretch", key=f"team_train_{team_id}"):
            with st.spinner("Ihr Modell wird trainiert..."):
                challenge_state.run_team_training(team_id, X_train, y_train, X_test, y_test)
            render_message_panel("Training abgeschlossen", "Ihr Team-Ergebnis ist jetzt verfuegbar.", tone="success")
            time.sleep(1)
            st.rerun()

    elif current_phase == "results":
        result = challenge_state.get_team_result(team_id)
        if result is None:
            render_message_panel("Noch keine Ergebnisse", "Das Training ist noch nicht abgeschlossen.", tone="warning")
        else:
            leaderboard = challenge_state.get_leaderboard()
            my_rank = next((e["rank"] for e in leaderboard if e["team_id"] == team_id), None)
            optimal = challenge_state.get_optimal_result()

            st.markdown(
                render_panel(
                    "Training abgeschlossen",
                    '<p class="ui-panel-copy">Ihr Modell wurde erfolgreich ausgewertet. Unten sehen Sie die wichtigsten Kennzahlen und das globale Leaderboard.</p>',
                    tone="success",
                ),
                unsafe_allow_html=True,
            )

            # --- Benchmark comparison ---
            team_metrics = [
                {"label": "Ihr F1-Score", "value": format_percent(result["f1_macro"])},
                {"label": "Ihre Accuracy", "value": format_percent(result["accuracy"])},
                {"label": "Rang", "value": f"{my_rank}/{len(leaderboard)}" if my_rank else "-"},
            ]
            if optimal:
                team_metrics.append({"label": "Benchmark (alle 12)", "value": format_percent(optimal["f1_macro"])})
            st.markdown(render_metric_grid(team_metrics), unsafe_allow_html=True)

            if optimal:
                delta = result["f1_macro"] - optimal["f1_macro"]
                if delta >= -0.02:
                    bench_tone = "success"
                    bench_text = (
                        "Ihr Modell mit nur 4 Features erreicht nahezu die Leistung des Referenzmodells "
                        "mit allen 11 Features. Eine exzellente Feature-Auswahl!"
                    )
                elif delta >= -0.10:
                    bench_tone = "accent"
                    bench_text = (
                        f"Ihr Modell liegt {abs(delta)*100:.1f} Prozentpunkte unter dem Referenzmodell (alle 11 Features). "
                        "Ueberlegen Sie, ob ein anderes Feature mehr Trennschaerfe geboten haette."
                    )
                else:
                    bench_tone = "warning"
                    bench_text = (
                        f"Ihr Modell liegt {abs(delta)*100:.1f} Prozentpunkte unter dem Referenzmodell. "
                        "Moeglicherweise fehlen Ihrem Set entscheidende Features &ndash; "
                        "vergleichen Sie die Feature-Importances mit den Boxplots aus der Exploration."
                    )
                st.markdown(
                    render_panel("Vergleich mit Referenzmodell", f'<p class="ui-panel-copy">{bench_text}</p>', tone=bench_tone),
                    unsafe_allow_html=True,
                )

            # --- Model explanation: voting ---
            with st.expander("So entscheidet Ihr Modell", expanded=True):
                voting_examples = result.get("voting_examples", [])
                n_estimators = result.get("n_estimators", 100)

                if voting_examples:
                    st.markdown(
                        render_panel(
                            "So stimmen die Baeume ab",
                            (
                                '<p class="ui-panel-copy">'
                                f"Alle {n_estimators} Baeume geben unabhaengig eine Vorhersage ab. "
                                "Die Klasse mit den meisten Stimmen gewinnt (Mehrheitsentscheid). "
                                "Hier zwei Beispiele aus Ihren Testdaten:"
                                "</p>"
                            ),
                            tone="muted",
                        ),
                        unsafe_allow_html=True,
                    )
                    for example in voting_examples:
                        is_correct = example["type"] == "correct"
                        icon = "&#10004;" if is_correct else "&#10008;"
                        label = "Korrekt klassifiziert" if is_correct else "Fehlklassifiziert"
                        vote_class_names = example.get("class_names", CLASS_NAMES)
                        vote_counts = example["vote_counts"]

                        bar_colors = [
                            "#2F7D4A" if cn == example["true_class"] else
                            "#A13A38" if cn == example["predicted_class"] and not is_correct else
                            HSB_PRIMARY
                            for cn in vote_class_names
                        ]
                        fig_vote = go.Figure(go.Bar(
                            x=_CM_SHORT_NAMES,
                            y=vote_counts,
                            marker_color=bar_colors,
                            text=[f"{v}" for v in vote_counts],
                            textposition="auto",
                        ))
                        fig_vote.update_layout(
                            **get_plotly_layout(
                                title=f"{icon} {label}",
                                yaxis_title="Stimmen",
                                xaxis_title="",
                                height=300,
                                margin=dict(l=40, r=20, t=50, b=40),
                            )
                        )
                        st.plotly_chart(fig_vote, width="stretch")
                        st.markdown(
                            f'<p style="text-align:center;font-size:0.88rem;color:#495057;">'
                            f'Wahrheit: <strong>{escape(example["true_class"])}</strong> &nbsp;|&nbsp; '
                            f'Vorhersage: <strong>{escape(example["predicted_class"])}</strong>'
                            f"</p>",
                            unsafe_allow_html=True,
                        )

                if not voting_examples:
                    render_message_panel(
                        "Nicht verfuegbar",
                        "Die Modellerklaerung ist fuer dieses Ergebnis nicht verfuegbar. "
                        "Trainieren Sie das Modell erneut, um die Visualisierung zu sehen.",
                        tone="muted",
                    )

            # --- Confusion matrix with interpretive guidance ---
            with st.expander("Konfusionsmatrix", expanded=True):
                fig_cm = plot_confusion_matrix(result["confusion_matrix"])
                st.plotly_chart(fig_cm, width="stretch")

                cm_array = np.asarray(result["confusion_matrix"], dtype=float)
                row_sums = cm_array.sum(axis=1)
                row_sums[row_sums == 0] = 1.0
                misclassification_pairs = []
                for r in range(cm_array.shape[0]):
                    for c in range(cm_array.shape[1]):
                        if r != c and cm_array[r, c] / row_sums[r] > 0.10:
                            misclassification_pairs.append(
                                (CLASS_NAMES[r], CLASS_NAMES[c], cm_array[r, c] / row_sums[r] * 100)
                            )
                if misclassification_pairs:
                    hints = "".join(
                        f"<li><strong>{true_cls}</strong> wird in {pct:.0f}% der Faelle als <strong>{pred_cls}</strong> fehlklassifiziert.</li>"
                        for true_cls, pred_cls, pct in sorted(misclassification_pairs, key=lambda x: -x[2])
                    )
                    st.markdown(
                        render_panel(
                            "Interpretationshilfe",
                            (
                                '<p class="ui-panel-copy">Haeufige Verwechslungen Ihres Modells:</p>'
                                f'<ul class="ui-panel-copy" style="margin-top:0.4rem;padding-left:1.1rem;">{hints}</ul>'
                                '<p class="ui-panel-copy" style="margin-top:0.5rem;">'
                                "Klassen, die verwechselt werden, haben aehnliche Merkmalswerte in Ihren gewaehlten Features. "
                                "Ein zusaetzliches Feature, das diese Klassen trennt, wuerde die Leistung verbessern."
                                "</p>"
                            ),
                            tone="muted",
                        ),
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        render_panel(
                            "Interpretationshilfe",
                            '<p class="ui-panel-copy">Keine groesseren Verwechslungen &ndash; Ihr Feature-Set trennt die Klassen gut.</p>',
                            tone="success",
                        ),
                        unsafe_allow_html=True,
                    )

            # --- Feature importances with reflection ---
            with st.expander("Feature-Wichtigkeit & Reflexion", expanded=True):
                fig_fi = plot_feature_importances(
                    result["feature_importances"],
                    result["feature_names"],
                    f"Feature Importances — {team['name']}"
                )
                st.plotly_chart(fig_fi, width="stretch")

                importances = np.asarray(result["feature_importances"], dtype=float)
                feat_names = np.asarray(result["feature_names"])
                top_feat = feat_names[np.argmax(importances)]
                low_feat = feat_names[np.argmin(importances)]
                st.markdown(
                    render_panel(
                        "Reflexion",
                        (
                            '<p class="ui-panel-copy">'
                            f"Ihr wichtigstes Feature war <strong>{escape(str(top_feat))}</strong>, "
                            f"waehrend <strong>{escape(str(low_feat))}</strong> am wenigsten beigetragen hat."
                            "</p>"
                            '<p class="ui-panel-copy" style="margin-top:0.5rem;">'
                            "Vergleichen Sie das mit Ihrer urspruenglichen Einschaetzung: "
                            "Haetten Sie anhand der Boxplots vorhergesagt, welches Feature am wichtigsten sein wuerde?"
                            "</p>"
                        ),
                        tone="muted",
                    ),
                    unsafe_allow_html=True,
                )

            st.markdown(render_section_heading("🏆 Leaderboard", "Vergleich aller Teams in dieser Runde."), unsafe_allow_html=True)
            st.markdown(render_leaderboard(leaderboard, include_time=True, include_features=True), unsafe_allow_html=True)

            # --- Takeaways ---
            with st.expander("Was nehme ich mit?", expanded=True):
                my_features = team.get("selected_features") or []
                takeaway_lines = [
                    "Die <strong>Feature-Auswahl</strong> bestimmt massgeblich, wie gut ein ML-Modell Klassen unterscheiden kann.",
                    "Features, die in den Boxplots klar unterschiedliche Verteilungen pro Klasse zeigen, sind in der Regel die besten Kandidaten.",
                    "Wenige, gut trennende Features koennen fast dieselbe Leistung erzielen wie alle zusammen.",
                    "Die <strong>Konfusionsmatrix</strong> zeigt nicht nur <em>ob</em> Fehler auftreten, sondern <em>welche</em> Klassen verwechselt werden &ndash; das gibt Hinweise auf fehlende Merkmale.",
                    "Feature-Importances zeigen, welches Ihrer Features am meisten zur Trennung beigetragen hat &ndash; vergleichen Sie das mit Ihrer urspruenglichen Einschaetzung.",
                ]
                if optimal:
                    takeaway_lines.append(
                        f"Das Referenzmodell mit allen 11 Features erreicht F1 = {optimal['f1_macro']*100:.1f}%. "
                        "Wenige, gut gewaehlte Features koennen einen Grossteil dieser Leistung abdecken."
                    )
                takeaway_html = "".join(f"<li>{line}</li>" for line in takeaway_lines)
                st.markdown(
                    render_panel(
                        "Kernerkenntnisse",
                        f'<ul class="ui-panel-copy" style="padding-left:1.1rem;margin:0;">{takeaway_html}</ul>',
                        tone="accent",
                    ),
                    unsafe_allow_html=True,
                )

    st.stop()


# ============================================================
# VIEW: Registrierung (Default)
# ============================================================

st.markdown(
    render_page_header(
        "Hörsaalübung\nMustererkennung",
        "Interaktive Classroom-Challenge zur Klassifikation von Wälzlagerfehlern mit Machine Learning.",
        side_label="Auf einen Blick",
        side_title="Ablauf",
        side_copy="",
        side_items=[
            "Team registrieren",
            "Persoenlichen Link erhalten",
            "Vier Features waehlen",
            "Ergebnisse vergleichen",
        ],
        variant="public",
        utility_context="Probevorlesung - Julian Koch",
    ),
    unsafe_allow_html=True,
)

current_phase = challenge_state.get_phase()

form_col, info_col = st.columns([1.3, 1])

with form_col:
    with st.container(border=True):
        st.markdown(
            (
                '<div class="registration-form-title">Team registrieren</div>'
                '<div class="registration-form-copy">Geben Sie einen Teamnamen ein. Nach dem Absenden wird automatisch der persoenliche Team-Link geoeffnet.</div>'
            ),
            unsafe_allow_html=True,
        )
        with st.form("registration_form", clear_on_submit=False):
            team_name_input = st.text_input(
                "Teamname (2-30 Zeichen):",
                max_chars=30,
                placeholder="z. B. Die Stadtmusikanten",
            )
            submitted = st.form_submit_button("Team beitreten", type="primary", width="stretch")

with info_col:
    teams_count = len(challenge_state.get_all_teams())
    st.markdown(
        render_panel(
            "Aktueller Stand",
            render_metric_grid(
                [
                    {"label": "Bereits registriert", "value": teams_count},
                    {"label": "Verfuegbare Features", "value": len(FEATURE_NAMES)},
                ]
            ),
            tone="muted",
        ),
        unsafe_allow_html=True,
    )
    if is_demo:
        st.markdown(
            render_panel(
                "Demo-Modus",
                (
                    '<p class="ui-panel-copy">'
                    "Die Originaldaten basieren auf dem CWRU Bearing Dataset (Case Western Reserve University),"
                    " einem etablierten Referenzdatensatz fuer ML/DL in der Zustandsdiagnose."
                    "</p>"
                    '<p class="ui-panel-copy" style="margin-top:0.55rem;">'
                    "Erfasst wurden Schwingungsdaten eines 2-HP-Motorpruefstands mit kuenstlich eingebrachten"
                    " Lagerfehlern (Innenring, Aussenring, Kugel) in mehreren Fehlergroessen und Lastpunkten."
                    "</p>"
                    '<p class="ui-panel-copy" style="margin-top:0.55rem;">'
                    "Typische Struktur: Normalbetrieb sowie Drive-End/Fan-End-Fehler; Abtastraten 12 kHz und 48 kHz,"
                    " MATLAB-Dateien mit Vibrationssignalen und Drehzahl."
                    "</p>"
                ),
                tone="muted",
            ),
            unsafe_allow_html=True,
        )

if submitted:
    if len(team_name_input.strip()) < 2:
        render_message_panel("Teamname zu kurz", "Der Teamname muss mindestens zwei Zeichen enthalten.", tone="danger")
    else:
        try:
            cleaned_name = team_name_input.strip()
            new_team_id = challenge_state.register_team(cleaned_name)
            render_message_panel("Registrierung erfolgreich", f"Das Team {cleaned_name} wurde angelegt. Der persoenliche Link wird jetzt geoeffnet.", tone="success")
            time.sleep(1)

            st.query_params["team"] = new_team_id
            st.rerun()

        except ValueError as e:
            render_message_panel("Registrierung fehlgeschlagen", str(e), tone="danger")
