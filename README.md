# 🏭 Mustererkennung in einem Produktionsprozess

## Wälzlager-Fehlerdiagnose mit dem CWRU Bearing Dataset

Interaktive Demo für eine Probevorlesung — zeigt den kompletten Weg von
Rohdaten über Feature-Extraktion bis hin zu klassischem Machine Learning
und Deep Learning für die automatische Fehlererkennung in Wälzlagern.

---

## 📋 Inhalt

| Komponente | Beschreibung |
|------------|-------------|
| **Streamlit-App** | Interaktive Web-Demo für die Live-Vorlesung |
| **Jupyter Notebook** | Handout zum Nacharbeiten mit Code und Erklärungen |
| **src/** | Wiederverwendbare Python-Module |

## 🗂 Projektstruktur

```
hsb_demo/
├── app/
│   └── streamlit_app.py          ← Interaktive Streamlit-Demo
├── notebooks/
│   └── mustererkennung_demo.ipynb ← Jupyter-Handout
├── src/
│   ├── __init__.py
│   ├── data_loader.py            ← Daten laden & segmentieren
│   ├── features.py               ← Feature-Extraktion (12 Features)
│   ├── classical_model.py        ← Random Forest Pipeline
│   └── cnn_model.py              ← 1D-CNN (Keras)
├── data/                          ← CWRU .mat-Dateien (s. unten)
├── models/                        ← Gespeicherte trainierte Modelle
├── requirements.txt
└── README.md
```

---

## 🚀 Schnellstart (Docker — empfohlen)

### 1. (Optional) CWRU-Dataset herunterladen

Den echten Dataset können Sie von Kaggle herunterladen:

👉 https://www.kaggle.com/datasets/brjapon/cwru-bearing-datasets/data

Entpacken Sie die `.mat`-Dateien in den Ordner `data/`.

> **Hinweis:** Ohne den echten Dataset werden automatisch **synthetische Demo-Daten** verwendet,
> die das Verhalten echter Wälzlager-Signale simulieren. Die gesamte Demo funktioniert auch ohne Download!

### 2. Streamlit-App starten (Live-Demo im Hörsaal)

```bash
docker compose up streamlit
```

Öffnen Sie → **http://localhost:8501**

### 3. Jupyter Notebook starten (Handout)

```bash
docker compose up jupyter
```

Öffnen Sie → **http://localhost:8888/?token=demo**

### 4. Beides gleichzeitig

```bash
docker compose up
```

---

### Alternative: Ohne Docker (lokal)

```bash
pip install -r requirements.txt
streamlit run app/streamlit_app.py            # Streamlit
jupyter notebook notebooks/mustererkennung_demo.ipynb  # Notebook
```

---

## 📊 Was wird gezeigt?

### Schritt 1 — Datenexploration
- Vibrationssignale der 4 Fehlerklassen im Zeitbereich
- Frequenzspektren (FFT) zum Vergleich
- Klassenverteilung

### Schritt 2 — Feature-Extraktion
- 8 Zeitbereich-Features (RMS, Kurtosis, Scheitelfaktor, ...)
- 4 Frequenzbereich-Features (Spektraler Schwerpunkt, ...)
- PCA-Projektion zur Visualisierung der Trennbarkeit

### Schritt 3 — Klassisches ML (Random Forest)
- Training mit sklearn-Pipeline (StandardScaler → RandomForest)
- Konfusionsmatrix, Feature Importances
- Interaktiv: Anzahl Bäume einstellen

### Schritt 4 — Deep Learning (1D-CNN)
- 3-schichtiges CNN auf Rohsignalen (kein Feature-Engineering!)
- Trainingsverlauf (Loss/Accuracy-Kurven)
- Einzelvorhersagen mit Wahrscheinlichkeiten inspizieren

### Schritt 5 — Vergleich
- Side-by-side Metriken (Accuracy, F1, Trainingszeit)
- Konfusionsmatrizen nebeneinander
- Diskussion: Wann welchen Ansatz?

---

## 🔧 Technologie-Stack

| Bibliothek | Verwendung |
|-----------|------------|
| **NumPy / SciPy** | Signalverarbeitung, .mat-Dateien |
| **Pandas** | Feature-Tabellen |
| **Matplotlib / Seaborn** | Statische Plots (Notebook) |
| **Plotly** | Interaktive Plots (Streamlit) |
| **scikit-learn** | Random Forest, PCA, Metriken |
| **TensorFlow / Keras** | 1D-CNN |
| **Streamlit** | Web-App |
| **ipywidgets** | Notebook-Interaktivität |

---

## 📚 Hintergrund: CWRU Bearing Dataset

- **Quelle:** Case Western Reserve University Bearing Data Center
- **Sensoren:** Beschleunigungssensoren am Motorlagergehäuse
- **Abtastrate:** 12.000 Hz (Drive End)
- **Fehlertypen:**
  - Normal (gesundes Lager)
  - Innenringfehler (IR) — verschiedene Durchmesser
  - Außenringfehler (OR) — verschiedene Positionen
  - Kugelfehler (B) — verschiedene Durchmesser
- **Motorlasten:** 0, 1, 2, 3 HP

---

*Erstellt für die Probevorlesung „Mustererkennung in einem Produktionsprozess"*
