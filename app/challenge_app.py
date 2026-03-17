"""
challenge_app.py — Bearing Challenge: Interaktive Classroom-App
===============================================================

Streamlit-App für eine Echtzeit-Challenge, bei der Teams von Studierenden
gegeneinander antreten, indem sie 4 aus 12 Features auswählen und ein
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
from io import BytesIO

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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
    print("⚠ qrcode-Library nicht installiert. QR-Code wird nicht angezeigt.")

# Auto-Refresh
try:
    from streamlit_autorefresh import st_autorefresh
    HAS_AUTOREFRESH = True
except ImportError:
    HAS_AUTOREFRESH = False
    print("⚠ streamlit-autorefresh nicht installiert. Auto-Refresh deaktiviert.")

# Eigene Module
from src.data_loader import prepare_dataset, generate_demo_data, CLASS_NAMES
from src.features import FEATURE_NAMES, _compute_spectrum
from src.feature_info import FEATURE_INFO, get_time_domain_features, get_frequency_domain_features
from src import challenge_state
from app.ui_theme import (
    inject_custom_css, get_plotly_layout, get_class_color, get_rank_color,
    render_phase_badge, render_status_badge, render_rank_emoji,
    HSB_PRIMARY, COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR, CHART_COLORS
)


# ============================================================
# Konfiguration
# ============================================================

st.set_page_config(
    page_title="Bearing Challenge — HSB",
    page_icon="🏭",
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
    """Lädt den Dataset (echt oder synthetisch)."""
    data_dir = os.path.join(PROJECT_DIR, "data")
    try:
        mat_files = [f for f in os.listdir(data_dir) if f.endswith(".mat")]
        if len(mat_files) == 0:
            raise FileNotFoundError("Keine .mat-Dateien")
        data = prepare_dataset(data_dir, segment_length=1024, overlap=0.5)
        return data, False
    except (FileNotFoundError, ValueError):
        data = generate_demo_data(n_per_class=500, segment_length=1024)
        return data, True


# Daten laden
data, is_demo = load_data()
X_train = data["X_train"]
X_test = data["X_test"]
y_train = data["y_train"]
y_test = data["y_test"]


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
    """Plottet Zeitsignal und FFT nebeneinander."""
    t_ms = np.arange(len(signal)) / fs * 1000
    freqs, mag = _compute_spectrum(signal, fs)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Zeitsignal", "Frequenzspektrum (FFT)"],
    )
    
    # Zeitsignal
    fig.add_trace(go.Scatter(
        x=t_ms, y=signal, mode="lines",
        line=dict(color=color, width=1.5),
        name="Signal",
    ), row=1, col=1)
    
    # FFT
    fig.add_trace(go.Scatter(
        x=freqs, y=mag, mode="lines", fill="tozeroy",
        line=dict(color=color, width=1.5),
        fillcolor=f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2)",
        name="Spektrum",
    ), row=1, col=2)
    
    fig.update_xaxes(title_text="Zeit (ms)", row=1, col=1)
    fig.update_xaxes(title_text="Frequenz (Hz)", range=[0, 6000], row=1, col=2)
    fig.update_yaxes(title_text="Amplitude", row=1, col=1)
    fig.update_yaxes(title_text="Amplitude", row=1, col=2)
    
    fig.update_layout(**get_plotly_layout(title=title, height=350))
    return fig


def plot_confusion_matrix(cm, title="Konfusionsmatrix"):
    """Plottet die Konfusionsmatrix."""
    cm_text = [[str(val) for val in row] for row in cm]
    fig = go.Figure(data=go.Heatmap(
        z=cm, x=CLASS_NAMES, y=CLASS_NAMES,
        text=cm_text, texttemplate="%{text}",
        textfont={"size": 16},
        colorscale=[[0.0, "#F8F9FA"], [0.5, "#0077C8"], [1.0, "#003D66"]],
        showscale=True,
    ))
    fig.update_layout(
        **get_plotly_layout(
            title=title,
            xaxis_title="Vorhersage",
            yaxis_title="Wahrheit",
            height=400,
            yaxis=dict(autorange="reversed"),
        )
    )
    return fig


def plot_feature_importances(importances, feature_names, title="Feature Importances"):
    """Plottet Feature Importances als horizontales Balkendiagramm."""
    sorted_idx = np.argsort(importances)
    fig = go.Figure(go.Bar(
        x=importances[sorted_idx],
        y=np.array(feature_names)[sorted_idx],
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


# ============================================================
# Routing
# ============================================================

query_params = st.query_params
admin_key = query_params.get("admin", None)
team_id = query_params.get("team", None)

# Admin-Authentifizierung
is_admin = False
if admin_key:
    is_admin = hmac.compare_digest(admin_key, ADMIN_SECRET)
    if not is_admin:
        st.error("🚫 Ungültiges Admin-Passwort.")
        st.stop()


# ============================================================
# VIEW: Admin-Panel
# ============================================================

if is_admin:
    st.title("🏭 Bearing Challenge — Admin-Panel")
    st.markdown("---")
    
    # Phase-Badge
    current_phase = challenge_state.get_phase()
    st.markdown(render_phase_badge(current_phase), unsafe_allow_html=True)
    st.markdown("##")
    
    # QR-Code (links), Phase-Steuerung (rechts)
    col_qr, col_control = st.columns([1, 2])
    
    with col_qr:
        st.subheader("📱 QR-Code für Studierende")
        qr_url = get_app_url_for_qr()
        st.caption(f"URL: `{qr_url}`")
        
        if HAS_QRCODE:
            qr_bytes = generate_qr_code(qr_url)
            if qr_bytes:
                st.image(qr_bytes, width=300)
        else:
            st.warning("QR-Code-Bibliothek nicht installiert. URL manuell teilen.")
    
    with col_control:
        st.subheader("⚙️ Phasen-Steuerung")
        
        # Phase-Buttons
        if current_phase == "registration":
            if st.button("➡️ Feature-Auswahl freigeben", type="primary", use_container_width=True):
                challenge_state.set_phase("feature_selection")
                st.rerun()
        
        elif current_phase == "feature_selection":
            if st.button("➡️ Training starten", type="primary", use_container_width=True):
                challenge_state.set_phase("training")
                st.rerun()
        
        elif current_phase == "training":
            if st.button("➡️ Ergebnisse zeigen", type="primary", use_container_width=True):
                challenge_state.set_phase("results")
                st.rerun()
        
        elif current_phase == "results":
            if st.button("🔄 Neue Runde starten", type="primary", use_container_width=True):
                if st.session_state.get("confirm_reset", False):
                    challenge_state.reset()
                    st.session_state["confirm_reset"] = False
                    st.rerun()
                else:
                    st.session_state["confirm_reset"] = True
                    st.warning("⚠️ Klicken Sie erneut, um zu bestätigen (alle Daten werden gelöscht).")
    
    st.markdown("---")
    
    # Auto-Refresh in Registrierungs- und Feature-Auswahl-Phase
    if current_phase in ["registration", "feature_selection"] and HAS_AUTOREFRESH:
        st_autorefresh(interval=3000, key="admin_refresh")
    
    # ======== Registrierungs-Phase ========
    if current_phase == "registration":
        st.subheader("📋 Registrierte Teams")
        
        teams = challenge_state.get_all_teams()
        if teams:
            team_names = [t["name"] for t in teams.values()]
            for i, name in enumerate(team_names, start=1):
                st.markdown(f"**{i}.** {name}")
            
            st.metric("Anzahl Teams", len(teams))
        else:
            st.info("Noch keine Teams registriert. Zeigen Sie den QR-Code!")
    
    # ======== Feature-Auswahl-Phase ========
    elif current_phase == "feature_selection":
        st.subheader("📊 Team-Status")
        
        teams = challenge_state.get_all_teams()
        status = challenge_state.get_submission_status()
        
        if teams:
            # Fortschrittsbalken
            st.progress(status["percentage"] / 100)
            st.caption(f"{status['submitted']}/{status['total_teams']} Teams haben Features abgegeben ({status['percentage']:.0f}%)")
            
            # Tabelle
            rows = []
            for tid, team in teams.items():
                rows.append({
                    "Team": team["name"],
                    "Status": "✅ Abgegeben" if team["submitted"] else "⏳ Ausstehend",
                    "Features": ", ".join(team["selected_features"]) if team["selected_features"] else "—",
                })
            
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Keine Teams registriert.")
    
    # ======== Training-Phase ========
    elif current_phase == "training":
        st.subheader("🚀 Training")
        
        status = challenge_state.get_submission_status()
        if status["submitted"] == 0:
            st.warning("Keine Teams haben Features abgegeben.")
        else:
            st.info(f"{status['submitted']} Teams bereit für Training.")
            
            if st.button("🚀 Alle Modelle trainieren", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                def progress_callback(current, total):
                    progress_bar.progress(current / total)
                    status_text.text(f"Trainiere Team {current}/{total}...")
                
                with st.spinner("Training läuft..."):
                    challenge_state.run_all_trainings(
                        X_train, y_train, X_test, y_test,
                        progress_callback=progress_callback
                    )
                    
                    # Optimales Modell trainieren
                    challenge_state.train_optimal_model(X_train, y_train, X_test, y_test)
                
                st.success("✅ Training abgeschlossen!")
                time.sleep(2)
                
                # Automatisch zu Results wechseln
                challenge_state.set_phase("results")
                st.rerun()
    
    # ======== Ergebnis-Phase ========
    elif current_phase == "results":
        st.subheader("🏆 Leaderboard")
        
        leaderboard = challenge_state.get_leaderboard()
        
        if not leaderboard:
            st.warning("Keine Ergebnisse verfügbar. Training noch nicht durchgeführt?")
        else:
            # Leaderboard-Tabelle mit Highlighting
            rows = []
            for entry in leaderboard:
                rank_emoji = render_rank_emoji(entry["rank"])
                rows.append({
                    "Rang": rank_emoji,
                    "Team": entry["team_name"],
                    "F1-Score": f"{entry['f1_macro']*100:.2f}%",
                    "Accuracy": f"{entry['accuracy']*100:.2f}%",
                    "Zeit (s)": f"{entry['train_time']:.2f}",
                })
            
            df = pd.DataFrame(rows)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=(len(rows) + 1) * 35 + 3,
            )
            
            # Top 3 hervorheben
            st.markdown("###")
            col1, col2, col3 = st.columns(3)
            
            for i, col in enumerate([col1, col2, col3], start=1):
                if i <= len(leaderboard):
                    entry = leaderboard[i-1]
                    with col:
                        st.markdown(f"### {render_rank_emoji(i)} {entry['team_name']}")
                        st.metric("F1-Score", f"{entry['f1_macro']*100:.1f}%")
                        st.metric("Accuracy", f"{entry['accuracy']*100:.1f}%")
        
        # Feature-Analyse (Expander)
        st.markdown("---")
        with st.expander("📈 Feature-Analyse", expanded=False):
            st.subheader("Feature-Häufigkeit")
            
            # Zähle, wie oft jedes Feature gewählt wurde
            teams = challenge_state.get_all_teams()
            feature_counts = {f: 0 for f in FEATURE_NAMES}
            
            for team in teams.values():
                if team["selected_features"]:
                    for feat in team["selected_features"]:
                        feature_counts[feat] += 1
            
            # Balkendiagramm
            sorted_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)
            fig = go.Figure(go.Bar(
                x=[count for _, count in sorted_features],
                y=[name for name, _ in sorted_features],
                orientation="h",
                marker_color=HSB_PRIMARY,
                text=[f"{count}×" for _, count in sorted_features],
                textposition="auto",
            ))
            fig.update_layout(**get_plotly_layout(
                xaxis_title="Anzahl Teams",
                height=500,
                margin=dict(l=200, r=20, t=30, b=40),
            ))
            st.plotly_chart(fig, use_container_width=True)
            
            # Optimales Feature-Set
            st.markdown("###")
            st.subheader("🎯 Optimales Feature-Set (alle 12 Features)")
            
            optimal = challenge_state.get_optimal_result()
            if optimal:
                col_opt1, col_opt2, col_opt3 = st.columns(3)
                col_opt1.metric("F1-Score", f"{optimal['f1_macro']*100:.2f}%")
                col_opt2.metric("Accuracy", f"{optimal['accuracy']*100:.2f}%")
                col_opt3.metric("Zeit", f"{optimal['train_time']:.2f}s")
                
                # Feature Importances
                fig_opt = plot_feature_importances(
                    np.array(optimal["feature_importances"]),
                    optimal["feature_names"],
                    "Feature Importances (optimales Modell)"
                )
                st.plotly_chart(fig_opt, use_container_width=True)
            else:
                st.info("Optimales Modell noch nicht trainiert.")
    
    st.stop()  # Admin-View endet hier


# ============================================================
# VIEW: Team-Ansicht (mit Query-Parameter ?team=<id>)
# ============================================================

if team_id:
    team = challenge_state.get_team(team_id)
    
    if team is None:
        st.error("🚫 Team-ID nicht gefunden. Bitte neu registrieren.")
        if st.button("Zur Registrierung"):
            st.query_params.clear()
            st.rerun()
        st.stop()
    
    current_phase = challenge_state.get_phase()
    
    st.title(f"🏭 Bearing Challenge")
    st.subheader(f"Team: **{team['name']}**")
    st.markdown("---")
    
    # Auto-Refresh in Warte-Phasen
    if current_phase in ["registration", "training"] and HAS_AUTOREFRESH:
        st_autorefresh(interval=3000, key="team_refresh")
    
    # ======== Phase: Registrierung (Warten) ========
    if current_phase == "registration":
        st.info("✋ Willkommen! Warte auf den Dozenten, um die Feature-Auswahl zu starten...")
        
        teams_count = len(challenge_state.get_all_teams())
        st.metric("Registrierte Teams", teams_count)
    
    # ======== Phase: Feature-Auswahl ========
    elif current_phase == "feature_selection":
        if team["submitted"]:
            st.success("✅ Feature-Auswahl erfolgreich abgeschickt!")
            st.info(f"**Gewählte Features:** {', '.join(team['selected_features'])}")
            st.markdown("Warte auf die anderen Teams und das Training...")
        
        else:
            st.markdown("### 🔧 Wähle 4 Features aus")
            
            # Datenexploration (Expander)
            with st.expander("📊 Rohdaten ansehen", expanded=False):
                selected_class = st.selectbox(
                    "Fehlerklasse:",
                    CLASS_NAMES,
                    key="explore_class"
                )
                class_idx = CLASS_NAMES.index(selected_class)
                mask = y_train == class_idx
                class_segments = X_train[mask]
                
                segment_idx = st.slider("Segment-Nr.:", 0, len(class_segments)-1, 0, key="explore_seg")
                signal = class_segments[segment_idx]
                color = get_class_color(selected_class)
                
                fig_explore = plot_signal_and_fft(signal, selected_class, color)
                st.plotly_chart(fig_explore, use_container_width=True)
            
            # Feature-Auswahl
            st.markdown("###")
            
            # Session State für ausgewählte Features
            if "selected_features" not in st.session_state:
                st.session_state["selected_features"] = set()
            
            selected = st.session_state["selected_features"]
            
            # Counter
            st.markdown(f"**{len(selected)}/4 Features ausgewählt**")
            st.progress(len(selected) / 4)
            
            # Feature-Karten (Grid)
            st.markdown("###")
            cols_per_row = 3
            feature_list = FEATURE_NAMES
            
            for i in range(0, len(feature_list), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    idx = i + j
                    if idx >= len(feature_list):
                        break
                    
                    feat_name = feature_list[idx]
                    feat_info = FEATURE_INFO[feat_name]
                    
                    with col:
                        is_selected = feat_name in selected
                        
                        # Checkbox
                        checked = st.checkbox(
                            f"{feat_info['icon']} **{feat_name}**",
                            value=is_selected,
                            key=f"feat_{feat_name}",
                            disabled=(len(selected) >= 4 and not is_selected),
                        )
                        
                        # Update Selection
                        if checked and feat_name not in selected:
                            if len(selected) < 4:
                                selected.add(feat_name)
                        elif not checked and feat_name in selected:
                            selected.remove(feat_name)
                        
                        # Info-Expander
                        with st.expander("ℹ️ Details"):
                            st.markdown(f"**{feat_info['name_de']}**")
                            st.markdown(f"*{feat_info['domain']}*")
                            st.latex(feat_info['formula'])
                            st.caption(feat_info['description'])
                            st.caption(f"💡 {feat_info['intuition']}")
            
            # Submit-Button
            st.markdown("###")
            if len(selected) == 4:
                if st.button("✅ Auswahl abschicken", type="primary", use_container_width=True):
                    try:
                        challenge_state.submit_features(team_id, list(selected))
                        st.success("✅ Feature-Auswahl erfolgreich abgeschickt!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Fehler: {e}")
            else:
                st.warning(f"⚠️ Bitte wähle genau 4 Features (aktuell: {len(selected)}).")
    
    # ======== Phase: Training (Warten) ========
    elif current_phase == "training":
        st.info("⚙️ Die Modelle werden trainiert... Bitte warten!")
        with st.spinner("Training läuft..."):
            time.sleep(1)
    
    # ======== Phase: Ergebnisse ========
    elif current_phase == "results":
        result = challenge_state.get_team_result(team_id)
        
        if result is None:
            st.warning("⚠️ Noch keine Ergebnisse verfügbar.")
        else:
            st.success("🎉 Training abgeschlossen!")
            
            # Eigenes Ergebnis
            leaderboard = challenge_state.get_leaderboard()
            my_rank = next((e["rank"] for e in leaderboard if e["team_id"] == team_id), None)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("F1-Score", f"{result['f1_macro']*100:.2f}%")
            col2.metric("Accuracy", f"{result['accuracy']*100:.2f}%")
            col3.metric("Rang", f"{my_rank}/{len(leaderboard)}" if my_rank else "—")
            
            # Konfusionsmatrix
            st.markdown("###")
            with st.expander("📊 Konfusionsmatrix", expanded=False):
                fig_cm = plot_confusion_matrix(result["confusion_matrix"])
                st.plotly_chart(fig_cm, use_container_width=True)
            
            # Feature Importances
            with st.expander("📈 Feature Importances", expanded=False):
                fig_fi = plot_feature_importances(
                    result["feature_importances"],
                    result["feature_names"],
                    f"Feature Importances — {team['name']}"
                )
                st.plotly_chart(fig_fi, use_container_width=True)
            
            # Link zum Leaderboard
            st.markdown("---")
            st.markdown("### 🏆 Leaderboard")
            
            rows = []
            for entry in leaderboard:
                rank_emoji = render_rank_emoji(entry["rank"])
                rows.append({
                    "Rang": rank_emoji,
                    "Team": entry["team_name"],
                    "F1-Score": f"{entry['f1_macro']*100:.2f}%",
                    "Accuracy": f"{entry['accuracy']*100:.2f}%",
                })
            
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.stop()  # Team-View endet hier


# ============================================================
# VIEW: Registrierung (Default)
# ============================================================

st.title("🏭 Bearing Challenge")
st.subheader("Wälzlager-Diagnose mit Machine Learning")

st.markdown("""
Willkommen zur **Bearing Challenge**! In dieser interaktiven Übung tretet ihr als Team
gegeneinander an, indem ihr die besten Features zur Klassifikation von Wälzlager-Fehlern auswählt.

**Ablauf:**
1. **Registrierung:** Gebt euren Teamnamen ein
2. **Feature-Auswahl:** Wählt 4 aus 12 verfügbaren Features
3. **Training:** Ein Random-Forest-Modell wird automatisch trainiert
4. **Ergebnisse:** Seht eure Performance im Leaderboard!
""")

st.markdown("---")

current_phase = challenge_state.get_phase()

if current_phase != "registration":
    st.warning("⚠️ Die Registrierung ist geschlossen. Die Challenge hat bereits begonnen.")
    st.info("Falls du bereits registriert bist, verwende den Link, der dir angezeigt wurde.")
    st.stop()

# Registrierungs-Formular
st.markdown("### 📝 Teamname eingeben")

team_name_input = st.text_input(
    "Teamname (2-30 Zeichen):",
    max_chars=30,
    placeholder="z.B. Team Alpha",
)

if st.button("🚀 Team beitreten", type="primary", use_container_width=True):
    if len(team_name_input.strip()) < 2:
        st.error("❌ Teamname muss mindestens 2 Zeichen lang sein.")
    else:
        try:
            new_team_id = challenge_state.register_team(team_name_input)
            st.success(f"✅ Team '{team_name_input}' erfolgreich registriert!")
            time.sleep(1)
            
            # Redirect zur Team-Ansicht
            st.query_params["team"] = new_team_id
            st.rerun()
        
        except ValueError as e:
            st.error(f"❌ {e}")

# Live-Counter
st.markdown("###")
teams_count = len(challenge_state.get_all_teams())
st.info(f"📊 **{teams_count} Teams** sind bereits registriert.")

# Demo-Modus-Hinweis
if is_demo:
    st.caption("🔄 **Demo-Modus**: Synthetische Daten werden verwendet.")
