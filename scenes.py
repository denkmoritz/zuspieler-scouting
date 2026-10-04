"""Manim-Szenen für das Zuspieler-Scouting.

Rendern, z. B.:
    venv/bin/manim -qh scenes.py ReplayAlle
    HILFS=1 venv/bin/manim -qh scenes.py Verteilung     # mit Hilfszuspieler
Alle Szenen: ./render_all.sh
"""
import sys
from collections import Counter
from pathlib import Path

from manim import *

sys.path.insert(0, str(Path(__file__).parent))
from scouting import (  # noqa: E402
    JENSEITS,
    ZIEL_LABEL,
    ZIELZONEN,
    angriff_punkt,
    annahme_punkt,
    load,
    pfeil_schluessel,
    zuspiel_punkt,
)

BG = "#1a1a19"
FELD = "#262624"
LINIE = "#c3c2b7"
MUTED = "#8a8983"
INK = "#ffffff"
HEAT = "#3987e5"
ANNAHME_FARBE = "#a09f98"
ZUSPIEL_FARBE = "#eb6834"
BALL = "#ffe08a"

config.background_color = BG

# d-Wert, der in der Mitte des gezeichneten Feldes liegt
D_MITTE = (9 - JENSEITS) / 2
FELD_HOEHE = 9 + JENSEITS


class Feld(VGroup):
    """Halbes Feld, Netz oben. `u` = Manim-Einheiten pro Meter."""

    def __init__(self, u=0.6, mitte=ORIGIN, zonen=True):
        super().__init__()
        self.u = u
        self.mitte = np.array(mitte, dtype=float)
        k = u / 0.6
        self.add(self.rect(0, -JENSEITS, 9, 0, fill_color=FELD, fill_opacity=0.45, stroke_width=0))
        self.add(self.rect(0, 0, 9, 9, fill_color=FELD, fill_opacity=1, stroke_color=LINIE, stroke_width=2.5 * k))
        self.add(Line(self.p(0, 3), self.p(9, 3), color=LINIE, stroke_width=2 * k))
        for a, b in (((3, 0), (3, 9)), ((6, 0), (6, 9))):
            self.add(DashedLine(self.p(*a), self.p(*b), color=MUTED, stroke_width=1 * k, dash_length=0.08).set_opacity(0.5))
        self.add(Line(self.p(-0.4, 0), self.p(9.4, 0), color=INK, stroke_width=5 * k))
        if zonen:
            for z, (x, d) in {"4": (0.35, 0.4), "3": (3.35, 0.4), "2": (6.35, 0.4), "5": (0.35, 8.6), "6": (3.35, 8.6), "1": (6.35, 8.6)}.items():
                self.add(Text(z, font_size=20 * k, color=MUTED).move_to(self.p(x, d)))

    def p(self, x, d):
        return self.mitte + np.array([(x - 4.5) * self.u, (D_MITTE - d) * self.u, 0])

    def rect(self, x0, d0, x1, d1, **kw):
        return Polygon(self.p(x0, d0), self.p(x1, d0), self.p(x1, d1), self.p(x0, d1), **kw)


def verteilung(feld, rows, mit_n=True):
    """Heatmap der Zielzonen + aufsummierte Pfeile (Dicke = Anteil)."""
    g = VGroup()
    n = len(rows)
    if n == 0:
        return g
    k = feld.u / 0.6

    kacheln, labels = VGroup(), VGroup()
    for z, anzahl in Counter(r["Ziel"] for r in rows).items():
        anteil = anzahl / n
        kacheln.add(feld.rect(*ZIELZONEN[z], fill_color=HEAT, fill_opacity=min(0.85, 0.08 + 1.4 * anteil), stroke_width=0))
        lab = VGroup(Text(f"{round(100 * anteil)} %", font_size=26 * k, color=INK, weight=BOLD))
        if mit_n:
            lab.add(Text(f"n = {anzahl}", font_size=15 * k, color=INK))
        lab.arrange(DOWN, buff=0.05 * k).move_to(feld.p(*ZIEL_LABEL[z]))
        lab.add_background_rectangle(color=BG, opacity=0.55, buff=0.06 * k)
        labels.add(lab)

    annahmen = VGroup()
    for (_, _), gruppe in _gruppen(rows, lambda r: (r["Annahme_von"], r["Zuspiel_von"])).items():
        a, s = feld.p(*annahme_punkt(gruppe[0])), feld.p(*zuspiel_punkt(gruppe[0]))
        annahmen.add(Line(a, s, color=ANNAHME_FARBE, stroke_width=(1 + 10 * len(gruppe) / n) * k).set_opacity(0.3))

    pfeile = VGroup()
    for gruppe in sorted(_gruppen(rows, pfeil_schluessel).values(), key=len, reverse=True):
        s, t = feld.p(*zuspiel_punkt(gruppe[0])), feld.p(*angriff_punkt(gruppe[0]))
        w = min(13, 1.5 + 24 * len(gruppe) / n) * k
        spitze = (0.13 + 0.014 * w / k) * k
        pfeil = ArcBetweenPoints(s, t, angle=_bogen(s, t, 0.45), color=INK, stroke_width=w).add_tip(tip_length=spitze, tip_width=spitze)
        pfeile.add(pfeil.set_opacity(0.85).set_fill(opacity=0, family=False))

    g.add(kacheln, annahmen, pfeile, labels)
    return g


def _bogen(s, t, winkel):
    """Bogenwinkel so, dass sich netznahe Pässe ins Feld hinein wölben."""
    return -winkel if t[0] < s[0] else winkel


def _gruppen(rows, key):
    out = {}
    for r in rows:
        out.setdefault(key(r), []).append(r)
    return out


def ballwege(feld, r):
    """Annahmebogen und Zuspielbogen einer Aktion."""
    k = feld.u / 0.6
    a, s, t = (feld.p(*f(r)) for f in (annahme_punkt, zuspiel_punkt, angriff_punkt))
    annahme = ArcBetweenPoints(a, s, angle=-0.6, color=ANNAHME_FARBE, stroke_width=3 * k)
    zuspiel = ArcBetweenPoints(s, t, angle=_bogen(s, t, 0.6), color=ZUSPIEL_FARBE, stroke_width=5 * k)
    zuspiel.add_tip(tip_length=0.17 * k, tip_width=0.17 * k)
    return annahme, zuspiel


def spiele_aktion(scene, feld, r, tempo=1.0, extra=()):
    """Animiert eine Aktion und lässt die Wege als blasse Spur stehen."""
    k = feld.u / 0.6
    annahme, zuspiel = ballwege(feld, r)
    ball = Dot(annahme.get_start(), radius=0.085 * k, color=BALL)
    ring = Circle(radius=0.16 * k, color=ZUSPIEL_FARBE, stroke_width=3 * k).move_to(annahme.get_end())
    scene.play(FadeIn(ball, scale=0.4), *extra, run_time=0.2 / tempo)
    scene.play(MoveAlongPath(ball, annahme), Create(annahme), run_time=0.65 / tempo, rate_func=linear)
    scene.play(MoveAlongPath(ball, zuspiel), Create(zuspiel), FadeIn(ring), run_time=0.65 / tempo, rate_func=linear)
    scene.wait(0.35 / tempo)
    scene.play(FadeOut(ball), FadeOut(ring), annahme.animate.set_stroke(opacity=0.12), zuspiel.animate.set_opacity(0.28).set_fill(opacity=0, family=False), run_time=0.25 / tempo)
    return VGroup(annahme, zuspiel)


def abschnitte(rows):
    """Zusammenhängende Blöcke gleichen Satzes und Zuspielers."""
    out = []
    for r in rows:
        key = (r["Satz"], r["Zuspieler"])
        if not out or out[-1][0] != key:
            out.append((key, []))
        out[-1][1].append(r)
    return out


def legende(k=1.0):
    eintraege = VGroup()
    for farbe, text in ((ANNAHME_FARBE, "Annahme"), (ZUSPIEL_FARBE, "Zuspiel")):
        eintraege.add(VGroup(Line(ORIGIN, RIGHT * 0.5, color=farbe, stroke_width=5), Text(text, font_size=18 * k, color=LINIE)).arrange(RIGHT, buff=0.15))
    return eintraege.arrange(RIGHT, buff=0.5)


# ---------------------------------------------------------------- Replay


class ReplayAlle(Scene):
    """Alle Ballwege nacheinander, blockweise nach Satz/Zuspieler."""

    titel = "Zuspieler-Scouting · Replay"

    def auswahl(self, r):
        return True

    def info(self, r, i, n):
        zeilen = VGroup(
            Text(f"Satz {r['Satz']}  ·  {r['Ausfuehrender']}", font_size=26, color=INK),
            Text(f"Rotation {r['Rotation']}  ·  {r['Zuspieler_Reihe']}", font_size=22, color=LINIE),
            Text(r["Code"], font_size=64, color=ZUSPIEL_FARBE, weight=BOLD),
            Text(f"Annahme von {r['Annahme_von']}  ·  {r['Annahme_Qualitaet']}", font_size=22, color=LINIE),
            Text(f"Zuspiel von {r['Zuspiel_von']}", font_size=22, color=LINIE),
            Text(f"Pass nach {r['Ziel']}  ·  {r['Angriffsart']}", font_size=22, color=LINIE),
            Text(f"Aktion {i} / {n}", font_size=18, color=MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        return zeilen.move_to(RIGHT * 1.2 + UP * 0.6, aligned_edge=LEFT)

    def construct(self):
        rows = [r for r in load() if self.auswahl(r)]
        feld = Feld(u=0.6, mitte=LEFT * 3.4 + DOWN * 0.3)
        kopf = Text(self.titel, font_size=28, color=INK).to_corner(UL, buff=0.35)
        leg = legende().move_to(RIGHT * 1.2 + DOWN * 3.3, aligned_edge=LEFT)
        self.play(FadeIn(feld), FadeIn(kopf), FadeIn(leg))

        info, i = None, 0
        for (satz, zuspieler), block in abschnitte(rows):
            karte = Text(f"Satz {satz} · Zuspieler {zuspieler}", font_size=40, color=INK, weight=BOLD)
            karte.add_background_rectangle(color=BG, opacity=0.85, buff=0.3).move_to(feld.p(4.5, 4.5))
            self.play(FadeIn(karte), *([FadeOut(info)] if info else []), run_time=0.4)
            self.wait(0.8)
            self.play(FadeOut(karte), run_time=0.3)
            spuren, info = VGroup(), None
            for r in block:
                i += 1
                neu = self.info(r, i, len(rows))
                if info:
                    self.remove(info)
                info = neu
                self.add(info)
                spuren.add(spiele_aktion(self, feld, r))
            self.wait(1.2)
            self.play(FadeOut(spuren), run_time=0.4)
        self.wait(0.5)


class ReplaySatz1(ReplayAlle):
    titel = "Replay · Satz 1"

    def auswahl(self, r):
        return r["Satz"] == 1


class ReplaySatz2(ReplayAlle):
    titel = "Replay · Satz 2"

    def auswahl(self, r):
        return r["Satz"] == 2


class ReplaySatz3(ReplayAlle):
    titel = "Replay · Satz 3"

    def auswahl(self, r):
        return r["Satz"] == 3


class ReplayZuspieler10(ReplayAlle):
    titel = "Replay · Zuspieler 10"

    def auswahl(self, r):
        return r["Zuspieler"] == "10"


class ReplayZuspieler11(ReplayAlle):
    titel = "Replay · Zuspieler 11"

    def auswahl(self, r):
        return r["Zuspieler"] == "11"


# ------------------------------------------------------------ Verteilung


class Verteilung(Scene):
    """Aufsummierte Pfeile und Heatmap der Zielzonen über alle Aktionen."""

    def construct(self):
        rows = load()
        feld = Feld(u=0.6, mitte=LEFT * 3.4 + DOWN * 0.3)
        kopf = Text("Zuspielverteilung gesamt", font_size=28, color=INK).to_corner(UL, buff=0.35)
        self.play(FadeIn(feld), FadeIn(kopf))
        kacheln, annahmen, pfeile, labels = verteilung(feld, rows)
        self.play(FadeIn(kacheln), run_time=0.8)
        self.play(LaggedStart(*[Create(a) for a in annahmen], lag_ratio=0.1), run_time=1.2)
        self.play(LaggedStart(*[GrowFromPoint(p, p.get_start()) for p in pfeile], lag_ratio=0.15), run_time=3)
        self.play(FadeIn(labels))

        n = len(rows)
        zeilen = VGroup(Text(f"{n} Aktionen", font_size=26, color=INK, weight=BOLD))
        for (ziel, art), anzahl in Counter((r["Ziel"], r["Angriffsart"]) for r in rows).most_common():
            name = f"nach {ziel} · {art}" if ziel != "T" else art
            zeilen.add(Text(f"{round(100 * anzahl / n):>3} %   {name}  ({anzahl})", font_size=20, color=LINIE))
        zeilen.add(Text("Pfeildicke = Anteil · Fläche = Zielzone", font_size=16, color=MUTED))
        zeilen.arrange(DOWN, aligned_edge=LEFT, buff=0.2).move_to(RIGHT * 1.2, aligned_edge=LEFT)
        self.play(LaggedStart(*[FadeIn(z, shift=LEFT * 0.2) for z in zeilen], lag_ratio=0.15), run_time=2)
        self.wait(3)


class Kombiniert(Scene):
    """Links läuft das Replay, rechts baut sich die Verteilung auf."""

    def construct(self):
        rows = load()
        links = Feld(u=0.52, mitte=LEFT * 3.5 + DOWN * 0.45)
        rechts = Feld(u=0.52, mitte=RIGHT * 3.5 + DOWN * 0.45)
        t_links = Text("Replay", font_size=22, color=LINIE).next_to(links, UP, buff=0.12)
        t_rechts = Text("Verteilung", font_size=22, color=LINIE).next_to(rechts, UP, buff=0.12)
        self.play(FadeIn(links), FadeIn(rechts), FadeIn(t_links), FadeIn(t_rechts))

        kopf, stand, spuren, bisher = None, VGroup(), VGroup(), []
        self.add(stand)
        letzter_block = None
        for i, r in enumerate(rows, 1):
            block = (r["Satz"], r["Zuspieler"])
            if block != letzter_block and len(spuren):
                self.play(FadeOut(spuren), run_time=0.3)
                spuren = VGroup()
            letzter_block = block
            neu = Text(
                f"Satz {r['Satz']} · {r['Ausfuehrender']} · Rot. {r['Rotation']} ({r['Zuspieler_Reihe']}) · {r['Code']} · {i}/{len(rows)}",
                font_size=24, color=INK,
            ).to_edge(UP, buff=0.3)
            if kopf:
                self.remove(kopf)
            kopf = neu
            self.add(kopf)
            spuren.add(spiele_aktion(self, links, r, tempo=1.3))
            bisher.append(r)
            self.remove(stand)
            stand = verteilung(rechts, bisher)
            self.add(stand)
        self.wait(3)


# -------------------------------------------------------------- Vergleich


class _Vergleich(Scene):
    titel = ""
    spalten = 2
    # Liste aus (Überschrift, Filterfunktion)
    panels = []

    def construct(self):
        rows = load()
        zeilen = -(-len(self.panels) // self.spalten)
        breite, hoehe = 13.4 / self.spalten, 6.9 / zeilen
        u = min((breite - 0.5) / 9, (hoehe - 0.5) / FELD_HOEHE)
        kopf = Text(self.titel, font_size=28, color=INK).to_edge(UP, buff=0.2)
        self.play(FadeIn(kopf))

        felder, titel, inhalte = VGroup(), VGroup(), []
        for i, (name, f) in enumerate(self.panels):
            zeile, spalte = divmod(i, self.spalten)
            mitte = np.array([(spalte - (self.spalten - 1) / 2) * breite, 3.35 - (zeile + 0.5) * hoehe - 0.2, 0])
            feld = Feld(u=u, mitte=mitte, zonen=u > 0.35)
            auswahl = [r for r in rows if f(r)]
            felder.add(feld)
            titel.add(Text(f"{name}  (n = {len(auswahl)})", font_size=max(15, 34 * u), color=INK).next_to(feld, UP, buff=0.08))
            inhalte.append(verteilung(feld, auswahl, mit_n=u > 0.35))
        self.play(FadeIn(felder), FadeIn(titel))
        inhalte = [g for g in inhalte if len(g)]
        self.play(*[FadeIn(g[0]) for g in inhalte], *[FadeIn(g[1]) for g in inhalte], run_time=0.8)
        self.play(*[LaggedStart(*[GrowFromPoint(p, p.get_start()) for p in g[2]], lag_ratio=0.2) for g in inhalte], run_time=2.5)
        self.play(*[FadeIn(g[3]) for g in inhalte])
        self.wait(4)


class VergleichZuspieler(_Vergleich):
    titel = "Zuspieler 10 vs. 11"
    panels = [(f"Zuspieler {z}", lambda r, z=z: r["Zuspieler"] == z) for z in ("10", "11")]


class VergleichReihe(_Vergleich):
    titel = "Zuspieler vorne vs. hinten (Läufer)"
    panels = [(name, lambda r, name=name: r["Zuspieler_Reihe"] == name) for name in ("Vorne", "Hinten (Läufer)")]


class VergleichRotation(_Vergleich):
    titel = "Verteilung nach Rotation (oben: Läufer hinten · unten: Zuspieler vorne)"
    spalten = 3
    panels = [(f"Rotation {n}", lambda r, n=n: r["Rotation"] == n) for n in (1, 6, 5, 4, 3, 2)]


class VergleichAnnahmequalitaet(_Vergleich):
    titel = "Verteilung nach Annahmequalität"
    spalten = 3
    panels = [(q, lambda r, q=q: r["Annahme_Qualitaet"] == q) for q in ("optimal", "3-m-Linie", "abweichend")]


class VergleichAnnahmezone(_Vergleich):
    titel = "Verteilung nach Annahmezone"
    spalten = 3
    panels = [(f"Annahme von {z}", lambda r, z=z: r["Annahme_von"] == z) for z in ("5", "6", "1")]
