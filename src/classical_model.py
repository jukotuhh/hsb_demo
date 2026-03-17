"""
classical_model.py — Klassisches ML mit Random Forest
=====================================================

Dieses Modul implementiert eine klassische ML-Pipeline für die
Wälzlager-Fehlerdiagnose:

    Extrahierte Features → StandardScaler → Random Forest → Klassifikation

Der Random Forest ist ideal für die Lehre, weil:
- Er aus vielen Entscheidungsbäumen besteht (intuitiv verständlich)
- Feature Importances berechnet werden können
- Kein aufwändiges Hyperparameter-Tuning nötig ist
- Er robust gegenüber Ausreißern und nicht-linearen Zusammenhängen ist
"""

import os
import time
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)


def build_classical_pipeline(
    n_estimators: int = 100,
    max_depth: int | None = None,
    random_state: int = 42,
) -> Pipeline:
    """
    Erstellt eine sklearn-Pipeline: StandardScaler → RandomForest.

    Parameter:
        n_estimators: Anzahl der Entscheidungsbäume
        max_depth:    Maximale Tiefe der Bäume (None = unbegrenzt)
        random_state: Zufallsseed für Reproduzierbarkeit

    Returns:
        sklearn Pipeline-Objekt
    """
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1,  # Alle CPU-Kerne nutzen
        )),
    ])
    return pipeline


def train_classical(
    X_train_features: pd.DataFrame | np.ndarray,
    y_train: np.ndarray,
    n_estimators: int = 100,
    max_depth: int | None = None,
    random_state: int = 42,
) -> dict:
    """
    Trainiert die klassische ML-Pipeline.

    Parameter:
        X_train_features: Feature-Matrix (N, 12) — Ausgabe von extract_all_features()
        y_train:          Labels (N,)
        n_estimators:     Anzahl der Entscheidungsbäume
        max_depth:        Maximale Tiefe
        random_state:     Zufallsseed

    Returns:
        Dictionary mit:
            model:         Trainierte Pipeline
            train_time:    Trainingszeit in Sekunden
            train_accuracy: Genauigkeit auf Trainingsdaten
    """
    if isinstance(X_train_features, pd.DataFrame):
        X = X_train_features.values
    else:
        X = X_train_features

    pipeline = build_classical_pipeline(n_estimators, max_depth, random_state)

    start_time = time.time()
    pipeline.fit(X, y_train)
    train_time = time.time() - start_time

    y_pred_train = pipeline.predict(X)
    train_accuracy = accuracy_score(y_train, y_pred_train)

    print(f"✓ Random Forest trainiert ({n_estimators} Bäume)")
    print(f"  Trainingszeit:     {train_time:.2f}s")
    print(f"  Training-Accuracy: {train_accuracy:.4f}")

    return {
        "model": pipeline,
        "train_time": train_time,
        "train_accuracy": train_accuracy,
    }


def evaluate_classical(
    model: Pipeline,
    X_test_features: pd.DataFrame | np.ndarray,
    y_test: np.ndarray,
    class_names: list[str] | None = None,
) -> dict:
    """
    Evaluiert das trainierte Modell auf den Testdaten.

    Returns:
        Dictionary mit:
            accuracy:       Test-Accuracy
            f1_macro:       Macro-averaged F1-Score
            confusion_matrix: Konfusionsmatrix (np.ndarray)
            classification_report: Textbericht
            y_pred:         Vorhersagen
            feature_importances: Feature-Wichtigkeiten (np.ndarray)
            feature_names:  Feature-Namen (falls DataFrame)
    """
    if isinstance(X_test_features, pd.DataFrame):
        feature_names = list(X_test_features.columns)
        X = X_test_features.values
    else:
        X = X_test_features
        feature_names = [f"Feature {i}" for i in range(X.shape[1])]

    y_pred = model.predict(X)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(
        y_test, y_pred,
        target_names=class_names,
        digits=4,
    )

    # Feature Importances aus dem Random Forest extrahieren
    rf = model.named_steps["classifier"]
    importances = rf.feature_importances_

    print(f"✓ Evaluation auf Testdaten:")
    print(f"  Test-Accuracy: {acc:.4f}")
    print(f"  F1-Score:      {f1:.4f}")
    print(f"\n{report}")

    return {
        "accuracy": acc,
        "f1_macro": f1,
        "confusion_matrix": cm,
        "classification_report": report,
        "y_pred": y_pred,
        "feature_importances": importances,
        "feature_names": feature_names,
    }


def save_model(model: Pipeline, filepath: str) -> None:
    """Speichert das trainierte Modell als .pkl-Datei."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    joblib.dump(model, filepath)
    print(f"✓ Modell gespeichert: {filepath}")


def load_model(filepath: str) -> Pipeline:
    """Lädt ein gespeichertes Modell."""
    model = joblib.load(filepath)
    print(f"✓ Modell geladen: {filepath}")
    return model
