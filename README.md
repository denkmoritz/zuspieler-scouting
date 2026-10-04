# Zuspieler-Scouting

Auswertung eines gescouteten gegnerischen Zuspielers (Läufer-System): aus welcher Zone kam die Annahme, von wo wurde zugespielt, wohin ging der Pass. Die Muster gibt es als interaktive Web-Ansicht und als Manim-Videos.

**Live:** https://denkmoritz.github.io/zuspieler-scouting/

## Web-Ansicht

`docs/index.html` ist eine einzelne Datei ohne Build-Schritt, die Daten sind eingebettet.

- Filter: Zuspieler, Satz, Rotation, Vorne/Hinten, Annahmequalität, Annahmezone (kombinierbar)
- Modus **Replay**: animierte Ballwege mit Play/Pause, Geschwindigkeit und Aktionsliste
- Modus **Verteilung**: Pfeildicke nach Anteil, Heatmap der Zielzonen, Tabellen
- Über „Andere CSV laden“ lässt sich ein anderes Spiel im gleichen Format ansehen

Die gerenderten Videos stehen unter `docs/videos.html`.

## Videos rendern

Voraussetzungen: Python 3.11, ffmpeg.

```sh
python3 -m venv venv
venv/bin/pip install -r requirements.txt

./render_all.sh                               # alle Szenen in 1080p, kopiert sie nach docs/videos/
venv/bin/manim -qh scenes.py Kombiniert       # eine einzelne Szene
HILFS=1 ./render_all.sh                       # mit der Aktion des Hilfszuspielers
```

Szenen: `ReplayAlle`, `ReplaySatz1`–`3`, `ReplayZuspieler10`/`11`, `Verteilung`, `Kombiniert`, `VergleichZuspieler`, `VergleichReihe`, `VergleichRotation`, `VergleichAnnahmequalitaet`, `VergleichAnnahmezone`.

## Daten

`data/scouting_zuspieler.csv` (Semikolon-getrennt, UTF-8 mit BOM), eine Zeile pro Zuspiel.

Der Code setzt sich aus Annahmezone, Zielzone und Zuspielposition zusammen, z. B. `64O` = Annahme von 6, Pass nach 4, Zuspiel von optimaler Position.

| Zuspiel von | Bedeutung |
|---|---|
| `O` | optimal, am Netz zwischen Position 2 und 3 |
| `N` | gute Annahme, Zuspiel etwa von der 3-m-Linie |
| Zahl | Zone, aus der gespielt wurde (`3.5` = zwischen 3 und 4) |

Sonderfälle in der Mitte: `S` = Schuss, `U` = Aufsteiger über Kopf, `T` = Zuspieler spielt selbst rüber.

## Aufbau

| Datei | Inhalt |
|---|---|
| `scouting.py` | CSV laden, Feldgeometrie (Annahme-, Zuspiel- und Angriffspunkte) |
| `scenes.py` | Manim-Szenen |
| `render_all.sh` | rendert alle Szenen |
| `docs/` | GitHub Page: interaktive Ansicht und Videos |

Die Feldkoordinaten stehen in `scouting.py` und gespiegelt im Skript von `docs/index.html`. Wer sie ändert, muss beide Stellen anpassen; dasselbe gilt für die eingebettete CSV in `docs/index.html`.
