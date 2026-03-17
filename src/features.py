"""
features.py — Feature-Extraktion für Vibrationssignale
======================================================

Dieses Modul berechnet Zeit- und Frequenzbereich-Features aus den
segmentierten Vibrationssignalen. Diese Features dienen als Eingabe
für klassische ML-Algorithmen (z.B. Random Forest).

Zeitbereich-Features (8):
    1. RMS (Root Mean Square)        — Effektivwert
    2. Standardabweichung            — Streuung
    3. Kurtosis                      — Wölbung (Spitzigkeit)
    4. Schiefe (Skewness)            — Asymmetrie
    5. Peak-to-Peak                  — Spitze-zu-Spitze-Wert
    6. Scheitelfaktor (Crest Factor) — Verhältnis Spitzenwert / RMS
    7. Formfaktor (Shape Factor)     — Verhältnis RMS / Mittelwert(|x|)
    8. Impulsfaktor (Impulse Factor) — Verhältnis Spitzenwert / Mittelwert(|x|)

Frequenzbereich-Features (4):
    9.  Spektraler Schwerpunkt       — Mittlere Frequenz (gewichtet)
    10. Spektrale Bandbreite         — Streuung im Frequenzbereich
    11. Dominante Frequenz           — Frequenz mit max. Amplitude
    12. Mittlere Frequenz            — Schwerpunkt des Leistungsspektrums
"""

import numpy as np
import pandas as pd
from scipy.stats import kurtosis, skew


# ============================================================
# Zeitbereich-Features
# ============================================================

def rms(x: np.ndarray) -> float:
    r"""
    Root Mean Square (Effektivwert).

    $$x_{\text{RMS}} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} x_i^2}$$

    Misst die durchschnittliche Signalenergie.
    Erhöhte Werte deuten auf stärkere Vibrationen hin.
    """
    return np.sqrt(np.mean(x ** 2))


def std_dev(x: np.ndarray) -> float:
    r"""
    Standardabweichung.

    $$\sigma = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (x_i - \bar{x})^2}$$

    Misst die Streuung des Signals um den Mittelwert.
    """
    return np.std(x)


def kurtosis_value(x: np.ndarray) -> float:
    r"""
    Kurtosis (Wölbung / Spitzigkeit).

    $$\kappa = \frac{\frac{1}{N} \sum_{i=1}^{N} (x_i - \bar{x})^4}{\sigma^4}$$

    Misst, wie "spitz" die Verteilung ist.
    Hohe Kurtosis → impulsive Signale → typisch für Lagerschäden.
    (Fisher-Definition: Normalverteilung hat Kurtosis ≈ 0)
    """
    return kurtosis(x, fisher=True)


def skewness_value(x: np.ndarray) -> float:
    r"""
    Schiefe (Skewness).

    $$\gamma = \frac{\frac{1}{N} \sum_{i=1}^{N} (x_i - \bar{x})^3}{\sigma^3}$$

    Misst die Asymmetrie der Signalverteilung.
    """
    return skew(x)


def peak_to_peak(x: np.ndarray) -> float:
    r"""
    Peak-to-Peak (Spitze-zu-Spitze-Wert).

    $$x_{p2p} = x_{\max} - x_{\min}$$

    Maximale Schwingungsbreite des Signals.
    """
    return np.max(x) - np.min(x)


def crest_factor(x: np.ndarray) -> float:
    r"""
    Scheitelfaktor (Crest Factor).

    $$CF = \frac{|x|_{\max}}{x_{\text{RMS}}}$$

    Verhältnis von Spitzenwert zu Effektivwert.
    Hoher Scheitelfaktor → vereinzelte starke Ausschläge.
    """
    x_rms = rms(x)
    if x_rms == 0:
        return 0.0
    return np.max(np.abs(x)) / x_rms


def shape_factor(x: np.ndarray) -> float:
    r"""
    Formfaktor (Shape Factor).

    $$SF = \frac{x_{\text{RMS}}}{\frac{1}{N} \sum |x_i|}$$

    Verhältnis von RMS zum mittleren Absolutwert.
    Für eine Sinuswelle: SF ≈ 1.11, für Impulse höher.
    """
    mean_abs = np.mean(np.abs(x))
    if mean_abs == 0:
        return 0.0
    return rms(x) / mean_abs


def impulse_factor(x: np.ndarray) -> float:
    r"""
    Impulsfaktor (Impulse Factor).

    $$IF = \frac{|x|_{\max}}{\frac{1}{N} \sum |x_i|}$$

    Verhältnis von Spitzenwert zum mittleren Absolutwert.
    Sehr sensitiv gegenüber impulsiven Fehlersignalen.
    """
    mean_abs = np.mean(np.abs(x))
    if mean_abs == 0:
        return 0.0
    return np.max(np.abs(x)) / mean_abs


# ============================================================
# Frequenzbereich-Features
# ============================================================

def _compute_spectrum(x: np.ndarray, fs: float = 12000.0):
    """
    Berechnet das einseitige Amplitudenspektrum via FFT.

    Returns:
        freqs:  Frequenzvektor (Hz)
        magnitude: Amplitudenspektrum (normalisiert)
    """
    N = len(x)
    fft_vals = np.fft.rfft(x)
    magnitude = np.abs(fft_vals) * 2.0 / N
    freqs = np.fft.rfftfreq(N, d=1.0 / fs)
    return freqs, magnitude


def spectral_centroid(x: np.ndarray, fs: float = 12000.0) -> float:
    r"""
    Spektraler Schwerpunkt (Spectral Centroid).

    $$f_c = \frac{\sum f_i \cdot |X(f_i)|}{\sum |X(f_i)|}$$

    Die "mittlere" Frequenz, gewichtet nach Amplitude.
    Verschiebt sich bei Lagerschäden zu höheren Frequenzen.
    """
    freqs, mag = _compute_spectrum(x, fs)
    total = np.sum(mag)
    if total == 0:
        return 0.0
    return np.sum(freqs * mag) / total


def spectral_bandwidth(x: np.ndarray, fs: float = 12000.0) -> float:
    r"""
    Spektrale Bandbreite (Spectral Spread).

    $$BW = \sqrt{\frac{\sum (f_i - f_c)^2 \cdot |X(f_i)|}{\sum |X(f_i)|}}$$

    Streuung der Frequenzkomponenten um den Schwerpunkt.
    Breitere Bandbreite → mehr Frequenzkomponenten → komplexeres Signal.
    """
    freqs, mag = _compute_spectrum(x, fs)
    total = np.sum(mag)
    if total == 0:
        return 0.0
    fc = np.sum(freqs * mag) / total
    return np.sqrt(np.sum(((freqs - fc) ** 2) * mag) / total)


def dominant_frequency(x: np.ndarray, fs: float = 12000.0) -> float:
    r"""
    Dominante Frequenz.

    $$f_{\text{dom}} = \arg\max_{f_i} |X(f_i)|$$

    Die Frequenz mit der höchsten Amplitude im Spektrum.
    """
    freqs, mag = _compute_spectrum(x, fs)
    if len(mag) == 0:
        return 0.0
    return freqs[np.argmax(mag)]


def mean_frequency(x: np.ndarray, fs: float = 12000.0) -> float:
    r"""
    Mittlere Frequenz (Mean Frequency).

    $$f_{\text{mean}} = \frac{\sum f_i \cdot S(f_i)}{\sum S(f_i)}$$

    wobei $S(f_i) = |X(f_i)|^2$ das Leistungsspektrum ist.
    """
    freqs, mag = _compute_spectrum(x, fs)
    power = mag ** 2
    total = np.sum(power)
    if total == 0:
        return 0.0
    return np.sum(freqs * power) / total


# ============================================================
# Feature-Extraktion für eine Menge von Segmenten
# ============================================================

# Alle verfügbaren Features als geordnete Liste
FEATURE_FUNCTIONS = [
    ("RMS", rms),
    ("Standardabweichung", std_dev),
    ("Kurtosis", kurtosis_value),
    ("Schiefe", skewness_value),
    ("Peak-to-Peak", peak_to_peak),
    ("Scheitelfaktor", crest_factor),
    ("Formfaktor", shape_factor),
    ("Impulsfaktor", impulse_factor),
    ("Spektraler Schwerpunkt", spectral_centroid),
    ("Spektrale Bandbreite", spectral_bandwidth),
    ("Dominante Frequenz", dominant_frequency),
    ("Mittlere Frequenz", mean_frequency),
]

FEATURE_NAMES = [name for name, _ in FEATURE_FUNCTIONS]


def extract_features_single(segment: np.ndarray) -> np.ndarray:
    """
    Berechnet alle 12 Features für ein einzelnes Segment.

    Parameter:
        segment: 1D-Array der Länge segment_length

    Returns:
        1D-Array mit 12 Feature-Werten
    """
    return np.array([func(segment) for _, func in FEATURE_FUNCTIONS], dtype=np.float64)


def extract_all_features(X: np.ndarray) -> pd.DataFrame:
    """
    Berechnet alle 12 Features für eine Menge von Segmenten.

    Parameter:
        X: np.ndarray der Form (N, segment_length)

    Returns:
        pandas DataFrame mit N Zeilen und 12 Feature-Spalten
    """
    n_samples = X.shape[0]
    features = np.zeros((n_samples, len(FEATURE_FUNCTIONS)), dtype=np.float64)

    for i in range(n_samples):
        features[i] = extract_features_single(X[i])

    df = pd.DataFrame(features, columns=FEATURE_NAMES)

    print(f"✓ {len(FEATURE_NAMES)} Features für {n_samples} Segmente berechnet")
    return df


def extract_selected_features(
    X: np.ndarray,
    selected_features: list[str] | None = None,
) -> pd.DataFrame:
    """
    Berechnet nur ausgewählte Features.

    Parameter:
        X: np.ndarray der Form (N, segment_length)
        selected_features: Liste von Feature-Namen (None = alle)

    Returns:
        pandas DataFrame mit den ausgewählten Feature-Spalten
    """
    if selected_features is None:
        return extract_all_features(X)

    valid = {name: func for name, func in FEATURE_FUNCTIONS}
    selected_funcs = []
    for name in selected_features:
        if name not in valid:
            raise ValueError(f"Unbekanntes Feature: '{name}'. Verfügbar: {FEATURE_NAMES}")
        selected_funcs.append((name, valid[name]))

    n_samples = X.shape[0]
    features = np.zeros((n_samples, len(selected_funcs)), dtype=np.float64)

    for i in range(n_samples):
        for j, (_, func) in enumerate(selected_funcs):
            features[i, j] = func(X[i])

    df = pd.DataFrame(features, columns=[n for n, _ in selected_funcs])
    print(f"✓ {len(selected_funcs)} Features für {n_samples} Segmente berechnet")
    return df
