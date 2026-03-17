"""
challenge_state.py — Serverseitiger State für die Classroom-Challenge
======================================================================

Dieses Modul verwaltet den gemeinsamen State aller Teams und der Challenge.
Da alle Streamlit-Clients denselben Serverprozess teilen, wird der State
im Prozessspeicher gehalten (thread-safe mit `threading.Lock`) und zusätzlich
in einer JSON-Datei persistiert.

State-Struktur:
    {
        "phase": "registration" | "feature_selection" | "training" | "results",
        "teams": {
            "<team_id>": {
                "name": "Team Alpha",
                "joined_at": "2026-03-17T10:00:00",
                "selected_features": ["RMS", "Kurtosis", ...] | null,
                "submitted": false
            }
        },
        "results": {
            "<team_id>": {
                "f1_macro": 0.87,
                "accuracy": 0.89,
                "confusion_matrix": [[...]],
                "feature_importances": {...},
                "train_time": 0.42
            }
        }
    }
"""

import json
import os
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from src.features import FEATURE_NAMES, extract_selected_features
from src.classical_model import train_classical, evaluate_classical
from src.data_loader import CLASS_NAMES


# ============================================================
# Globaler State (prozessweit, thread-safe)
# ============================================================

_STATE_LOCK = threading.Lock()
_STATE = {
    "phase": "registration",
    "teams": {},
    "results": {},
    "optimal_result": None,  # Training mit allen 12 Features
}

# Persistenz-Pfad
STATE_FILE = Path("data/challenge_state.json")


# ============================================================
# Persistenz: Laden & Speichern
# ============================================================

def _load_state_from_disk():
    """Lädt den State aus der JSON-Datei (falls vorhanden)."""
    global _STATE
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                # Merge mit Default-Keys
                _STATE["phase"] = loaded.get("phase", "registration")
                _STATE["teams"] = loaded.get("teams", {})
                _STATE["results"] = loaded.get("results", {})
                _STATE["optimal_result"] = loaded.get("optimal_result", None)
                print(f"✓ Challenge-State geladen: {len(_STATE['teams'])} Teams")
        except Exception as e:
            print(f"⚠ Fehler beim Laden des States: {e}")


def _save_state_to_disk():
    """Speichert den aktuellen State in die JSON-Datei."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        # NumPy-Arrays in Listen konvertieren
        state_copy = {
            "phase": _STATE["phase"],
            "teams": _STATE["teams"],
            "results": {
                tid: {
                    "f1_macro": float(r["f1_macro"]),
                    "accuracy": float(r["accuracy"]),
                    "confusion_matrix": r["confusion_matrix"].tolist() if isinstance(r["confusion_matrix"], np.ndarray) else r["confusion_matrix"],
                    "feature_importances": r["feature_importances"].tolist() if isinstance(r["feature_importances"], np.ndarray) else r["feature_importances"],
                    "feature_names": r["feature_names"],
                    "train_time": float(r["train_time"]),
                }
                for tid, r in _STATE["results"].items()
            },
            "optimal_result": _STATE.get("optimal_result"),
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state_copy, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"⚠ Fehler beim Speichern des States: {e}")


# Beim Import einmalig laden
_load_state_from_disk()


# ============================================================
# API-Funktionen (thread-safe)
# ============================================================

def get_phase() -> str:
    """Gibt die aktuelle Challenge-Phase zurück."""
    with _STATE_LOCK:
        return _STATE["phase"]


def set_phase(phase: str):
    """
    Setzt die Challenge-Phase (nur für Dozent).
    
    Erlaubte Phasen:
        - "registration"
        - "feature_selection"
        - "training"
        - "results"
    """
    valid_phases = ["registration", "feature_selection", "training", "results"]
    if phase not in valid_phases:
        raise ValueError(f"Ungültige Phase: {phase}. Erlaubt: {valid_phases}")
    
    with _STATE_LOCK:
        _STATE["phase"] = phase
        _save_state_to_disk()


def register_team(name: str) -> str:
    """
    Registriert ein neues Team.
    
    Parameter:
        name: Teamname (2-30 Zeichen, einzigartig)
    
    Returns:
        team_id (UUID4)
    
    Raises:
        ValueError: Wenn der Name ungültig oder bereits vergeben ist.
    """
    name = name.strip()
    
    # Validierung
    if len(name) < 2 or len(name) > 30:
        raise ValueError("Teamname muss zwischen 2 und 30 Zeichen lang sein.")
    
    with _STATE_LOCK:
        # Prüfe auf Duplikate (case-insensitive)
        existing_names = {t["name"].lower() for t in _STATE["teams"].values()}
        if name.lower() in existing_names:
            raise ValueError(f"Der Teamname '{name}' ist bereits vergeben.")
        
        # Team erstellen
        team_id = str(uuid.uuid4())
        _STATE["teams"][team_id] = {
            "name": name,
            "joined_at": datetime.now().isoformat(),
            "selected_features": None,
            "submitted": False,
        }
        _save_state_to_disk()
        
        print(f"✓ Team registriert: {name} (ID: {team_id})")
        return team_id


def get_team(team_id: str) -> dict | None:
    """Gibt die Team-Daten zurück oder None."""
    with _STATE_LOCK:
        return _STATE["teams"].get(team_id)


def get_all_teams() -> dict:
    """Gibt alle Teams zurück (dict: team_id → team_data)."""
    with _STATE_LOCK:
        return dict(_STATE["teams"])


def submit_features(team_id: str, features: list[str]):
    """
    Speichert die Feature-Auswahl eines Teams.
    
    Parameter:
        team_id: Team-ID
        features: Liste mit genau 4 Feature-Namen
    
    Raises:
        ValueError: Wenn Team nicht existiert, bereits submitted, oder Features ungültig.
    """
    with _STATE_LOCK:
        team = _STATE["teams"].get(team_id)
        if team is None:
            raise ValueError(f"Team-ID nicht gefunden: {team_id}")
        
        if team["submitted"]:
            raise ValueError("Dieses Team hat bereits Features abgegeben.")
        
        # Validierung
        if len(features) != 4:
            raise ValueError(f"Es müssen genau 4 Features ausgewählt werden (erhalten: {len(features)}).")
        
        for feat in features:
            if feat not in FEATURE_NAMES:
                raise ValueError(f"Unbekanntes Feature: '{feat}'. Verfügbar: {FEATURE_NAMES}")
        
        # Speichern
        team["selected_features"] = features
        team["submitted"] = True
        _save_state_to_disk()
        
        print(f"✓ Feature-Auswahl gespeichert für {team['name']}: {features}")


def run_all_trainings(X_train, y_train, X_test, y_test, progress_callback=None):
    """
    Trainiert für jedes Team ein Random Forest mit dessen 4 gewählten Features.
    
    Parameter:
        X_train, y_train: Trainingsdaten (Rohsignale)
        X_test, y_test:   Testdaten (Rohsignale)
        progress_callback: Optionale Callback-Funktion (team_idx, total_teams)
    
    Speichert die Ergebnisse in _STATE["results"].
    """
    with _STATE_LOCK:
        teams_to_train = [
            (tid, team) for tid, team in _STATE["teams"].items()
            if team["submitted"] and team["selected_features"] is not None
        ]
    
    if not teams_to_train:
        print("⚠ Keine Teams haben Features abgegeben.")
        return
    
    print(f"\n🚀 Starte Training für {len(teams_to_train)} Teams...")
    
    for idx, (team_id, team) in enumerate(teams_to_train, start=1):
        if progress_callback:
            progress_callback(idx, len(teams_to_train))
        
        features = team["selected_features"]
        print(f"\n[{idx}/{len(teams_to_train)}] Trainiere {team['name']} mit Features: {features}")
        
        try:
            # Features extrahieren
            X_train_feat = extract_selected_features(X_train, features)
            X_test_feat = extract_selected_features(X_test, features)
            
            # Training (feste Parameter für faire Vergleichbarkeit)
            train_result = train_classical(
                X_train_feat.values,
                y_train,
                n_estimators=100,
                max_depth=None,
                random_state=42,
            )
            
            # Evaluation
            eval_result = evaluate_classical(
                train_result["model"],
                X_test_feat,
                y_test,
                class_names=CLASS_NAMES,
            )
            
            # Speichern
            with _STATE_LOCK:
                _STATE["results"][team_id] = {
                    "f1_macro": eval_result["f1_macro"],
                    "accuracy": eval_result["accuracy"],
                    "confusion_matrix": eval_result["confusion_matrix"],
                    "feature_importances": eval_result["feature_importances"],
                    "feature_names": eval_result["feature_names"],
                    "train_time": train_result["train_time"],
                }
            
            print(f"  ✓ F1={eval_result['f1_macro']:.4f}, Acc={eval_result['accuracy']:.4f}")
        
        except Exception as e:
            print(f"  ⚠ Fehler beim Training von {team['name']}: {e}")
            with _STATE_LOCK:
                _STATE["results"][team_id] = {
                    "f1_macro": 0.0,
                    "accuracy": 0.0,
                    "confusion_matrix": np.zeros((4, 4)),
                    "feature_importances": np.zeros(4),
                    "feature_names": features,
                    "train_time": 0.0,
                    "error": str(e),
                }
    
    # Speichern
    _save_state_to_disk()
    print(f"\n✓ Training abgeschlossen für {len(teams_to_train)} Teams.")


def train_optimal_model(X_train, y_train, X_test, y_test):
    """
    Trainiert ein Modell mit ALLEN 12 Features als Benchmark.
    
    Speichert das Ergebnis in _STATE["optimal_result"].
    """
    print("\n🔬 Trainiere optimales Modell (alle 12 Features)...")
    
    from src.features import extract_all_features
    
    X_train_feat = extract_all_features(X_train)
    X_test_feat = extract_all_features(X_test)
    
    train_result = train_classical(
        X_train_feat.values,
        y_train,
        n_estimators=100,
        max_depth=None,
        random_state=42,
    )
    
    eval_result = evaluate_classical(
        train_result["model"],
        X_test_feat,
        y_test,
        class_names=CLASS_NAMES,
    )
    
    with _STATE_LOCK:
        _STATE["optimal_result"] = {
            "f1_macro": float(eval_result["f1_macro"]),
            "accuracy": float(eval_result["accuracy"]),
            "feature_importances": eval_result["feature_importances"].tolist(),
            "feature_names": eval_result["feature_names"],
            "train_time": float(train_result["train_time"]),
        }
        _save_state_to_disk()
    
    print(f"✓ Optimales Modell: F1={eval_result['f1_macro']:.4f}, Acc={eval_result['accuracy']:.4f}")


def get_leaderboard() -> list[dict]:
    """
    Gibt eine sortierte Leaderboard-Liste zurück (absteigend nach F1-Score).
    
    Returns:
        Liste von Dictionaries mit:
            - rank: Platzierung (1, 2, 3, ...)
            - team_id
            - team_name
            - f1_macro
            - accuracy
            - train_time
    """
    with _STATE_LOCK:
        entries = []
        for team_id, result in _STATE["results"].items():
            team = _STATE["teams"].get(team_id)
            if team is None:
                continue
            
            entries.append({
                "team_id": team_id,
                "team_name": team["name"],
                "f1_macro": result["f1_macro"],
                "accuracy": result["accuracy"],
                "train_time": result["train_time"],
            })
    
    # Sortieren: F1 absteigend, bei Gleichstand Accuracy absteigend
    entries.sort(key=lambda x: (x["f1_macro"], x["accuracy"]), reverse=True)
    
    # Rang hinzufügen
    for i, entry in enumerate(entries, start=1):
        entry["rank"] = i
    
    return entries


def get_team_result(team_id: str) -> dict | None:
    """Gibt das Ergebnis eines Teams zurück oder None."""
    with _STATE_LOCK:
        return _STATE["results"].get(team_id)


def get_optimal_result() -> dict | None:
    """Gibt das optimale Ergebnis (alle 12 Features) zurück."""
    with _STATE_LOCK:
        return _STATE.get("optimal_result")


def reset():
    """
    Setzt die Challenge komplett zurück (neues Spiel).
    
    WARNUNG: Alle Teams und Ergebnisse werden gelöscht!
    """
    with _STATE_LOCK:
        _STATE["phase"] = "registration"
        _STATE["teams"] = {}
        _STATE["results"] = {}
        _STATE["optimal_result"] = None
        _save_state_to_disk()
    
    print("✓ Challenge wurde zurückgesetzt.")


def get_submission_status() -> dict:
    """
    Gibt einen Überblick über den Submission-Status zurück.
    
    Returns:
        {
            "total_teams": 8,
            "submitted": 5,
            "pending": 3,
            "percentage": 62.5
        }
    """
    with _STATE_LOCK:
        total = len(_STATE["teams"])
        submitted = sum(1 for t in _STATE["teams"].values() if t["submitted"])
        pending = total - submitted
        percentage = (submitted / total * 100) if total > 0 else 0.0
        
        return {
            "total_teams": total,
            "submitted": submitted,
            "pending": pending,
            "percentage": percentage,
        }
