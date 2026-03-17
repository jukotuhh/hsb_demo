# UI-Design & Style-Guide: Bearing Challenge

## Überblick

Dieser Style-Guide definiert das visuelle Erscheinungsbild der „Bearing Challenge" Classroom-App. Das Design orientiert sich am öffentlich sichtbaren Webauftritt der Hochschule Bremen (HSB) und verfolgt die Prinzipien: **seriös, technisch, klar, akademisch, mobil lesbar**.

---

## 1. Designprinzipien

### Leitgedanken
1. **HSB-Identität wahren**: Die App repräsentiert die Hochschule Bremen und sollte deren professionelles, weltoffenes und verlässliches Image widerspiegeln.
2. **Funktionalität vor Dekoration**: Farben und Gestaltungselemente dienen primär der Usability (Status, Fortschritt, Ranking), nicht der reinen Ästhetik.
3. **Dualer Kontext**: Die App muss sowohl auf dem Smartphone (Studierende) als auch auf dem Beamer (Dozent) einwandfrei funktionieren.
4. **Barrierefreiheit**: Ausreichende Kontraste, lesbare Schriftgrößen, klare visuelle Hierarchie.

---

## 2. Design-Token-System

### 2.1 Farbpalette

#### Primärfarben (HSB-inspiriert)

Basierend auf dem öffentlichen HSB-Webauftritt (blaues Kaleidoskop-Logo, Schlüssel-Symbol):

| Token | Hex-Wert | Verwendung |
|-------|----------|-----------|
| `hsb-primary` | `#005B96` | Hauptfarbe: Buttons, Akzente, Primär-CTA |
| `hsb-primary-light` | `#0077C8` | Hover-Zustände, Links |
| `hsb-primary-dark` | `#003D66` | Aktive/Gedrückte Zustände |
| `hsb-neutral-50` | `#F8F9FA` | Hintergrund (hell) |
| `hsb-neutral-100` | `#E9ECEF` | Kartenhintergründe |
| `hsb-neutral-200` | `#DEE2E6` | Borders, Divider |
| `hsb-neutral-700` | `#495057` | Sekundärtext |
| `hsb-neutral-900` | `#212529` | Primärtext |

#### Funktionsfarben

| Token | Hex-Wert | Verwendung |
|-------|----------|-----------|
| `color-success` | `#28A745` | Erfolg, abgeschlossene Tasks, korrekte Vorhersagen |
| `color-warning` | `#FFC107` | Warnung, ausstehende Abgaben |
| `color-error` | `#DC3545` | Fehler, falsche Vorhersagen |
| `color-info` | `#17A2B8` | Info-Boxen, Hinweise |

#### Leaderboard-Farben

| Rang | Token | Hex-Wert | Anwendung |
|------|-------|----------|-----------|
| 🥇 1. | `rank-gold` | `#FFD700` | Hintergrund/Badge für Platz 1 |
| 🥈 2. | `rank-silver` | `#C0C0C0` | Hintergrund/Badge für Platz 2 |
| 🥉 3. | `rank-bronze` | `#CD7F32` | Hintergrund/Badge für Platz 3 |

#### Chart-Farben (Klassen & Diagramme)

Für Wälzlager-Fehlerklassen (konsistent über alle Visualisierungen):

| Klasse | Token | Hex-Wert | Beschreibung |
|--------|-------|----------|--------------|
| Normal | `chart-normal` | `#28A745` | Grün — gesunder Zustand |
| Innenring (IR) | `chart-ir` | `#DC3545` | Rot — kritischer Fehler |
| Außenring (OR) | `chart-or` | `#005B96` | HSB-Blau — mittlerer Fehler |
| Kugel (B) | `chart-ball` | `#FFC107` | Gelb — variabler Fehler |

Für generische Diagramme (Feature Importances, Balken, Fortschritt):

| Token | Hex-Wert | Verwendung |
|-------|----------|-----------|
| `chart-primary` | `#005B96` | Hauptbalken, wichtige Werte |
| `chart-secondary` | `#0077C8` | Vergleichswerte |
| `chart-highlight` | `#28A745` | Hervorgehobene Features |

---

### 2.2 Typografie

#### Schrifthierarchie

Streamlit nutzt standardmäßig eine systembasierte Sans-Serif-Schrift. Die Hierarchie wird über Größen und Gewichte gesteuert:

| Element | Markdown/Streamlit | Größe (approx.) | Gewicht | Verwendung |
|---------|-------------------|-----------------|---------|-----------|
| **Hero-Titel** | `st.title()` | 2.5rem (40px) | Bold | Haupttitel auf Registrierungsseite |
| **Seitentitel** | `st.title()` | 2rem (32px) | Bold | Titel der Challenge-Ansichten |
| **Abschnitts-Titel** | `st.subheader()` | 1.5rem (24px) | Semibold | Sektionen innerhalb einer Seite |
| **Kartentitel** | `st.markdown("### ")` | 1.25rem (20px) | Semibold | Feature-Karten, Metriken |
| **Body-Text** | `st.markdown()` | 1rem (16px) | Regular | Fließtext, Beschreibungen |
| **Caption** | `st.caption()` | 0.875rem (14px) | Regular | Hilfetext, Metadaten |

**Wichtig für Beamer:** Auf der Admin-Ansicht sollten Titel mindestens `st.title()` und Metriken mit `st.metric()` in großer Schrift dargestellt werden.

---

### 2.3 Abstände & Layout

#### Spacing-System (basierend auf 8px-Grid)

| Token | Wert | Verwendung |
|-------|------|-----------|
| `space-xs` | 4px | Enge Abstände innerhalb von Komponenten |
| `space-sm` | 8px | Kompakte Abstände |
| `space-md` | 16px | Standard-Abstand zwischen Elementen |
| `space-lg` | 24px | Abstand zwischen Sektionen |
| `space-xl` | 32px | Große Abstände, Hero-Bereiche |
| `space-xxl` | 48px | Maximaler Abstand (z. B. vor Leaderboard) |

#### Border-Radius

| Token | Wert | Verwendung |
|-------|------|-----------|
| `radius-sm` | 4px | Buttons, kleine Badges |
| `radius-md` | 8px | Karten, Panels, Inputs |
| `radius-lg` | 12px | QR-Code-Container, große Karten |

#### Container-Breiten

| Kontext | Max-Breite | Begründung |
|---------|-----------|------------|
| **Registrierung (Mobile)** | 480px | Kompakte Formularansicht für Smartphones |
| **Team-Ansicht** | 100% | Vollbreite, responsive Spalten |
| **Admin-Panel** | 1400px | Großzügige Breite für Beamer/Desktop |

---

### 2.4 Komponentenzustände

#### Buttons

| Zustand | Hintergrund | Text | Border |
|---------|-------------|------|--------|
| **Default** | `hsb-primary` (#005B96) | Weiß | — |
| **Hover** | `hsb-primary-light` (#0077C8) | Weiß | — |
| **Active/Pressed** | `hsb-primary-dark` (#003D66) | Weiß | — |
| **Disabled** | `hsb-neutral-200` (#DEE2E6) | `hsb-neutral-700` | — |

#### Feature-Karten (Checkboxen)

| Zustand | Border | Hintergrund | Icon |
|---------|--------|-------------|------|
| **Unselected** | `hsb-neutral-200` (1px) | `hsb-neutral-50` | Grau |
| **Selected** | `hsb-primary` (2px) | `hsb-primary-light` (5% opacity) | Blau |
| **Submitted (Locked)** | `hsb-neutral-200` (1px) | `hsb-neutral-100` | Grau, deaktiviert |

#### Status-Badges

| Status | Hintergrund | Text | Icon |
|--------|-------------|------|------|
| **Ausstehend** | `color-warning` (20% opacity) | `#856404` | ⏳ |
| **Abgegeben** | `color-success` (20% opacity) | `#155724` | ✅ |
| **Gesperrt** | `hsb-neutral-200` | `hsb-neutral-700` | 🔒 |

---

## 3. Seitenbezogene UI-Muster

### 3.1 Registrierungsseite (Einstieg für Studierende)

**Layout-Prinzip:** Zentriert, minimalistisch, mobile-first.

#### Struktur

```
┌─────────────────────────────────────────┐
│          [HSB-Logo/Icon optional]       │
│                                         │
│   🏭 Bearing Challenge                   │
│   Wälzlager-Diagnose                    │
│                                         │
│   [Kurze Erklärung, 2-3 Sätze]         │
│                                         │
│   ┌───────────────────────────────┐    │
│   │  Teamname eingeben            │    │
│   │  [Input Field]                │    │
│   │  [Button: Team beitreten]     │    │
│   └───────────────────────────────┘    │
│                                         │
│   [Info: "X Teams registriert"]        │
└─────────────────────────────────────────┘
```

#### Design-Details

- **Hero-Bereich**: `st.title("🏭 Bearing Challenge")` mit `space-xl` Abstand danach
- **Erklärungstext**: `st.markdown()` in `space-md` unter Titel
- **Input-Feld**: `st.text_input()` mit Placeholder „Team Alpha", max. 30 Zeichen
- **Button**: `st.button(..., type="primary", use_container_width=True)` in `hsb-primary`
- **Live-Counter**: `st.info()` mit Icon, zeigt Anzahl registrierter Teams

**Bei geschlossener Registrierung:**
- Eingabefeld wird durch `st.warning("⚠️ Registrierung ist geschlossen")` ersetzt
- Button deaktiviert oder ausgeblendet

---

### 3.2 Team-Ansicht (Smartphone-optimiert)

**Layout-Prinzip:** Mobile-first, single-column, progressive disclosure.

#### Phase 1: Warten auf Freigabe

```
┌─────────────────────────────────────────┐
│   Willkommen, Team Alpha! 👋            │
│                                         │
│   Warte auf den Dozenten...            │
│   [Spinner/Animation]                   │
│                                         │
│   📊 X Teams sind bereit                │
└─────────────────────────────────────────┘
```

- Auto-Refresh alle 3 Sekunden via `streamlit-autorefresh`
- Friendly Tone, klare Statusanzeige

---

#### Phase 2: Feature-Auswahl

**Oberer Bereich: Datenexploration (ausklappbar)**

```
┌─────────────────────────────────────────┐
│ ▶️ 📊 Rohdaten ansehen (Expander)        │
│   ┌─────────────────────────────────┐   │
│   │ [Dropdown: Fehlerklasse]        │   │
│   │ [Zeitsignal-Plot]               │   │
│   │ [FFT-Plot]                      │   │
│   └─────────────────────────────────┘   │
│                                         │
│ ▶️ 📈 Feature-Verteilungen (Expander)   │
│   ┌─────────────────────────────────┐   │
│   │ [12 Mini-Violin-Plots]          │   │
│   └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

- Beide Expander standardmäßig **geschlossen** → Mobile Performance
- Plots: `use_container_width=True`, Höhe max. 350px

**Mittlerer Bereich: Feature-Auswahl**

```
┌─────────────────────────────────────────┐
│   Wähle 4 Features aus:  [2/4]          │
│                                         │
│   ┌──────────┐ ┌──────────┐            │
│   │ ⏱️ RMS   │ │ ⏱️ Std   │            │
│   │ [Info]   │ │ [Info]   │            │
│   │ [ ] Wahl │ │ [✓] Wahl │            │
│   └──────────┘ └──────────┘            │
│                                         │
│   ┌──────────┐ ┌──────────┐            │
│   │ ⏱️ Kurt. │ │ 📡 Spek. │            │
│   │ ...      │ │ ...      │            │
│   └──────────┘ └──────────┘            │
│   ... (8 weitere Karten)                │
│                                         │
│   [Button: ✅ Auswahl abschicken]       │
│   (nur aktiv bei genau 4 Features)     │
└─────────────────────────────────────────┘
```

**Feature-Karten (je ~150px Breite):**
- Grid: 2 Spalten auf Mobile, 3-4 auf Tablet/Desktop
- Border: `radius-md`, `hsb-neutral-200`
- Hover-Effekt: leichter Shadow
- **Selected**: Border `hsb-primary` (2px), Hintergrund leicht eingefärbt
- Icon: ⏱️ für Zeitbereich, 📡 für Frequenzbereich
- Infobox (Expander innerhalb Karte oder Tooltip):
  - LaTeX-Formel via `st.latex()`
  - Beschreibung (1-2 Sätze)
  - Intuition (Satz)

**Nach Abgabe: Locked State**
- Karten nicht mehr änderbar
- `st.success("✅ Feature-Auswahl erfolgreich abgeschickt!")`
- Button wird durch Status-Badge ersetzt

---

#### Phase 3: Training

```
┌─────────────────────────────────────────┐
│   ⚙️ Modelle werden trainiert...         │
│   [Progress Bar / Spinner]              │
│                                         │
│   Bitte warten...                       │
└─────────────────────────────────────────┘
```

- Auto-Refresh alle 5 Sekunden

---

#### Phase 4: Ergebnisse

```
┌─────────────────────────────────────────┐
│   Deine Ergebnisse 🎉                   │
│                                         │
│   ┌─────┬─────┬─────┐                  │
│   │ F1  │ Acc │ Rang│                  │
│   │ 87% │ 89% │  3  │                  │
│   └─────┴─────┴─────┘                  │
│                                         │
│   ▶️ Konfusionsmatrix (Expander)         │
│   ▶️ Feature Importances (Expander)     │
│                                         │
│   [Link zum Leaderboard scrollen]      │
└─────────────────────────────────────────┘
```

- Metriken: `st.metric()` mit großen Zahlen
- Rang: visuell hervorheben mit Farbe (Gold/Silber/Bronze wenn Top 3)
- Plots kompakt halten (max. 400px Höhe)

---

### 3.3 Admin-Panel (Beamer-optimiert)

**Layout-Prinzip:** Desktop/Beamer-first, große Schrift, hoher Kontrast.

#### Header (persistent)

```
┌─────────────────────────────────────────────────────────────┐
│  🏭 Bearing Challenge — Admin-Panel                          │
│  [QR-Code (300x300px)]  |  Phase: [BADGE: Registrierung]    │
└─────────────────────────────────────────────────────────────┘
```

- QR-Code: generiert mit `qrcode`, in Container mit `radius-lg`, Schatten
- Phasen-Badge: groß, farbcodiert:
  - Registrierung → `color-info`
  - Feature-Auswahl → `color-warning`
  - Training → `hsb-primary`
  - Ergebnisse → `color-success`

---

#### Phase-Steuerung

```
┌─────────────────────────────────────────┐
│   Phasen-Steuerung                      │
│                                         │
│   [Button: Registrierung starten]      │
│   [Button: Feature-Auswahl freigeben]  │
│   [Button: Training starten]           │
│   [Button: Ergebnisse zeigen]          │
│   [Button: Reset (rot)]                │
└─────────────────────────────────────────┘
```

- Buttons: volle Breite oder große Kacheln
- Aktiver Button: `hsb-primary`, inaktive: disabled
- Reset-Button: `color-error` mit Bestätigungsdialog

---

#### Registrierungs-Phase

```
┌─────────────────────────────────────────┐
│   Registrierte Teams (Live)             │
│                                         │
│   1. Team Alpha                         │
│   2. Team Beta                          │
│   3. Team Gamma                         │
│   ...                                   │
│                                         │
│   📊 8 Teams bereit                     │
└─────────────────────────────────────────┘
```

- Auto-Refresh alle 3 Sekunden
- Liste: große Schrift, nummeriert
- Counter: `st.metric()` prominent

---

#### Feature-Auswahl-Phase

```
┌─────────────────────────────────────────────────────────────┐
│   Team-Status                                                │
│                                                              │
│   Team          | Status         | Features                 │
│   ─────────────────────────────────────────────────────────│
│   Team Alpha    | ✅ Abgegeben   | RMS, Kurtosis, ...       │
│   Team Beta     | ⏳ Ausstehend  | —                        │
│   Team Gamma    | ✅ Abgegeben   | Std, Schiefe, ...        │
│                                                              │
│   Fortschritt: [████████░░] 5/8 Teams (62%)                 │
└─────────────────────────────────────────────────────────────┘
```

- Tabelle: `st.dataframe()` oder `st.table()` mit großem Font
- Status: farbige Badges (✅ grün, ⏳ gelb)
- Fortschrittsbalken: `st.progress()` mit Prozentanzeige

---

#### Training-Phase

```
┌─────────────────────────────────────────┐
│   Training                              │
│                                         │
│   [Button: 🚀 Alle Modelle trainieren]  │
│                                         │
│   [Progress: ████████░░░░ 67%]          │
│   Training läuft... (Team 5/8)          │
└─────────────────────────────────────────┘
```

- Button startet Training-Loop
- Live-Progress mit `st.progress()` und Status-Text

---

#### Ergebnis-Phase: Leaderboard

```
┌─────────────────────────────────────────────────────────────┐
│   🏆 Leaderboard                                             │
│                                                              │
│   Rang | Team         | F1-Score | Accuracy | Zeit          │
│   ──────────────────────────────────────────────────────────│
│   🥇 1 | Team Gamma   |   91.2%  |   92.5%  | 0.42s         │
│   🥈 2 | Team Alpha   |   87.3%  |   89.0%  | 0.38s         │
│   🥉 3 | Team Beta    |   85.1%  |   86.7%  | 0.45s         │
│      4 | Team Delta   |   82.0%  |   84.2%  | 0.40s         │
│   ...                                                        │
└─────────────────────────────────────────────────────────────┘
```

**Design-Details:**
- Rang-Spalte: Medals (🥇🥈🥉) für Top 3, sonst Nummer
- Hintergrund für Top 3:
  - Platz 1: `rank-gold` (10% opacity)
  - Platz 2: `rank-silver` (10% opacity)
  - Platz 3: `rank-bronze` (10% opacity)
- Sortierung: absteigend nach F1-Score (primär), Accuracy (sekundär)
- Tabelle: große Schrift, klare Trenner, abwechselnde Zeilenfarben für Lesbarkeit

---

#### Ergebnis-Phase: Feature-Analyse (Expander)

```
▶️ Feature-Analyse (klappbar)
  ┌─────────────────────────────────────────┐
  │ Feature-Häufigkeit (Balkendiagramm)     │
  │ RMS:       ████████ 7 Teams              │
  │ Kurtosis:  ██████   6 Teams              │
  │ ...                                     │
  │                                         │
  │ Optimales Feature-Set (Alle 12):        │
  │ F1-Score: 93.5% | Accuracy: 94.2%       │
  │                                         │
  │ [Feature Importances: Balkendiagramm]  │
  │                                         │
  │ Heatmap: Teams × Features               │
  │ (Welches Team hat welche Features?)     │
  └─────────────────────────────────────────┘
```

- Diagrams: Plotly mit `use_container_width=True`
- Heatmap: Teams als Y-Achse, Features als X-Achse, Farbe = gewählt (1) oder nicht (0)
- Feature-Importances des optimalen Modells als Benchmark

---

## 4. Responsive Design-Regeln

### 4.1 Breakpoints

| Breakpoint | Breite | Zielgerät | Anpassungen |
|-----------|--------|-----------|-------------|
| **Mobile** | < 768px | Smartphones | 1 Spalte, große Touch-Targets, reduzierte Plots |
| **Tablet** | 768px - 1024px | Tablets | 2 Spalten, moderate Plots |
| **Desktop** | > 1024px | Laptop/Desktop | 3-4 Spalten, volle Plot-Größe |
| **Beamer** | > 1400px | Projektion | Maximale Schriftgröße, hoher Kontrast |

### 4.2 Mobile-First-Regeln (Team-Ansicht)

1. **Sidebar deaktivieren**: `initial_sidebar_state="collapsed"`, ggf. via CSS versteckt
2. **Feature-Karten**: Von 3×4 Grid auf 2×6 oder 1×12 umschalten
3. **Plots**: Immer untereinander, nicht nebeneinander
4. **Buttons**: `use_container_width=True` für volle Breite
5. **Inputs**: Min. 44px Höhe (Touch-Target-Größe)

### 4.3 Desktop/Beamer-First-Regeln (Admin-Panel)

1. **QR-Code**: Mindestens 300×300px, zentriert
2. **Leaderboard**: Tabelle mit großer Schrift (min. 18px)
3. **Metriken**: `st.metric()` mit großen Zahlen, hoher Kontrast
4. **Phasen-Buttons**: Kacheln mit Icons, mindestens 150px Höhe
5. **Auto-Refresh**: Länger (10s) für stabilere Projektion

### 4.4 CSS-Medienqueries (Custom CSS)

Streamlit erlaubt Custom CSS via `st.markdown()`. Beispiel:

```css
/* Mobile: Feature-Karten volle Breite */
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: column;
    }
    .feature-card {
        width: 100% !important;
        margin-bottom: 16px;
    }
}

/* Beamer: Größere Schrift für Metriken */
@media (min-width: 1400px) {
    [data-testid="stMetricValue"] {
        font-size: 3rem !important;
    }
}
```

---

## 5. Datenvisualisierungen

### 5.1 Plotly-Diagramme (Farb-Konsistenz)

Alle Plotly-Charts sollten die definierten `chart-*`-Farben verwenden:

#### Zeitsignal & FFT (nach Klasse)

```python
# Beispiel: Farbzuordnung
CLASS_COLORS = {
    "Normal": "#28A745",    # chart-normal
    "IR": "#DC3545",        # chart-ir
    "OR": "#005B96",        # chart-or
    "B": "#FFC107",         # chart-ball
}

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=t, y=signal, mode="lines",
    line=dict(color=CLASS_COLORS[class_name], width=1.5),
))
fig.update_layout(
    plot_bgcolor="#F8F9FA",  # hsb-neutral-50
    paper_bgcolor="white",
    font=dict(family="sans-serif", size=14, color="#212529"),  # hsb-neutral-900
)
```

#### Konfusionsmatrix

```python
fig = go.Figure(data=go.Heatmap(
    z=cm, x=class_names, y=class_names,
    colorscale=[
        [0.0, "#F8F9FA"],      # hsb-neutral-50
        [0.5, "#0077C8"],      # hsb-primary-light
        [1.0, "#003D66"],      # hsb-primary-dark
    ],
    showscale=True,
))
```

Statt `"Greens"` oder `"Blues"` wird die HSB-Primärfarbe als Basis verwendet.

#### Balkendiagramme (Feature Importances, Häufigkeit)

```python
fig = go.Figure(go.Bar(
    x=values, y=feature_names,
    orientation="h",
    marker_color="#005B96",  # hsb-primary
    text=[f"{v:.3f}" for v in values],
    textposition="auto",
))
```

#### Leaderboard-Hinterlegung (optional, falls als Chart)

Für visuelle Hervorhebung im Leaderboard kann ein farbiger Streifen hinter den Top 3 gerendert werden:

```python
colors = ["#FFD700", "#C0C0C0", "#CD7F32"] + ["#F8F9FA"] * (len(teams) - 3)
fig = go.Figure(go.Bar(
    x=f1_scores, y=team_names,
    orientation="h",
    marker_color=colors,
))
```

---

### 5.2 Matplotlib/Seaborn (wenn verwendet)

Falls Matplotlib-Plots zum Einsatz kommen (z. B. im Notebook):

```python
import matplotlib.pyplot as plt
import seaborn as sns

# HSB-Palette setzen
hsb_palette = ["#28A745", "#DC3545", "#005B96", "#FFC107"]
sns.set_palette(hsb_palette)
sns.set_style("whitegrid")

# Plot mit HSB-Primärfarbe
plt.rcParams["axes.prop_cycle"] = plt.cycler(color=hsb_palette)
```

---

## 6. Technische Verankerung

### 6.1 Theme-Modul: `app/ui_theme.py` (neu)

Um die Tokens zentral zu verwalten, sollte ein dediziertes Modul erstellt werden:

```python
"""
UI Theme & Design Tokens für die Bearing Challenge.
Basierend auf dem HSB-Webauftritt (web-inspiriert).
"""

# ============================================================
# Farbpalette
# ============================================================

# Primärfarben (HSB)
HSB_PRIMARY = "#005B96"
HSB_PRIMARY_LIGHT = "#0077C8"
HSB_PRIMARY_DARK = "#003D66"
HSB_NEUTRAL_50 = "#F8F9FA"
HSB_NEUTRAL_100 = "#E9ECEF"
HSB_NEUTRAL_200 = "#DEE2E6"
HSB_NEUTRAL_700 = "#495057"
HSB_NEUTRAL_900 = "#212529"

# Funktionsfarben
COLOR_SUCCESS = "#28A745"
COLOR_WARNING = "#FFC107"
COLOR_ERROR = "#DC3545"
COLOR_INFO = "#17A2B8"

# Leaderboard
RANK_GOLD = "#FFD700"
RANK_SILVER = "#C0C0C0"
RANK_BRONZE = "#CD7F32"

# Chart-Farben (Klassen)
CHART_COLORS = {
    "Normal": COLOR_SUCCESS,
    "IR": COLOR_ERROR,
    "OR": HSB_PRIMARY,
    "B": COLOR_WARNING,
}

CHART_PRIMARY = HSB_PRIMARY
CHART_SECONDARY = HSB_PRIMARY_LIGHT
CHART_HIGHLIGHT = COLOR_SUCCESS

# ============================================================
# Spacing & Layout
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
    """Gibt ein Plotly-Layout-Dict mit HSB-Theme zurück."""
    layout = PLOTLY_LAYOUT.copy()
    layout.update(kwargs)
    return layout

# ============================================================
# Custom CSS
# ============================================================

CUSTOM_CSS = """
<style>
/* Feature-Karten */
.feature-card {
    border: 1px solid #DEE2E6;
    border-radius: 8px;
    padding: 16px;
    background-color: #F8F9FA;
    transition: all 0.2s;
}
.feature-card:hover {
    box-shadow: 0 4px 8px rgba(0, 91, 150, 0.1);
}
.feature-card.selected {
    border: 2px solid #005B96;
    background-color: rgba(0, 119, 200, 0.05);
}

/* Mobile: 1 Spalte */
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] {
        flex-direction: column;
    }
    .feature-card {
        width: 100% !important;
    }
}

/* Beamer: Große Schrift */
@media (min-width: 1400px) {
    [data-testid="stMetricValue"] {
        font-size: 3rem !important;
    }
    h1 {
        font-size: 3rem !important;
    }
}

/* Leaderboard: Top-3-Highlighting */
.rank-1 { background-color: rgba(255, 215, 0, 0.1); }
.rank-2 { background-color: rgba(192, 192, 192, 0.1); }
.rank-3 { background-color: rgba(205, 127, 50, 0.1); }
</style>
"""

def inject_custom_css():
    """Injiziert Custom CSS in die Streamlit-App."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
```

---

### 6.2 Verwendung in `app/challenge_app.py`

```python
import streamlit as st
from app.ui_theme import (
    HSB_PRIMARY, COLOR_SUCCESS, CHART_COLORS,
    get_plotly_layout, inject_custom_css
)

# Seiten-Konfiguration
st.set_page_config(
    page_title="Bearing Challenge — HSB",
    page_icon="🏭",
    layout="wide",
)

# Custom CSS injizieren
inject_custom_css()

# Beispiel: Button mit HSB-Primärfarbe
if st.button("Team beitreten", type="primary"):
    # Streamlit's primary-Button nutzt automatisch die Theme-Farbe
    pass

# Beispiel: Plotly-Chart mit HSB-Theme
fig = go.Figure(go.Scatter(x=x, y=y, line=dict(color=HSB_PRIMARY)))
fig.update_layout(**get_plotly_layout(title="Zeitsignal"))
st.plotly_chart(fig, use_container_width=True)
```

---

### 6.3 Streamlit-Config: `.streamlit/config.toml` (optional)

Für globales Theming kann eine Konfigurationsdatei erstellt werden:

```toml
[theme]
primaryColor = "#005B96"      # hsb-primary
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F8F9FA"  # hsb-neutral-50
textColor = "#212529"         # hsb-neutral-900
font = "sans serif"
```

**Wichtig:** Diese Datei überschreibt das Default-Theme. Bei Verwendung muss sichergestellt werden, dass alle Farben konsistent sind.

---

## 7. Akzeptanzkriterien (Quality Gates)

Bevor die Challenge-App als fertig gilt, müssen folgende Kriterien erfüllt sein:

### Visuell
- [ ] Alle Seiten nutzen konsistent die HSB-Primärfarbe (`#005B96`) für Buttons, Akzente und Charts.
- [ ] Leaderboard zeigt Gold/Silber/Bronze-Hinterlegung für Top 3.
- [ ] Feature-Karten haben klare visuelle Zustände (unselected, selected, locked).
- [ ] Status-Badges (ausstehend, abgegeben) sind farblich unterscheidbar.
- [ ] Plotly-Diagramme verwenden die definierten Klassenfarben (Normal=Grün, IR=Rot, OR=Blau, B=Gelb).

### Funktional
- [ ] Team-Ansicht ist auf einem Smartphone (375×667px, iPhone SE) ohne horizontales Scrollen nutzbar.
- [ ] Admin-Panel ist aus 3m Distanz auf einem Beamer lesbar (Schriftgrößen ≥ 24px für Titel).
- [ ] QR-Code ist mindestens 300×300px groß und wird korrekt generiert.
- [ ] Feature-Auswahl ist nach Abgabe visuell gesperrt (keine Änderungen möglich).

### Technisch
- [ ] Ein zentrales Theme-Modul (`app/ui_theme.py`) definiert alle Tokens.
- [ ] Custom CSS ist in einer Funktion (`inject_custom_css()`) gekapselt.
- [ ] Responsive Breakpoints (768px, 1024px, 1400px) sind via Media Queries implementiert.
- [ ] Plotly-Charts nutzen das zentrale Layout-Template (`get_plotly_layout()`).

### UX
- [ ] Registrierung zeigt live die Anzahl angemeldeter Teams.
- [ ] Team-Ansicht gibt klares Feedback nach Feature-Auswahl (Success-Message).
- [ ] Admin-Panel zeigt Fortschrittsbalken während Training.
- [ ] Leaderboard ist nach F1-Score sortiert (absteigend).

---

## 8. Anhang: Beispiel-Implementierung

### Feature-Karte (Beispiel)

```python
import streamlit as st
from app.ui_theme import HSB_PRIMARY, HSB_NEUTRAL_50, HSB_NEUTRAL_200

def render_feature_card(feature_name: str, domain: str, description: str, formula: str, selected: bool, locked: bool):
    """Rendert eine Feature-Karte."""
    
    # Icon je nach Domain
    icon = "⏱️" if domain == "Zeit" else "📡"
    
    # CSS-Klasse
    css_class = "feature-card"
    if selected:
        css_class += " selected"
    
    with st.container():
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        
        # Header
        st.markdown(f"### {icon} {feature_name}")
        
        # Formel (ausklappbar)
        with st.expander("ℹ️ Details"):
            st.latex(formula)
            st.markdown(description)
        
        # Checkbox (disabled wenn locked)
        if not locked:
            selected_new = st.checkbox(
                "Auswählen",
                value=selected,
                key=f"feat_{feature_name}",
            )
            return selected_new
        else:
            st.markdown("🔒 *Gesperrt*")
            return selected
        
        st.markdown('</div>', unsafe_allow_html=True)
```

---

### Leaderboard-Tabelle (Beispiel)

```python
import pandas as pd
import streamlit as st

def render_leaderboard(results: list[dict]):
    """Rendert das Leaderboard mit Top-3-Highlighting."""
    
    # Sortieren
    results_sorted = sorted(results, key=lambda x: x["f1_macro"], reverse=True)
    
    # Dataframe
    df = pd.DataFrame(results_sorted)
    df.insert(0, "Rang", range(1, len(df) + 1))
    df["F1-Score (%)"] = (df["f1_macro"] * 100).round(1)
    df["Accuracy (%)"] = (df["accuracy"] * 100).round(1)
    df["Zeit (s)"] = df["train_time"].round(2)
    
    # Display
    st.dataframe(
        df[["Rang", "team_name", "F1-Score (%)", "Accuracy (%)", "Zeit (s)"]],
        use_container_width=True,
        hide_index=True,
    )
    
    # Top 3 hervorheben (alternativ: mit Plotly Bar Chart)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"### 🥇 {results_sorted[0]['team_name']}")
        st.metric("F1-Score", f"{results_sorted[0]['f1_macro']*100:.1f}%")
    with col2:
        st.markdown(f"### 🥈 {results_sorted[1]['team_name']}")
        st.metric("F1-Score", f"{results_sorted[1]['f1_macro']*100:.1f}%")
    with col3:
        st.markdown(f"### 🥉 {results_sorted[2]['team_name']}")
        st.metric("F1-Score", f"{results_sorted[2]['f1_macro']*100:.1f}%")
```

---

## 9. Zusammenfassung & Checkliste für Implementierung

| Schritt | Beschreibung | Datei |
|---------|--------------|-------|
| 1. | Theme-Modul erstellen mit allen Tokens | `app/ui_theme.py` |
| 2. | Custom CSS für Karten, Responsive, Leaderboard | `app/ui_theme.py` (CUSTOM_CSS) |
| 3. | `.streamlit/config.toml` für globales Theme (optional) | `.streamlit/config.toml` |
| 4. | Challenge-App importiert Theme und injiziert CSS | `app/challenge_app.py` |
| 5. | Alle Plotly-Charts nutzen `get_plotly_layout()` | `app/challenge_app.py` |
| 6. | Feature-Karten als wiederverwendbare Komponente | `app/challenge_app.py` (Funktion) |
| 7. | Leaderboard mit Top-3-Highlighting | `app/challenge_app.py` (Funktion) |
| 8. | QR-Code mit HSB-Branding | `app/challenge_app.py` (Admin-View) |
| 9. | Responsive Tests auf Mobile, Tablet, Desktop, Beamer | Manuell |
| 10. | Akzeptanzkriterien durchgehen | Checkliste Abschnitt 7 |

---

**Autor:** KI-Assistant für HSB Demo-Projekt  
**Version:** 1.0 (März 2026)  
**Basis:** Öffentlich sichtbares HSB-Webdesign (web-inspiriert, nicht offizielles Corporate Design)

---

## Kontakt & Anpassungen

Falls offizielle HSB-Corporate-Design-Werte vorliegen (z. B. aus dem CD-Helpdesk), können die Farbtokens in `app/ui_theme.py` einfach aktualisiert werden. Alle abhängigen Komponenten (Charts, Buttons, Karten) übernehmen automatisch die neuen Werte.

**Ansprechpartner für CD-Anfragen:**  
Referat Kommunikation und Marketing (RKM), HSB  
[https://www.hs-bremen.de/die-hsb/organisation/verwaltung/kommunikation-und-marketing/](https://www.hs-bremen.de/die-hsb/organisation/verwaltung/kommunikation-und-marketing/)
