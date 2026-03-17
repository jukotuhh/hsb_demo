"""
Streamlit-App: Mustererkennung in einem Produktionsprozess
==========================================================

Interaktive Demo für die Probevorlesung.
Starten mit: streamlit run app/streamlit_app.py

Navigationsstruktur:
    1. 📊 Datenexploration
    2. 🔧 Feature-Extraktion
    3. 🌲 Klassisches ML (Random Forest)
    4. 🧠 Deep Learning (1D-CNN)
    5. ⚖️ Vergleich
"""

import sys
import os
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

# Projektverzeichnis zum Pfad hinzufügen
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from src.data_loader import (
    load_mat_files, segment_signals, normalize_segments,
    prepare_dataset, generate_demo_data, CLASS_NAMES, LABEL_NAMES,
)
from src.features import (
    extract_all_features, extract_features_single,
    FEATURE_NAMES, FEATURE_FUNCTIONS, _compute_spectrum,
)
from src.classical_model import train_classical, evaluate_classical
from src.cnn_model import build_cnn, train_cnn, evaluate_cnn, get_model_summary


# ============================================================
# Seiten-Konfiguration
# ============================================================

st.set_page_config(
    page_title="Mustererkennung — Wälzlager-Diagnose",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

COLORS = ["#2ecc71", "#e74c3c", "#3498db", "#f39c12"]
COLOR_MAP = {name: color for name, color in zip(CLASS_NAMES, COLORS)}


# ============================================================
# Caching: Daten und Modelle nur einmal laden/trainieren
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


@st.cache_data(show_spinner="Features werden berechnet...")
def compute_features(_X, split_name: str = ""):
    """Berechnet alle Features für die gegebenen Segmente."""
    return extract_all_features(_X)


@st.cache_resource(show_spinner="Random Forest wird trainiert...")
def train_rf(X_feat_values, y_train, n_estimators):
    """Trainiert den Random Forest."""
    result = train_classical(X_feat_values, y_train, n_estimators=n_estimators)
    return result


@st.cache_resource(show_spinner="CNN wird trainiert...")
def train_cnn_cached(X_train, y_train, epochs, batch_size):
    """Trainiert das CNN."""
    model = build_cnn(input_length=X_train.shape[1], num_classes=4)
    result = train_cnn(model, X_train, y_train, epochs=epochs,
                       batch_size=batch_size, verbose=0)
    return model, result


# ============================================================
# Daten laden
# ============================================================

data, is_demo = load_data()
X_train = data["X_train"]
X_test = data["X_test"]
y_train = data["y_train"]
y_test = data["y_test"]

# Features für Trainingsdaten
X_train_feat = compute_features(X_train, "train")
X_test_feat = compute_features(X_test, "test")


# ============================================================
# Sidebar — Navigation
# ============================================================

with st.sidebar:
    st.title("🏭 Navigation")
    st.markdown("---")

    page = st.radio(
        "Wählen Sie einen Abschnitt:",
        [
            "📊 Datenexploration",
            "🔧 Feature-Extraktion",
            "🌲 Klassisches ML",
            "🧠 Deep Learning",
            "⚖️ Vergleich",
        ],
        index=0,
    )

    st.markdown("---")
    st.markdown("### 📈 Datensatz-Info")
    if is_demo:
        st.info("🔄 **Demo-Modus** aktiv\n\nSynthetische Daten werden verwendet.\n\n"
                "Für echte Daten: CWRU-Dataset in `data/` ablegen.")
    else:
        st.success("✅ **Echte CWRU-Daten** geladen")

    st.metric("Trainings-Segmente", f"{len(X_train):,}")
    st.metric("Test-Segmente", f"{len(X_test):,}")
    st.metric("Segmentlänge", f"{X_train.shape[1]} Samples")
    st.metric("Klassen", "4")

    st.markdown("---")
    st.caption("Probevorlesung\n\"Mustererkennung in einem Produktionsprozess\"")


# ============================================================
# Hilfsfunktionen
# ============================================================

def plot_signal_plotly(signal, title="", color="#3498db", fs=12000):
    """Plottet ein einzelnes Signal mit Plotly."""
    t_ms = np.arange(len(signal)) / fs * 1000
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=t_ms, y=signal, mode="lines",
        line=dict(color=color, width=1),
        name="Signal",
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Zeit (ms)",
        yaxis_title="Amplitude",
        height=350,
        margin=dict(l=50, r=20, t=50, b=40),
    )
    return fig


def plot_spectrum_plotly(signal, title="", color="#3498db", fs=12000):
    """Plottet das FFT-Spektrum mit Plotly."""
    freqs, mag = _compute_spectrum(signal, fs)
    fig = go.Figure()
    # Transparente Füllfarbe erzeugen
    if color.startswith("#") and len(color) == 7:
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        fill_color = f"rgba({r},{g},{b},0.2)"
    else:
        fill_color = color

    fig.add_trace(go.Scatter(
        x=freqs, y=mag, mode="lines",
        fill="tozeroy",
        line=dict(color=color, width=1),
        fillcolor=fill_color,
        name="Spektrum",
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Frequenz (Hz)",
        yaxis_title="Amplitude",
        xaxis=dict(range=[0, 6000]),
        height=350,
        margin=dict(l=50, r=20, t=50, b=40),
    )
    return fig


def plot_confusion_matrix_plotly(cm, class_names, title="Konfusionsmatrix", colorscale="Greens"):
    """Plottet die Konfusionsmatrix mit Plotly."""
    cm_text = [[str(val) for val in row] for row in cm]
    fig = go.Figure(data=go.Heatmap(
        z=cm, x=class_names, y=class_names,
        text=cm_text, texttemplate="%{text}",
        textfont={"size": 16},
        colorscale=colorscale,
        showscale=True,
    ))
    fig.update_layout(
        title=title,
        xaxis_title="Vorhersage",
        yaxis_title="Wahrheit",
        height=450,
        yaxis=dict(autorange="reversed"),
    )
    return fig


# ============================================================
# Seite 1: Datenexploration
# ============================================================

if page == "📊 Datenexploration":
    st.title("📊 Datenexploration")
    st.markdown("""
    Wälzlager-Vibrationssignale enthalten **charakteristische Muster**,
    die auf verschiedene Fehlertypen hindeuten. Hier können Sie die
    Rohsignale interaktiv erkunden.
    """)

    st.markdown("---")

    # ---- Fehlertypen-Erklärung ----
    st.subheader("Fehlertypen im Wälzlager")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"### 🟢 Normal")
        st.markdown("Gesundes Lager, gleichmäßige Rotation, nur Grundrauschen.")
    with col2:
        st.markdown(f"### 🔴 Innenring (IR)")
        st.markdown("Defekt am Innenring. Erzeugt periodische Impulse bei hoher Drehfrequenz.")
    with col3:
        st.markdown(f"### 🔵 Außenring (OR)")
        st.markdown("Defekt am Außenring. Stärkere Impulse mit anderer Wiederholfrequenz.")
    with col4:
        st.markdown(f"### 🟡 Kugel (B)")
        st.markdown("Defekt an einer Wälzkugel. Unregelmäßige, variable Impulse.")

    st.markdown("---")

    # ---- Interaktive Signal-Anzeige ----
    st.subheader("Signale interaktiv erkunden")

    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        selected_class = st.selectbox(
            "Fehlerklasse wählen:",
            CLASS_NAMES,
            index=0,
        )
    class_idx = CLASS_NAMES.index(selected_class)

    # Segmente dieser Klasse
    mask = y_train == class_idx
    class_segments = X_train[mask]

    with col_ctrl2:
        segment_idx = st.slider(
            "Segment-Nr.:",
            0, len(class_segments) - 1, 0,
            help="Scrollen Sie durch verschiedene Segmente dieser Klasse"
        )

    signal = class_segments[segment_idx]
    color = COLORS[class_idx]

    col_sig, col_fft = st.columns(2)
    with col_sig:
        fig_sig = plot_signal_plotly(signal, f"Zeitsignal — {selected_class}", color)
        st.plotly_chart(fig_sig, use_container_width=True)
    with col_fft:
        fig_fft = plot_spectrum_plotly(signal, f"Frequenzspektrum — {selected_class}", color)
        st.plotly_chart(fig_fft, use_container_width=True)

    # ---- Alle Klassen im Vergleich ----
    st.markdown("---")
    st.subheader("Alle Klassen im Vergleich")

    fig = make_subplots(
        rows=2, cols=4,
        subplot_titles=[f"{n} — Zeitsignal" for n in CLASS_NAMES] +
                       [f"{n} — FFT" for n in CLASS_NAMES],
        vertical_spacing=0.12,
        horizontal_spacing=0.06,
    )

    t_ms = np.arange(1024) / 12000 * 1000

    for i, (name, color) in enumerate(zip(CLASS_NAMES, COLORS)):
        mask = y_train == i
        example = X_train[mask][0]
        freqs, mag = _compute_spectrum(example)

        # Zeitsignal
        fig.add_trace(go.Scatter(
            x=t_ms, y=example, mode="lines",
            line=dict(color=color, width=1), showlegend=False,
        ), row=1, col=i + 1)

        # FFT
        fig.add_trace(go.Scatter(
            x=freqs, y=mag, mode="lines", fill="tozeroy",
            line=dict(color=color, width=1), showlegend=False,
        ), row=2, col=i + 1)

    fig.update_layout(height=600, margin=dict(l=40, r=20, t=60, b=40))
    for i in range(4):
        fig.update_xaxes(title_text="Zeit (ms)", row=1, col=i + 1)
        fig.update_xaxes(title_text="Frequenz (Hz)", range=[0, 6000], row=2, col=i + 1)

    st.plotly_chart(fig, use_container_width=True)

    # ---- Klassenverteilung ----
    st.markdown("---")
    st.subheader("Klassenverteilung")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        counts_train = [int(np.sum(y_train == i)) for i in range(4)]
        fig_dist = go.Figure(go.Bar(
            x=CLASS_NAMES, y=counts_train,
            marker_color=COLORS, text=counts_train, textposition="auto",
        ))
        fig_dist.update_layout(title="Trainingsset", yaxis_title="Anzahl Segmente", height=400)
        st.plotly_chart(fig_dist, use_container_width=True)

    with col_v2:
        counts_test = [int(np.sum(y_test == i)) for i in range(4)]
        fig_dist2 = go.Figure(go.Bar(
            x=CLASS_NAMES, y=counts_test,
            marker_color=COLORS, text=counts_test, textposition="auto",
        ))
        fig_dist2.update_layout(title="Testset", yaxis_title="Anzahl Segmente", height=400)
        st.plotly_chart(fig_dist2, use_container_width=True)


# ============================================================
# Seite 2: Feature-Extraktion
# ============================================================

elif page == "🔧 Feature-Extraktion":
    st.title("🔧 Feature-Extraktion")
    st.markdown("""
    Für klassische ML-Algorithmen müssen wir aus jedem Rohsignal **aussagekräftige Zahlenwerte (Features)** berechnen.
    Wir extrahieren **12 Features** pro Segment — 8 im Zeitbereich und 4 im Frequenzbereich.
    """)

    st.markdown("---")

    # ---- Feature-Übersicht ----
    st.subheader("Übersicht: 12 Features")

    col_time, col_freq = st.columns(2)
    with col_time:
        st.markdown("#### ⏱️ Zeitbereich-Features")
        st.markdown("""
        | Feature | Beschreibung |
        |---------|-------------|
        | **RMS** | Effektivwert — misst die Signalenergie |
        | **Standardabweichung** | Streuung um den Mittelwert |
        | **Kurtosis** | Spitzigkeit — sensitiv für Impulse! |
        | **Schiefe** | Asymmetrie der Verteilung |
        | **Peak-to-Peak** | Maximale Schwingungsbreite |
        | **Scheitelfaktor** | Spitzenwert / RMS |
        | **Formfaktor** | RMS / mittlerer Absolutwert |
        | **Impulsfaktor** | Spitzenwert / mittlerer Absolutwert |
        """)

    with col_freq:
        st.markdown("#### 📡 Frequenzbereich-Features")
        st.markdown("""
        | Feature | Beschreibung |
        |---------|-------------|
        | **Spektraler Schwerpunkt** | Mittlere Frequenz (gewichtet) |
        | **Spektrale Bandbreite** | Frequenz-Streuung |
        | **Dominante Frequenz** | Frequenz mit max. Amplitude |
        | **Mittlere Frequenz** | Leistungs-gewichteter Schwerpunkt |
        """)

    st.markdown("---")

    # ---- Feature-Verteilungen ----
    st.subheader("Feature-Verteilungen pro Klasse")

    selected_features = st.multiselect(
        "Features auswählen:",
        FEATURE_NAMES,
        default=["RMS", "Kurtosis", "Scheitelfaktor", "Spektraler Schwerpunkt"],
    )

    if selected_features:
        n_feat = len(selected_features)
        cols = min(n_feat, 4)
        rows = (n_feat + cols - 1) // cols

        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=selected_features,
            vertical_spacing=0.15,
        )

        for idx, feat in enumerate(selected_features):
            r = idx // cols + 1
            c = idx % cols + 1
            for class_idx, (name, color) in enumerate(zip(CLASS_NAMES, COLORS)):
                mask = y_train == class_idx
                values = X_train_feat.loc[mask, feat]
                fig.add_trace(go.Histogram(
                    x=values, name=name,
                    marker_color=color, opacity=0.6,
                    nbinsx=40,
                    showlegend=(idx == 0),
                ), row=r, col=c)

        fig.update_layout(
            height=350 * rows,
            barmode="overlay",
            margin=dict(l=40, r=20, t=60, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ---- PCA-Projektion ----
    st.subheader("PCA-Projektion (2D)")
    st.markdown("""
    Die **Principal Component Analysis (PCA)** projiziert unsere 12 Features auf 2 Dimensionen.
    Gut trennbare Cluster = **Features sind aussagekräftig!**
    """)

    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train_feat[FEATURE_NAMES])
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    # Subsampling für schnellere Darstellung
    max_points = 2000
    if len(X_pca) > max_points:
        idx = np.random.RandomState(42).choice(len(X_pca), max_points, replace=False)
        X_pca_plot = X_pca[idx]
        y_plot = y_train[idx]
    else:
        X_pca_plot = X_pca
        y_plot = y_train

    fig_pca = go.Figure()
    for class_idx, (name, color) in enumerate(zip(CLASS_NAMES, COLORS)):
        mask = y_plot == class_idx
        fig_pca.add_trace(go.Scatter(
            x=X_pca_plot[mask, 0], y=X_pca_plot[mask, 1],
            mode="markers", name=name,
            marker=dict(color=color, size=5, opacity=0.6),
        ))

    fig_pca.update_layout(
        title=f"PCA — Erklärte Varianz: PC1={pca.explained_variance_ratio_[0]*100:.1f}%, "
              f"PC2={pca.explained_variance_ratio_[1]*100:.1f}%",
        xaxis_title=f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)",
        yaxis_title=f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)",
        height=550,
    )
    st.plotly_chart(fig_pca, use_container_width=True)

    # ---- Feature-Statistiken ----
    st.markdown("---")
    st.subheader("Feature-Statistiken pro Klasse")

    stats_dfs = []
    for class_idx, name in enumerate(CLASS_NAMES):
        mask = y_train == class_idx
        class_feat = X_train_feat.loc[mask, FEATURE_NAMES]
        stats = class_feat.describe().loc[["mean", "std"]].T
        stats.columns = [f"{name} — Mittelwert", f"{name} — Std"]
        stats_dfs.append(stats)

    stats_combined = pd.concat(stats_dfs, axis=1)
    st.dataframe(stats_combined.style.format("{:.4f}"), use_container_width=True)


# ============================================================
# Seite 3: Klassisches ML
# ============================================================

elif page == "🌲 Klassisches ML":
    st.title("🌲 Klassisches ML: Random Forest")
    st.markdown("""
    ### Wie funktioniert ein Random Forest?

    1. **Viele Entscheidungsbäume** werden auf zufälligen Teilmengen der Daten trainiert
    2. Jeder Baum \"stimmt ab\" → die **Mehrheitsentscheidung** gewinnt
    3. Vorteile: Robust, gute Genauigkeit, berechnet **Feature Importances**

    **Pipeline:**
    ```
    Rohsignal → Segmentierung → Feature-Extraktion (12 Features) → Standardisierung → Random Forest → Vorhersage
    ```
    """)

    st.markdown("---")

    # ---- Hyperparameter ----
    st.subheader("⚙️ Hyperparameter")
    col_hp1, col_hp2 = st.columns(2)
    with col_hp1:
        n_estimators = st.slider(
            "Anzahl Entscheidungsbäume:",
            min_value=10, max_value=500, value=100, step=10,
            help="Mehr Bäume = bessere Genauigkeit, aber längere Trainingszeit"
        )
    with col_hp2:
        st.markdown(f"""
        **Gewählte Parameter:**
        - 🌲 Bäume: **{n_estimators}**
        - 📊 Features: **{len(FEATURE_NAMES)}**
        - 📏 Training: **{len(X_train):,}** Segmente
        - 🧪 Test: **{len(X_test):,}** Segmente
        """)

    # ---- Training ----
    if st.button("🚀 Random Forest trainieren", type="primary", use_container_width=True):
        with st.spinner("Training läuft..."):
            rf_result = train_rf(
                X_train_feat[FEATURE_NAMES].values,
                y_train,
                n_estimators,
            )
            rf_model = rf_result["model"]

            rf_eval = evaluate_classical(
                rf_model, X_test_feat[FEATURE_NAMES], y_test,
                class_names=CLASS_NAMES,
            )

        st.success(f"✅ Training abgeschlossen in {rf_result['train_time']:.2f}s")

        # Metriken
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Test-Accuracy", f"{rf_eval['accuracy']*100:.2f}%")
        col_m2.metric("F1-Score (Macro)", f"{rf_eval['f1_macro']*100:.2f}%")
        col_m3.metric("Trainingszeit", f"{rf_result['train_time']:.2f}s")

        # Speichere in Session State
        st.session_state["rf_eval"] = rf_eval
        st.session_state["rf_result"] = rf_result
        st.session_state["rf_model"] = rf_model

    # ---- Ergebnisse anzeigen ----
    if "rf_eval" in st.session_state:
        rf_eval = st.session_state["rf_eval"]
        rf_result = st.session_state["rf_result"]

        st.markdown("---")

        col_cm, col_fi = st.columns(2)
        with col_cm:
            st.subheader("Konfusionsmatrix")
            fig_cm = plot_confusion_matrix_plotly(
                rf_eval["confusion_matrix"], CLASS_NAMES,
                f"Accuracy: {rf_eval['accuracy']*100:.1f}%", "Greens"
            )
            st.plotly_chart(fig_cm, use_container_width=True)

        with col_fi:
            st.subheader("Feature Importances")
            importances = rf_eval["feature_importances"]
            sorted_idx = np.argsort(importances)
            fig_fi = go.Figure(go.Bar(
                x=importances[sorted_idx],
                y=np.array(FEATURE_NAMES)[sorted_idx],
                orientation="h",
                marker_color="#2ecc71",
            ))
            fig_fi.update_layout(
                xaxis_title="Wichtigkeit",
                height=450,
                margin=dict(l=150, r=20, t=30, b=40),
            )
            st.plotly_chart(fig_fi, use_container_width=True)

        # Classification Report
        st.subheader("Detaillierter Klassifikationsbericht")
        st.code(rf_eval["classification_report"])


# ============================================================
# Seite 4: Deep Learning
# ============================================================

elif page == "🧠 Deep Learning":
    st.title("🧠 Deep Learning: 1D-CNN")
    st.markdown("""
    ### Was ist anders beim Deep Learning?

    | | Klassisches ML | Deep Learning |
    |---|---|---|
    | **Input** | Handgemachte Features | **Rohsignal** direkt |
    | **Feature-Extraktion** | Manuell (Domain-Wissen nötig) | **Automatisch** gelernt |
    | **Modell** | Random Forest (Bäume) | 1D-CNN (Faltungsschichten) |

    ### CNN-Architektur:
    ```
    Rohsignal (1024 Punkte)
        │
        ├─ Conv1D(32, kernel=7)  → Erkennt grobe Muster
        ├─ Conv1D(64, kernel=5)  → Erkennt feinere Muster
        ├─ Conv1D(128, kernel=3) → Erkennt komplexe Muster
        │
        ├─ GlobalAveragePooling  → Zusammenfassung
        ├─ Dense(64) + Dropout   → Entscheidungsschicht
        └─ Dense(4, Softmax)     → 4 Klassen-Wahrscheinlichkeiten
    ```
    """)

    st.markdown("---")

    # ---- Hyperparameter ----
    st.subheader("⚙️ Hyperparameter")
    col_hp1, col_hp2 = st.columns(2)
    with col_hp1:
        epochs = st.slider("Epochen:", 5, 50, 15, step=5)
    with col_hp2:
        batch_size = st.select_slider("Batch-Größe:", [16, 32, 64, 128], value=64)

    # ---- Modell-Zusammenfassung ----
    with st.expander("📋 Modell-Architektur anzeigen"):
        temp_model = build_cnn(input_length=1024, num_classes=4)
        summary = get_model_summary(temp_model)
        st.code(summary)
        total_params = temp_model.count_params()
        st.info(f"📊 Gesamte Parameter: **{total_params:,}** "
                f"(≈ {total_params * 4 / 1024:.0f} KB)")

    # ---- Training ----
    if st.button("🚀 CNN trainieren", type="primary", use_container_width=True):
        with st.spinner("CNN-Training läuft... (kann etwas dauern)"):
            cnn_model, cnn_result = train_cnn_cached(
                X_train, y_train, epochs, batch_size
            )

            cnn_eval = evaluate_cnn(
                cnn_model, X_test, y_test, class_names=CLASS_NAMES
            )

        st.success(f"✅ Training abgeschlossen in {cnn_result['train_time']:.1f}s")

        # Metriken
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Test-Accuracy", f"{cnn_eval['accuracy']*100:.2f}%")
        col_m2.metric("F1-Score (Macro)", f"{cnn_eval['f1_macro']*100:.2f}%")
        col_m3.metric("Trainingszeit", f"{cnn_result['train_time']:.1f}s")

        st.session_state["cnn_eval"] = cnn_eval
        st.session_state["cnn_result"] = cnn_result
        st.session_state["cnn_model"] = cnn_model

    # ---- Ergebnisse anzeigen ----
    if "cnn_eval" in st.session_state:
        cnn_eval = st.session_state["cnn_eval"]
        cnn_result = st.session_state["cnn_result"]

        st.markdown("---")

        # Trainingsverlauf
        col_loss, col_acc = st.columns(2)

        history = cnn_result["history"].history

        with col_loss:
            st.subheader("Verlust (Loss)")
            fig_loss = go.Figure()
            fig_loss.add_trace(go.Scatter(
                y=history["loss"], mode="lines+markers",
                name="Training", line=dict(color="#3498db", width=2),
            ))
            fig_loss.add_trace(go.Scatter(
                y=history["val_loss"], mode="lines+markers",
                name="Validierung", line=dict(color="#e74c3c", width=2, dash="dash"),
            ))
            fig_loss.update_layout(
                xaxis_title="Epoche", yaxis_title="Loss", height=400,
            )
            st.plotly_chart(fig_loss, use_container_width=True)

        with col_acc:
            st.subheader("Genauigkeit (Accuracy)")
            fig_acc = go.Figure()
            fig_acc.add_trace(go.Scatter(
                y=[v * 100 for v in history["accuracy"]], mode="lines+markers",
                name="Training", line=dict(color="#3498db", width=2),
            ))
            fig_acc.add_trace(go.Scatter(
                y=[v * 100 for v in history["val_accuracy"]], mode="lines+markers",
                name="Validierung", line=dict(color="#e74c3c", width=2, dash="dash"),
            ))
            fig_acc.update_layout(
                xaxis_title="Epoche", yaxis_title="Accuracy (%)", height=400,
            )
            st.plotly_chart(fig_acc, use_container_width=True)

        # Konfusionsmatrix
        st.subheader("Konfusionsmatrix")
        fig_cm = plot_confusion_matrix_plotly(
            cnn_eval["confusion_matrix"], CLASS_NAMES,
            f"1D-CNN — Accuracy: {cnn_eval['accuracy']*100:.1f}%", "Blues",
        )
        st.plotly_chart(fig_cm, use_container_width=True)

        # Classification Report
        st.subheader("Detaillierter Klassifikationsbericht")
        st.code(cnn_eval["classification_report"])

        # ---- Beispiel-Vorhersagen ----
        st.markdown("---")
        st.subheader("🔍 Einzelne Vorhersagen inspizieren")

        sample_idx = st.slider("Test-Segment wählen:", 0, len(X_test) - 1, 0)
        sample_signal = X_test[sample_idx]
        true_label = y_test[sample_idx]
        pred_probs = cnn_eval["y_prob"][sample_idx]
        pred_label = np.argmax(pred_probs)

        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            fig_ex = plot_signal_plotly(
                sample_signal,
                f"Test-Segment #{sample_idx}",
                COLORS[true_label],
            )
            st.plotly_chart(fig_ex, use_container_width=True)

        with col_ex2:
            fig_prob = go.Figure(go.Bar(
                x=CLASS_NAMES,
                y=pred_probs * 100,
                marker_color=COLORS,
                text=[f"{p*100:.1f}%" for p in pred_probs],
                textposition="auto",
            ))
            fig_prob.update_layout(
                title="CNN-Vorhersage (Wahrscheinlichkeiten)",
                yaxis_title="Wahrscheinlichkeit (%)",
                yaxis=dict(range=[0, 105]),
                height=350,
            )
            st.plotly_chart(fig_prob, use_container_width=True)

        if pred_label == true_label:
            st.success(f"✅ Korrekt! Wahrheit: **{CLASS_NAMES[true_label]}** | "
                       f"Vorhersage: **{CLASS_NAMES[pred_label]}** "
                       f"({pred_probs[pred_label]*100:.1f}%)")
        else:
            st.error(f"❌ Falsch! Wahrheit: **{CLASS_NAMES[true_label]}** | "
                     f"Vorhersage: **{CLASS_NAMES[pred_label]}** "
                     f"({pred_probs[pred_label]*100:.1f}%)")


# ============================================================
# Seite 5: Vergleich
# ============================================================

elif page == "⚖️ Vergleich":
    st.title("⚖️ Vergleich: Klassisches ML vs. Deep Learning")

    has_rf = "rf_eval" in st.session_state
    has_cnn = "cnn_eval" in st.session_state

    if not has_rf or not has_cnn:
        st.warning("⚠️ Bitte trainieren Sie zuerst **beide Modelle** "
                   "(Random Forest + CNN) auf den vorherigen Seiten.")
        if not has_rf:
            st.info("→ Random Forest: Gehen Sie zu \"🌲 Klassisches ML\"")
        if not has_cnn:
            st.info("→ 1D-CNN: Gehen Sie zu \"🧠 Deep Learning\"")
        st.stop()

    rf_eval = st.session_state["rf_eval"]
    rf_result = st.session_state["rf_result"]
    cnn_eval = st.session_state["cnn_eval"]
    cnn_result = st.session_state["cnn_result"]

    # ---- Metriken-Vergleich ----
    st.subheader("📊 Metriken im Vergleich")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "RF — Accuracy",
        f"{rf_eval['accuracy']*100:.1f}%",
    )
    col2.metric(
        "CNN — Accuracy",
        f"{cnn_eval['accuracy']*100:.1f}%",
        delta=f"{(cnn_eval['accuracy']-rf_eval['accuracy'])*100:+.1f}%",
    )
    col3.metric(
        "RF — Trainingszeit",
        f"{rf_result['train_time']:.2f}s",
    )
    col4.metric(
        "CNN — Trainingszeit",
        f"{cnn_result['train_time']:.1f}s",
    )

    st.markdown("---")

    # ---- Vergleichstabelle ----
    st.subheader("Detaillierter Vergleich")

    comparison = pd.DataFrame({
        "Eigenschaft": [
            "Test-Accuracy",
            "F1-Score (Macro)",
            "Trainingszeit",
            "Feature-Engineering nötig?",
            "Interpretierbarkeit",
            "Modellkomplexität",
            "Input",
        ],
        "🌲 Random Forest": [
            f"{rf_eval['accuracy']*100:.2f}%",
            f"{rf_eval['f1_macro']*100:.2f}%",
            f"{rf_result['train_time']:.2f}s",
            "Ja (12 Features manuell)",
            "Hoch (Feature Importances)",
            "Niedrig",
            "Extrahierte Features (12 Werte)",
        ],
        "🧠 1D-CNN": [
            f"{cnn_eval['accuracy']*100:.2f}%",
            f"{cnn_eval['f1_macro']*100:.2f}%",
            f"{cnn_result['train_time']:.1f}s",
            "Nein (Rohsignal direkt)",
            "Niedrig (Black Box)",
            "Hoch",
            "Rohsignal (1024 Werte)",
        ],
    })

    st.dataframe(
        comparison.style.set_properties(**{"text-align": "center"}),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")

    # ---- Konfusionsmatrizen nebeneinander ----
    st.subheader("Konfusionsmatrizen")

    col_cm1, col_cm2 = st.columns(2)
    with col_cm1:
        fig_cm_rf = plot_confusion_matrix_plotly(
            rf_eval["confusion_matrix"], CLASS_NAMES,
            f"Random Forest — {rf_eval['accuracy']*100:.1f}%", "Greens",
        )
        st.plotly_chart(fig_cm_rf, use_container_width=True)

    with col_cm2:
        fig_cm_cnn = plot_confusion_matrix_plotly(
            cnn_eval["confusion_matrix"], CLASS_NAMES,
            f"1D-CNN — {cnn_eval['accuracy']*100:.1f}%", "Blues",
        )
        st.plotly_chart(fig_cm_cnn, use_container_width=True)

    # ---- Balkendiagramm ----
    st.markdown("---")
    st.subheader("Accuracy & F1-Score")

    fig_compare = go.Figure()
    fig_compare.add_trace(go.Bar(
        x=["Accuracy", "F1-Score"],
        y=[rf_eval["accuracy"] * 100, rf_eval["f1_macro"] * 100],
        name="🌲 Random Forest",
        marker_color="#2ecc71",
        text=[f"{rf_eval['accuracy']*100:.1f}%", f"{rf_eval['f1_macro']*100:.1f}%"],
        textposition="auto",
    ))
    fig_compare.add_trace(go.Bar(
        x=["Accuracy", "F1-Score"],
        y=[cnn_eval["accuracy"] * 100, cnn_eval["f1_macro"] * 100],
        name="🧠 1D-CNN",
        marker_color="#3498db",
        text=[f"{cnn_eval['accuracy']*100:.1f}%", f"{cnn_eval['f1_macro']*100:.1f}%"],
        textposition="auto",
    ))

    fig_compare.update_layout(
        barmode="group",
        yaxis_title="Prozent (%)",
        yaxis=dict(range=[0, 105]),
        height=450,
        legend=dict(font=dict(size=14)),
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    # ---- Fazit ----
    st.markdown("---")
    st.subheader("📝 Fazit")

    st.markdown("""
    ### Wann welchen Ansatz wählen?

    | Situation | Empfehlung |
    |-----------|------------|
    | Wenig Daten, klares Domain-Wissen | **Klassisches ML** |
    | Viele Daten, komplexe Muster | **Deep Learning** |
    | Interpretierbarkeit wichtig (z.B. Zertifizierung) | **Klassisches ML** |
    | Schnelle Entwicklung ohne Expertenwissen | **Deep Learning** |
    | Echtzeit auf Edge-Geräten | **Klassisches ML** (schnellere Inferenz) |

    ### Kernerkenntnisse:

    1. **Klassisches ML** benötigt **Domain-Wissen** für die Feature-Extraktion,
       liefert aber interpretierbare Ergebnisse und ist schneller zu trainieren.

    2. **Deep Learning** lernt Features **automatisch** aus Rohsignalen und kann
       subtilere Muster erkennen, ist aber weniger interpretierbar.

    3. In der Praxis: **Beide Ansätze haben ihre Berechtigung!**
       Oft startet man mit klassischem ML und wechselt zu DL, wenn mehr Daten verfügbar sind.

    ### Ausblick:
    - **Transfer Learning** — vortrainierte Modelle auf neue Maschinen übertragen
    - **Anomalieerkennung** — nur \"Normal\" trainieren, Abweichungen erkennen
    - **Explainable AI (XAI)** — Deep Learning interpretierbar machen
    - **Edge Deployment** — Modelle auf Mikrocontrollern für Echtzeit-Überwachung
    """)
