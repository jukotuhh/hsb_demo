"""
cnn_model.py — 1D Convolutional Neural Network für Vibrationssignale
====================================================================

Dieses Modul implementiert ein einfaches 1D-CNN mit Keras/TensorFlow
für die automatische Fehlerdiagnose aus rohen Vibrationssignalen.

Der entscheidende Vorteil gegenüber dem klassischen ML-Ansatz:
→ Keine manuelle Feature-Extraktion nötig!
→ Das CNN lernt die relevanten Merkmale selbst aus den Rohdaten.

Architektur:
    Input (1024, 1) — rohes Vibrationssegment
        │
        ├─ Conv1D(32, kernel=7) → BatchNorm → ReLU → MaxPool(2)
        ├─ Conv1D(64, kernel=5) → BatchNorm → ReLU → MaxPool(2)
        ├─ Conv1D(128, kernel=3) → BatchNorm → ReLU → MaxPool(2)
        │
        ├─ GlobalAveragePooling1D
        ├─ Dense(64) → ReLU → Dropout(0.5)
        └─ Dense(4, Softmax) → Ausgabe: Wahrscheinlichkeiten pro Klasse

Die Schichten im Detail:
    - Conv1D-Schichten:  Erkennen lokale Muster (wie handgemachte Features,
                         aber automatisch gelernt)
    - BatchNorm:         Stabilisiert das Training
    - MaxPooling:        Reduziert die Dimensionalität, macht das Modell
                         robuster gegenüber kleinen Verschiebungen
    - GlobalAvgPooling:  Fasst alle gelernten Merkmale zusammen
    - Dropout:           Verhindert Overfitting (zufälliges Deaktivieren
                         von Neuronen während des Trainings)
"""

import os
import time
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score


def build_cnn(
    input_length: int = 1024,
    num_classes: int = 4,
) -> keras.Model:
    """
    Erstellt ein einfaches 1D-CNN für die Vibrationssignalklassifikation.

    Parameter:
        input_length: Länge eines Eingabesegments (Standard: 1024)
        num_classes:  Anzahl der Klassen (Standard: 4)

    Returns:
        Kompiliertes Keras-Modell
    """
    model = keras.Sequential([
        # --- Eingabe ---
        layers.Input(shape=(input_length, 1)),

        # --- Block 1: Grobe Muster erkennen ---
        layers.Conv1D(filters=32, kernel_size=7, padding="same"),
        layers.BatchNormalization(),
        layers.Activation("relu"),
        layers.MaxPooling1D(pool_size=2),

        # --- Block 2: Feinere Muster ---
        layers.Conv1D(filters=64, kernel_size=5, padding="same"),
        layers.BatchNormalization(),
        layers.Activation("relu"),
        layers.MaxPooling1D(pool_size=2),

        # --- Block 3: Komplexe Muster ---
        layers.Conv1D(filters=128, kernel_size=3, padding="same"),
        layers.BatchNormalization(),
        layers.Activation("relu"),
        layers.MaxPooling1D(pool_size=2),

        # --- Klassifikation ---
        layers.GlobalAveragePooling1D(),
        layers.Dense(64, activation="relu"),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation="softmax"),
    ])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model


def get_model_summary(model: keras.Model) -> str:
    """Gibt die Modell-Zusammenfassung als String zurück."""
    lines = []
    model.summary(print_fn=lambda x: lines.append(x))
    return "\n".join(lines)


def train_cnn(
    model: keras.Model,
    X_train: np.ndarray,
    y_train: np.ndarray,
    epochs: int = 20,
    batch_size: int = 64,
    validation_split: float = 0.15,
    verbose: int = 1,
) -> dict:
    """
    Trainiert das 1D-CNN.

    Parameter:
        model:            Kompiliertes Keras-Modell (von build_cnn())
        X_train:          Trainingsdaten (N, segment_length)
        y_train:          Labels (N,)
        epochs:           Anzahl Trainingsepochen
        batch_size:       Batch-Größe
        validation_split: Anteil der Trainingsdaten für Validierung
        verbose:          Ausgabelevel (0=still, 1=Fortschrittsbalken, 2=pro Epoche)

    Returns:
        Dictionary mit:
            history:      Keras-History-Objekt (Loss/Accuracy pro Epoche)
            train_time:   Trainingszeit in Sekunden
    """
    # CNN erwartet 3D-Input: (N, length, 1)
    if X_train.ndim == 2:
        X_train = X_train[..., np.newaxis]

    start_time = time.time()

    # Early Stopping: Training stoppen, wenn Validierungs-Loss nicht mehr sinkt
    early_stop = keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=5,
        restore_best_weights=True,
        verbose=1,
    )

    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_split=validation_split,
        callbacks=[early_stop],
        verbose=verbose,
    )

    train_time = time.time() - start_time
    print(f"\n✓ CNN-Training abgeschlossen in {train_time:.1f}s")
    print(f"  Letzte Epoche — Loss: {history.history['loss'][-1]:.4f}, "
          f"Accuracy: {history.history['accuracy'][-1]:.4f}")

    return {
        "history": history,
        "train_time": train_time,
    }


def evaluate_cnn(
    model: keras.Model,
    X_test: np.ndarray,
    y_test: np.ndarray,
    class_names: list[str] | None = None,
) -> dict:
    """
    Evaluiert das CNN auf den Testdaten.

    Returns:
        Dictionary mit:
            accuracy:       Test-Accuracy
            f1_macro:       Macro-averaged F1-Score
            confusion_matrix: Konfusionsmatrix
            classification_report: Textbericht
            y_pred:         Vorhersagen
            y_prob:         Wahrscheinlichkeiten pro Klasse
    """
    # CNN erwartet 3D-Input
    if X_test.ndim == 2:
        X_test = X_test[..., np.newaxis]

    # Vorhersagen
    y_prob = model.predict(X_test, verbose=0)
    y_pred = np.argmax(y_prob, axis=1)

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")
    cm = confusion_matrix(y_test, y_pred)
    report = classification_report(
        y_test, y_pred,
        target_names=class_names,
        digits=4,
    )

    print(f"✓ CNN-Evaluation auf Testdaten:")
    print(f"  Test-Accuracy: {acc:.4f}")
    print(f"  F1-Score:      {f1:.4f}")
    print(f"\n{report}")

    return {
        "accuracy": acc,
        "f1_macro": f1,
        "confusion_matrix": cm,
        "classification_report": report,
        "y_pred": y_pred,
        "y_prob": y_prob,
    }


def save_cnn(model: keras.Model, filepath: str) -> None:
    """Speichert das trainierte CNN."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    model.save(filepath)
    print(f"✓ CNN gespeichert: {filepath}")


def load_cnn(filepath: str) -> keras.Model:
    """Lädt ein gespeichertes CNN."""
    model = keras.models.load_model(filepath)
    print(f"✓ CNN geladen: {filepath}")
    return model
