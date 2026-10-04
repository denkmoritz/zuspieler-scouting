#!/bin/sh
# Rendert alle Szenen. Qualität als Argument: l (480p), m (720p), h (1080p, Standard), k (4K).
# Mit Hilfszuspieler: HILFS=1 ./render_all.sh
cd "$(dirname "$0")" || exit 1
Q="${1:-h}"
for scene in ReplayAlle ReplaySatz1 ReplaySatz2 ReplaySatz3 ReplayZuspieler10 ReplayZuspieler11 \
             Verteilung Kombiniert \
             VergleichZuspieler VergleichReihe VergleichRotation VergleichAnnahmequalitaet VergleichAnnahmezone; do
  venv/bin/manim "-q$Q" scenes.py "$scene" || exit 1
done

# Für die GitHub Page: fertige 1080p-Videos nach docs/videos/ kopieren
if [ "$Q" = "h" ]; then
  mkdir -p docs/videos && cp media/videos/scenes/1080p60/*.mp4 docs/videos/
fi
