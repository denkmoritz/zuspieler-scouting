"""Daten und Feldgeometrie für das Zuspieler-Scouting.

Koordinaten: x = 0..9 m von links nach rechts (Blick von der Grundlinie zum Netz),
d = Abstand vom Netz in m (0 = Netz, 9 = Grundlinie, negativ = Feld des Gegners).
"""
import csv
import os
from pathlib import Path

CSV_PATH = Path(__file__).parent / "data" / "scouting_zuspieler.csv"

# So weit wird das gegnerische Feld hinter dem Netz noch gezeichnet (für "T").
JENSEITS = 1.4

# Annahmepunkte: Mitte der Hinterfeldzonen, leicht Richtung Grundlinie versetzt,
# damit sie nicht mit einem Zuspiel aus Zone 1/6 zusammenfallen.
ANNAHME = {"5": (1.5, 6.5), "6": (4.5, 6.5), "1": (7.5, 6.5)}

ZUSPIEL = {
    "O": (5.5, 0.5),
    "N": (5.5, 3.0),
    "2": (7.0, 0.7),
    "3": (4.5, 0.7),
    "3.5": (3.0, 0.7),
    "4": (1.8, 0.7),
    "1": (7.5, 5.0),
    "6": (4.5, 5.0),
}

# Zonenflächen für die Heatmap: (x0, d0, x1, d1)
ZIELZONEN = {
    "4": (0, 0, 3, 3),
    "3": (3, 0, 6, 3),
    "2": (6, 0, 9, 3),
    "6": (3, 3, 6, 9),
    "1": (6, 3, 9, 9),
    "T": (0, -1.2, 9, -0.15),
}

# Position des Prozentlabels je Zielzone
ZIEL_LABEL = {
    "4": (1.5, 2.1),
    "3": (4.5, 2.1),
    "2": (7.5, 2.1),
    "6": (4.5, 8.0),
    "1": (7.5, 8.0),
    "T": (7.5, -0.68),
}

ZIEL_NAME = {
    "4": "Außen (4)",
    "3": "Mitte (3)",
    "2": "Diagonal (2)",
    "1": "Hinterfeld (1)",
    "6": "Pipe (6)",
    "T": "Zuspieler selbst (T)",
}


def load(include_hilfs=None):
    """Lädt die Aktionen. Der Hilfszuspieler ist nur mit HILFS=1 dabei."""
    if include_hilfs is None:
        include_hilfs = os.environ.get("HILFS") == "1"
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    for r in rows:
        for key in ("Nr", "Satz", "Rotation"):
            r[key] = int(r[key])
        r["Ziel"] = r["Pass_nach"] or "T"
    if not include_hilfs:
        rows = [r for r in rows if r["Ausfuehrender"] != "Hilfszuspieler"]
    return rows


def annahme_punkt(r):
    return ANNAHME[r["Annahme_von"]]


def zuspiel_punkt(r):
    return ZUSPIEL[r["Zuspiel_von"]]


def angriff_punkt(r):
    sx, sd = zuspiel_punkt(r)
    art, ziel = r["Angriffsart"], r["Ziel"]
    if ziel == "T":
        return (sx - 0.5, -1.0)
    if art == "Schuss":
        return (sx - 2.0, 0.5)
    if art == "Aufsteiger über Kopf":
        return (sx + 0.9, 0.5)
    if ziel == "3":
        # Aufsteiger: Zonenmitte, aber nie auf dem Zuspieler selbst
        return (4.5 if abs(sx - 4.5) > 0.8 else sx - 1.0, 0.5)
    return {"4": (0.7, 0.6), "2": (8.3, 0.6), "1": (7.5, 3.6), "6": (4.5, 3.6)}[ziel]


def pfeil_schluessel(r):
    """Aktionen mit gleichem Schlüssel ergeben in der Verteilung denselben Pfeil."""
    return (r["Zuspiel_von"], r["Ziel"], r["Angriffsart"])
