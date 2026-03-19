"""
data_loader.py — Laden und Vorverarbeiten des CWRU Bearing Datasets
===================================================================

Dieses Modul liest die .mat-Dateien des CWRU Bearing Datasets ein,
segmentiert die langen Vibrationssignale in Fenster fester Länge und
bereitet die Daten für das Training von ML- und DL-Modellen vor.

CWRU-Dataset: https://www.kaggle.com/datasets/brjapon/cwru-bearing-datasets/data
"""

import os
import re
import numpy as np
from scipy.io import loadmat
from sklearn.model_selection import train_test_split


# ============================================================
# Klassen-Mapping: Dateinamen → Fehlerkategorie
# ============================================================
#
# Die Dateien im CWRU-Dataset folgen einem Namensschema:
#   - "Normal" / "normal"  → Gesunder Zustand
#   - "IR"                 → Innenringfehler (Inner Race)
#   - "OR"                 → Außenringfehler (Outer Race)
#   - "B"                  → Kugelfehler (Ball)
#
# Fehlerdurchmesser: 0.007, 0.014, 0.021 Zoll
# Motorlasten: 0, 1, 2, 3 HP

LABEL_MAP = {
    "Normal": 0,
    "IR": 1,       # Innenringfehler
    "OR": 2,       # Außenringfehler
    "B": 3,        # Kugelfehler
}

LABEL_NAMES = {
    0: "Normal",
    1: "Innenring (IR)",
    2: "Außenring (OR)",
    3: "Kugel (B)",
}

CLASS_NAMES = ["Normal", "Innenring (IR)", "Außenring (OR)", "Kugel (B)"]


def _detect_label_from_filename(filename: str) -> int | None:
    """
    Erkennt die Fehlerklasse anhand des Dateinamens.

    Beispiele:
        "Normal_0.mat"  → 0
        "IR007_0.mat"   → 1
        "OR014@6_0.mat" → 2
        "B021_0.mat"    → 3

    Returns:
        int (Label) oder None, falls nicht zuordenbar.
    """
    name = os.path.splitext(filename)[0].upper()

    if "NORMAL" in name:
        return 0
    elif "IR" in name:
        return 1
    elif "OR" in name:
        return 2
    elif name.startswith("B") or "_B" in name:
        return 3
    return None


def _extract_de_signal(mat_data: dict) -> np.ndarray | None:
    """
    Extrahiert das Drive-End-Beschleunigungssignal aus einer .mat-Datei.

    Der CWRU-Dataset speichert die Signale unter verschiedenen Schlüsseln,
    z.B. 'X097_DE_time', 'X105_DE_time', etc. Diese Funktion sucht
    automatisch den richtigen Schlüssel.

    Returns:
        1D numpy-Array mit dem Vibrationssignal oder None.
    """
    for key in mat_data:
        if "DE_time" in key:
            signal = mat_data[key].flatten()
            return signal
    # Fallback: Versuche beliebige numerische Spalte
    for key in mat_data:
        if not key.startswith("__"):
            val = mat_data[key]
            if hasattr(val, "shape") and val.ndim >= 1 and val.size > 1000:
                return val.flatten()
    return None


def load_mat_files(data_dir: str) -> list[dict]:
    """
    Lädt alle .mat-Dateien aus dem angegebenen Verzeichnis (rekursiv).

    Returns:
        Liste von Dictionaries:
        [
            {
                "filename": "IR007_0.mat",
                "label": 1,
                "label_name": "Innenring (IR)",
                "signal": np.array([...]),   # 1D float64
                "length": 121265,
            },
            ...
        ]
    """
    records = []
    if not os.path.isdir(data_dir):
        raise FileNotFoundError(
            f"Datenverzeichnis nicht gefunden: {data_dir}\n"
            f"Bitte laden Sie den CWRU-Dataset von Kaggle herunter und "
            f"entpacken Sie die .mat-Dateien in diesen Ordner."
        )

    for root, _, files in os.walk(data_dir):
        for fname in sorted(files):
            if not fname.endswith(".mat"):
                continue

            label = _detect_label_from_filename(fname)
            if label is None:
                print(f"⚠ Überspringe (unbekanntes Label): {fname}")
                continue

            filepath = os.path.join(root, fname)
            try:
                mat = loadmat(filepath)
            except Exception as e:
                print(f"⚠ Fehler beim Laden von {fname}: {e}")
                continue

            signal = _extract_de_signal(mat)
            if signal is None:
                print(f"⚠ Kein DE-Signal gefunden in: {fname}")
                continue

            records.append({
                "filename": fname,
                "label": label,
                "label_name": LABEL_NAMES[label],
                "signal": signal.astype(np.float64),
                "length": len(signal),
            })

    if not records:
        raise ValueError(
            f"Keine gültigen .mat-Dateien in {data_dir} gefunden.\n"
            f"Stellen Sie sicher, dass die CWRU-Dateien dort liegen."
        )

    print(f"✓ {len(records)} Dateien geladen:")
    for lbl, name in LABEL_NAMES.items():
        count = sum(1 for r in records if r["label"] == lbl)
        print(f"  {name}: {count} Dateien")

    return records


# ============================================================
# Segmentierung
# ============================================================

def segment_signals(
    records: list[dict],
    segment_length: int = 1024,
    overlap: float = 0.5,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Segmentiert die langen Vibrationssignale in Fenster fester Länge.

    Parameter:
        records:        Ausgabe von load_mat_files()
        segment_length: Anzahl Samples pro Segment (Standard: 1024)
        overlap:        Überlappung zwischen Segmenten (0.0 bis <1.0)

    Returns:
        X: np.ndarray der Form (N, segment_length) — Segmente
        y: np.ndarray der Form (N,)                — Labels
    """
    step = int(segment_length * (1 - overlap))
    if step < 1:
        step = 1

    segments = []
    labels = []

    for rec in records:
        signal = rec["signal"]
        label = rec["label"]
        n_samples = len(signal)

        start = 0
        while start + segment_length <= n_samples:
            segment = signal[start : start + segment_length]
            segments.append(segment)
            labels.append(label)
            start += step

    X = np.array(segments, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)

    print(f"✓ {len(X)} Segmente erzeugt (Länge={segment_length}, Überlappung={overlap*100:.0f}%)")
    for lbl, name in LABEL_NAMES.items():
        count = np.sum(y == lbl)
        print(f"  {name}: {count} Segmente")

    return X, y


# ============================================================
# Normalisierung
# ============================================================

def normalize_segments(X: np.ndarray) -> np.ndarray:
    """
    Z-Score-Normalisierung pro Segment (Mittelwert=0, Std=1).

    Jedes Segment wird individuell normalisiert, damit unterschiedliche
    Amplitudenniveaus (z.B. durch Sensorplatzierung) ausgeglichen werden.
    """
    mean = X.mean(axis=1, keepdims=True)
    std = X.std(axis=1, keepdims=True)
    std[std == 0] = 1.0  # Division durch Null vermeiden
    return (X - mean) / std


# ============================================================
# Kompletter Daten-Pipeline-Aufruf
# ============================================================

def prepare_dataset(
    data_dir: str,
    segment_length: int = 1024,
    overlap: float = 0.5,
    test_size: float = 0.2,
    normalize: bool = True,
    random_state: int = 42,
) -> dict:
    """
    Kompletter Pipeline-Aufruf: Laden → Segmentieren → Normalisieren → Split.

    Returns:
        Dictionary mit:
            X_train, X_test : np.ndarray (N, segment_length)
            y_train, y_test : np.ndarray (N,)
            records         : Rohdaten-Einträge
            class_names     : Liste der Klassennamen
    """
    # 1. Laden
    records = load_mat_files(data_dir)

    # 2. Segmentieren
    X, y = segment_signals(records, segment_length, overlap)

    # 3. Normalisieren
    if normalize:
        X = normalize_segments(X)
        print("✓ Z-Score-Normalisierung angewendet")

    # 4. Train/Test-Split (stratifiziert)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
    print(f"✓ Train/Test-Split: {len(X_train)} Training, {len(X_test)} Test")

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "records": records,
        "class_names": CLASS_NAMES,
    }


# ============================================================
# Demo-Daten (synthetisch) — für Tests ohne echten Dataset
# ============================================================

def generate_demo_data(
    n_per_class: int = 500,
    segment_length: int = 1024,
    noise_level: float = 0.3,
    normalize: bool = True,
    random_state: int = 42,
) -> dict:
    """
    Erzeugt synthetische Demo-Daten, die echten Wälzlager-Signalen ähneln.

    Dies ermöglicht es, die gesamte Pipeline zu demonstrieren, auch wenn
    der echte CWRU-Dataset noch nicht heruntergeladen wurde.

    Die vier Klassen werden durch unterschiedliche Signalmuster simuliert:
    - Normal:     Niederfrequentes Rauschen
    - Innenring:  Periodische Impulse mit hoher Frequenz
    - Außenring:  Periodische Impulse mit mittlerer Frequenz
    - Kugel:      Unregelmäßige Impulse mit variabler Amplitude

    Returns:
        Gleiches Format wie prepare_dataset()
    """
    rng = np.random.RandomState(random_state)
    t = np.linspace(0, 1, segment_length)
    fs = 12000  # Abtastrate wie im CWRU-Dataset

    segments = []
    labels = []

    for _ in range(n_per_class):
        # ---- Normal: Grundrauschen + leichte Vibration ----
        sig = 0.1 * np.sin(2 * np.pi * 30 * t)
        sig += noise_level * rng.randn(segment_length)
        segments.append(sig)
        labels.append(0)

        # ---- Innenring: Periodische Impulse (BPFI ~ 160 Hz) ----
        sig = 0.1 * np.sin(2 * np.pi * 30 * t)
        impulse_freq = 160 + rng.uniform(-10, 10)
        impulse_times = np.arange(0, 1, 1 / impulse_freq)
        for it in impulse_times:
            idx = int(it * segment_length)
            if idx < segment_length - 20:
                amplitude = 0.8 + rng.uniform(-0.2, 0.2)
                decay = np.exp(-np.arange(20) * 0.3)
                sig[idx:idx+20] += amplitude * decay * np.sin(
                    2 * np.pi * 3000 * np.arange(20) / fs
                )
        sig += noise_level * rng.randn(segment_length)
        segments.append(sig)
        labels.append(1)

        # ---- Außenring: Periodische Impulse (BPFO ~ 105 Hz) ----
        sig = 0.1 * np.sin(2 * np.pi * 30 * t)
        impulse_freq = 105 + rng.uniform(-10, 10)
        impulse_times = np.arange(0, 1, 1 / impulse_freq)
        for it in impulse_times:
            idx = int(it * segment_length)
            if idx < segment_length - 25:
                amplitude = 1.0 + rng.uniform(-0.3, 0.3)
                decay = np.exp(-np.arange(25) * 0.25)
                sig[idx:idx+25] += amplitude * decay * np.sin(
                    2 * np.pi * 2000 * np.arange(25) / fs
                )
        sig += noise_level * rng.randn(segment_length)
        segments.append(sig)
        labels.append(2)

        # ---- Kugel: Unregelmäßige Impulse (BSF ~ 140 Hz) ----
        sig = 0.1 * np.sin(2 * np.pi * 30 * t)
        n_impulses = rng.randint(8, 20)
        impulse_positions = rng.uniform(0, 1, n_impulses)
        for ip in impulse_positions:
            idx = int(ip * segment_length)
            width = rng.randint(10, 30)
            if idx < segment_length - width:
                amplitude = rng.uniform(0.3, 1.2)
                decay = np.exp(-np.arange(width) * rng.uniform(0.15, 0.4))
                freq = rng.uniform(1500, 4000)
                sig[idx:idx+width] += amplitude * decay * np.sin(
                    2 * np.pi * freq * np.arange(width) / fs
                )
        sig += noise_level * rng.randn(segment_length)
        segments.append(sig)
        labels.append(3)

    X = np.array(segments, dtype=np.float32)
    y = np.array(labels, dtype=np.int32)

    # Optional normalisieren
    if normalize:
        X = normalize_segments(X)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    print(f"✓ Demo-Daten erzeugt: {len(X_train)} Training, {len(X_test)} Test")

    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "records": None,
        "class_names": CLASS_NAMES,
    }
