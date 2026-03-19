"""
feature_info.py — Feature-Beschreibungen für die Classroom-Challenge
====================================================================

Dieses Modul liefert strukturierte Metadaten zu jedem der 12 Features
aus features.py. Die Informationen werden in der Challenge-App für:
    - Tooltips bei Feature-Karten
    - Info-Expander mit Formeln und Erklärungen
    - Didaktische Hinweise für Studierende

verwendet.

Die Beschreibungen sind direkt aus den Docstrings der Feature-Funktionen
abgeleitet und auf Deutsch formuliert.
"""

from src.features import FEATURE_NAMES


FEATURE_INFO = {
    "RMS": {
        "name_de": "Effektivwert (RMS)",
        "domain": "Zeitbereich",
        "formula": r"x_{\text{RMS}} = \sqrt{\frac{1}{N} \sum_{i=1}^{N} x_i^2}",
        "description": "Misst die durchschnittliche Signalenergie. Erhöhte Werte deuten auf stärkere Vibrationen hin.",
        "intuition": "Je lauter das Lager vibriert, desto höher der RMS.",
        "useful_for": "Unterscheidung Normal ↔ Fehlerhaft",
    },
    
    "Standardabweichung": {
        "name_de": "Standardabweichung",
        "domain": "Zeitbereich",
        "formula": r"\sigma = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (x_i - \bar{x})^2}",
        "description": "Misst die Streuung des Signals um den Mittelwert. Hohe Streuung deutet auf unregelmäßige Vibrationen hin.",
        "intuition": "Wie stark schwankt die Vibration?",
        "useful_for": "Erkennung von Unregelmäßigkeiten",
    },
    
    "Kurtosis": {
        "name_de": "Kurtosis (Wölbung)",
        "domain": "Zeitbereich",
        "formula": r"\kappa = \frac{\frac{1}{N} \sum_{i=1}^{N} (x_i - \bar{x})^4}{\sigma^4}",
        "description": "Misst, wie 'spitz' die Verteilung ist. Hohe Kurtosis → impulsive Signale → typisch für Lagerschäden!",
        "intuition": "Gibt es vereinzelte starke Ausschläge (Impulse)?",
        "useful_for": "Sehr sensitiv für Lagerschäden",
    },
    
    "Schiefe": {
        "name_de": "Schiefe (Skewness)",
        "domain": "Zeitbereich",
        "formula": r"\gamma = \frac{\frac{1}{N} \sum_{i=1}^{N} (x_i - \bar{x})^3}{\sigma^3}",
        "description": "Misst die Asymmetrie der Signalverteilung. Zeigt an, ob das Signal nach oben oder unten verzerrt ist.",
        "intuition": "Ist die Vibration symmetrisch?",
        "useful_for": "Erkennung asymmetrischer Fehler",
    },
    
    "Peak-to-Peak": {
        "name_de": "Peak-to-Peak",
        "domain": "Zeitbereich",
        "formula": r"x_{p2p} = x_{\max} - x_{\min}",
        "description": "Maximale Schwingungsbreite des Signals. Großer Wertebereich deutet auf starke Ausschläge hin.",
        "intuition": "Wie groß ist die maximale Schwingung?",
        "useful_for": "Grobe Amplitudeneinschätzung",
    },
    
    "Scheitelfaktor": {
        "name_de": "Scheitelfaktor (Crest Factor)",
        "domain": "Zeitbereich",
        "formula": r"CF = \frac{|x|_{\max}}{x_{\text{RMS}}}",
        "description": "Verhältnis von Spitzenwert zu Effektivwert. Hoher Scheitelfaktor → vereinzelte starke Ausschläge.",
        "intuition": "Gibt es seltene, aber extreme Spitzen?",
        "useful_for": "Impulserkennung bei Lagerschäden",
    },
    
    "Formfaktor": {
        "name_de": "Formfaktor (Shape Factor)",
        "domain": "Zeitbereich",
        "formula": r"SF = \frac{x_{\text{RMS}}}{\frac{1}{N} \sum |x_i|}",
        "description": "Verhältnis von RMS zum mittleren Absolutwert. Für eine Sinuswelle: SF ≈ 1.11, für Impulse höher.",
        "intuition": "Wie 'glatt' ist die Vibration?",
        "useful_for": "Unterscheidung glatte ↔ impulsive Signale",
    },
    
    "Impulsfaktor": {
        "name_de": "Impulsfaktor (Impulse Factor)",
        "domain": "Zeitbereich",
        "formula": r"IF = \frac{|x|_{\max}}{\frac{1}{N} \sum |x_i|}",
        "description": "Verhältnis von Spitzenwert zum mittleren Absolutwert. Sehr sensitiv gegenüber impulsiven Fehlersignalen.",
        "intuition": "Wie stark stechen Impulse heraus?",
        "useful_for": "Impulserkennung (besonders sensitiv)",
    },
    
    "Spektraler Schwerpunkt": {
        "name_de": "Spektraler Schwerpunkt",
        "domain": "Frequenzbereich",
        "formula": r"f_c = \frac{\sum f_i \cdot |X(f_i)|}{\sum |X(f_i)|}",
        "description": "Die 'mittlere' Frequenz, gewichtet nach Amplitude. Verschiebt sich bei Lagerschäden zu höheren Frequenzen.",
        "intuition": "Wo liegt die durchschnittliche Frequenz?",
        "useful_for": "Erkennung hochfrequenter Fehler",
    },
    
    "Spektrale Bandbreite": {
        "name_de": "Spektrale Bandbreite",
        "domain": "Frequenzbereich",
        "formula": r"BW = \sqrt{\frac{\sum (f_i - f_c)^2 \cdot |X(f_i)|}{\sum |X(f_i)|}}",
        "description": "Streuung der Frequenzkomponenten um den Schwerpunkt. Breitere Bandbreite → mehr Frequenzkomponenten → komplexeres Signal.",
        "intuition": "Wie breit ist das Frequenzspektrum?",
        "useful_for": "Erkennung komplexer Fehlerfrequenzen",
    },
    
    "Dominante Frequenz": {
        "name_de": "Dominante Frequenz",
        "domain": "Frequenzbereich",
        "formula": r"f_{\text{dom}} = \arg\max_{f_i} |X(f_i)|",
        "description": "Die Frequenz mit der höchsten Amplitude im Spektrum. Zeigt die stärkste periodische Komponente.",
        "intuition": "Welche Frequenz dominiert?",
        "useful_for": "Identifikation charakteristischer Fehlerfrequenzen",
    },
    
    "Mittlere Frequenz": {
        "name_de": "Mittlere Frequenz",
        "domain": "Frequenzbereich",
        "formula": r"f_{\text{mean}} = \frac{\sum f_i \cdot S(f_i)}{\sum S(f_i)}",
        "description": "Schwerpunkt des Leistungsspektrums (S(f) = |X(f)|²). Ähnlich zum spektralen Schwerpunkt, aber auf Leistung basiert.",
        "intuition": "Wo liegt die Leistung im Frequenzspektrum?",
        "useful_for": "Energieverteilung im Frequenzbereich",
    },
}


# Validierung: Prüfe, ob alle Features aus features.py abgedeckt sind
_missing = set(FEATURE_NAMES) - set(FEATURE_INFO.keys())
if _missing:
    raise ValueError(f"FEATURE_INFO fehlt für: {_missing}")


def get_feature_info(feature_name: str) -> dict:
    """
    Gibt die Metadaten zu einem Feature zurück.
    
    Parameter:
        feature_name: Name des Features (z.B. "RMS")
    
    Returns:
        Dictionary mit: name_de, domain, formula, description, intuition, useful_for
    
    Raises:
        KeyError: Wenn das Feature nicht bekannt ist.
    """
    return FEATURE_INFO[feature_name]


def get_time_domain_features() -> list[str]:
    """Gibt die Namen aller Zeitbereich-Features zurück."""
    return [name for name, info in FEATURE_INFO.items() if info["domain"] == "Zeitbereich"]


def get_frequency_domain_features() -> list[str]:
    """Gibt die Namen aller Frequenzbereich-Features zurück."""
    return [name for name, info in FEATURE_INFO.items() if info["domain"] == "Frequenzbereich"]


def get_all_feature_names() -> list[str]:
    """Gibt alle Feature-Namen in der Reihenfolge von FEATURE_NAMES zurück."""
    return FEATURE_NAMES
