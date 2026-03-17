# Bearing Challenge — Schnellstart-Anleitung

## Überblick

Die **Bearing Challenge** ist eine interaktive Classroom-App, bei der Studierenden-Teams in Echtzeit gegeneinander antreten. Jedes Team wählt 4 aus 12 verfügbaren Features, ein ML-Modell wird automatisch trainiert, und ein Live-Leaderboard zeigt die F1-Scores.

---

## Schnellstart (Lokal)

### 1. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 2. Challenge-App starten

```bash
streamlit run app/challenge_app.py
```

Die App läuft dann auf: **http://localhost:8501**

### 3. Admin-Panel öffnen

Admin-URL (für Dozent):
```
http://localhost:8501/?admin=hsb2026
```

**Wichtig:** Das Admin-Passwort kann über die Umgebungsvariable `CHALLENGE_ADMIN_SECRET` geändert werden:

```bash
export CHALLENGE_ADMIN_SECRET=mein-geheimes-passwort
streamlit run app/challenge_app.py
```

### 4. Teams registrieren

Studierende öffnen einfach: **http://localhost:8501** und geben ihren Teamnamen ein.

---

## Docker-Deployment

### Mit docker-compose starten

```bash
docker-compose up challenge
```

Die App läuft dann auf: **http://localhost:8502**

### Umgebungsvariablen anpassen

In `docker-compose.yml`:

```yaml
environment:
  - CHALLENGE_ADMIN_SECRET=ihr-geheimes-passwort
  - CHALLENGE_APP_URL=https://ihre-domain.com
```

---

## Deployment auf Railway.app (Empfohlen)

### 1. GitHub-Repo erstellen

Pushen Sie dieses Projekt auf GitHub (public oder private).

### 2. Railway-Projekt erstellen

1. Gehen Sie zu [railway.app](https://railway.app)
2. Klicken Sie auf **New Project** → **Deploy from GitHub Repo**
3. Wählen Sie Ihr Repo aus

### 3. Umgebungsvariablen setzen

In den Railway-Settings:

```
CHALLENGE_ADMIN_SECRET=ihr-geheimes-passwort
CHALLENGE_APP_URL=https://ihr-projekt.up.railway.app
PORT=8501
```

### 4. Start-Command setzen (optional)

Railway erkennt den Dockerfile automatisch. Falls nicht, setzen Sie:

```bash
streamlit run app/challenge_app.py --server.port $PORT --server.address 0.0.0.0
```

### 5. Deployment

Railway deployed automatisch bei jedem Push zu `main`. Die App ist dann unter einer URL wie:

```
https://hsb-demo-production.up.railway.app
```

verfügbar.

---

## User-Flows

### Flow Dozent (Beamer)

1. Admin-URL öffnen: `/?admin=<SECRET>`
2. QR-Code zeigen (wird automatisch generiert)
3. Warten auf Team-Registrierungen
4. Phase wechseln: **Registrierung** → **Feature-Auswahl** → **Training** → **Ergebnisse**
5. In der **Training-Phase**: Button "🚀 Alle Modelle trainieren" klicken
6. In der **Ergebnis-Phase**: Leaderboard besprechen + Feature-Analyse zeigen
7. Reset für neue Runde

### Flow Studierende (Smartphone)

1. QR-Code scannen oder URL öffnen
2. Teamname eingeben → Registrierung
3. Warten auf Dozent
4. **Feature-Auswahl:**
   - Optional: Rohdaten erkunden (Zeitsignal + FFT)
   - 4 aus 12 Features auswählen
   - Feature-Infos lesen (Formel, Beschreibung, Intuition)
   - Auswahl abschicken
5. Warten auf Training
6. **Ergebnisse:**
   - Eigener F1-Score, Accuracy, Rang
   - Eigene Konfusionsmatrix
   - Eigene Feature Importances
   - Leaderboard ansehen

---

## Architektur

```
┌─────────────────────────────────────────────────┐
│              Streamlit App (Python)              │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Dozent  │  │  Team-   │  │  Leaderboard  │  │
│  │  Admin   │  │  Ansicht │  │  & Ergebnis   │  │
│  │  Panel   │  │ (Mobile) │  │  Analyse      │  │
│  └──────────┘  └──────────┘  └───────────────┘  │
│                                                  │
│  ┌──────────────────────────────────────────┐    │
│  │  Backend-Logik (src-Module)              │    │
│  │  • challenge_state.py (State-Management) │    │
│  │  • feature_info.py (Feature-Metadaten)   │    │
│  │  • features.py, classical_model.py       │    │
│  │  • data_loader.py                        │    │
│  └──────────────────────────────────────────┘    │
│                                                  │
│  ┌────────────────────────┐                      │
│  │  data/                 │                      │
│  │  challenge_state.json  │ (Persistenz)         │
│  └────────────────────────┘                      │
└─────────────────────────────────────────────────┘
```

---

## Wichtige Dateien

| Datei | Beschreibung |
|-------|-------------|
| `app/challenge_app.py` | Haupt-App (Routing, Views) |
| `app/ui_theme.py` | UI-Design-Tokens (HSB-Branding) |
| `src/challenge_state.py` | State-Management (Thread-safe) |
| `src/feature_info.py` | Feature-Beschreibungen (deutsch) |
| `data/challenge_state.json` | Persistierter State (automatisch erstellt) |
| `UI_DESIGN_STYLE_GUIDE.md` | Vollständiger Style-Guide |

---

## Konfiguration

### Admin-Secret

Standard: `hsb2026`

Ändern via Umgebungsvariable:

```bash
export CHALLENGE_ADMIN_SECRET=neues-passwort
```

### App-URL (für QR-Code)

Standard: `http://localhost:8501`

Ändern via Umgebungsvariable:

```bash
export CHALLENGE_APP_URL=https://ihre-domain.com
```

### Port

Standard: `8501`

Ändern via:

```bash
streamlit run app/challenge_app.py --server.port 8502
```

---

## Troubleshooting

### QR-Code wird nicht angezeigt

Installieren Sie `qrcode[pil]`:

```bash
pip install qrcode[pil]
```

### Auto-Refresh funktioniert nicht

Installieren Sie `streamlit-autorefresh`:

```bash
pip install streamlit-autorefresh
```

### State wird nicht persistiert

Stellen Sie sicher, dass der `data/`-Ordner existiert und beschreibbar ist:

```bash
mkdir -p data
chmod 755 data
```

### Teams können sich nicht registrieren

Prüfen Sie die Phase im Admin-Panel. Nur in der **Registrierungs-Phase** können sich Teams anmelden.

### Training schlägt fehl

Prüfen Sie, ob:
- Mindestens 1 Team Features abgegeben hat
- Die Daten korrekt geladen wurden (siehe Console-Output)
- Genügend Arbeitsspeicher verfügbar ist (mindestens 2 GB empfohlen)

---

## Daten

### Echte Daten (CWRU Dataset)

Laden Sie den CWRU Bearing Dataset von Kaggle herunter:

https://www.kaggle.com/datasets/brjapon/cwru-bearing-datasets/data

Entpacken Sie die `.mat`-Dateien in den `data/`-Ordner.

### Demo-Modus

Falls keine echten Daten vorliegen, generiert die App automatisch synthetische Demo-Daten.

---

## Sicherheit

### Admin-Secret schützen

- **Niemals** das Admin-Secret im Code committen
- Verwenden Sie Umgebungsvariablen oder ein Secret-Management-Tool
- Ändern Sie das Secret für Produktions-Deployments

### Timing-Angriffe vermeiden

Das Admin-Secret wird mit `hmac.compare_digest()` verglichen, um Timing-Angriffe zu vermeiden.

### Team-IDs

Team-IDs sind UUIDv4 und nicht erratbar. Es besteht kein Risiko, dass Teams sich gegenseitig manipulieren können.

---

## Entwicklung

### Neue Features hinzufügen

1. Feature-Funktion in `src/features.py` definieren
2. Feature zu `FEATURE_FUNCTIONS` hinzufügen
3. Metadaten in `src/feature_info.py` ergänzen
4. App neu starten

### UI-Anpassungen

Alle Design-Tokens sind in `app/ui_theme.py` definiert. Änderungen dort wirken sich auf die gesamte App aus.

Siehe auch: `UI_DESIGN_STYLE_GUIDE.md` für vollständige Design-Dokumentation.

---

## Support

Bei Fragen oder Problemen:

1. Prüfen Sie die Console-Ausgabe auf Fehlermeldungen
2. Lesen Sie die Spezifikation (siehe Projektordner)
3. Prüfen Sie den Style-Guide: `UI_DESIGN_STYLE_GUIDE.md`

---

## Lizenz

Dieses Projekt ist für Lehrzwecke an der Hochschule Bremen (HSB) entwickelt.
