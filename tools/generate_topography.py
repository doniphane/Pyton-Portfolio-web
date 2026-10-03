"""Génère ``app/static/img/topography.svg``.

Les courbes de niveau du hero sont produites ici plutôt que dessinées à la main :
un champ de perturbation sur un rayon donne des courbes imbriquées qui ne sont
pas concentriques, comme une vraie carte topographique — deux pitons et leurs
coulées, pas une cible.

    python3 tools/generate_topography.py

Le fichier est déterministe : mêmes paramètres, même SVG.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / "app" / "static" / "img" / "topography.svg"

WIDTH, HEIGHT = 1600, 1000
STEPS = 96    # points par courbe (suffisant pour des Bézier lissées)
LEVELS = 12   # nombre de courbes de niveau par sommet
DECIMALS = 0  # coordonnées entières : le fichier reste léger


@dataclass(frozen=True)
class Peak:
    """Un sommet : position, rayon de base et amplitude des irrégularités."""

    cx: float
    cy: float
    radius: float
    harmonics: tuple[tuple[int, float, float], ...]  # (fréquence, amplitude, phase)


PEAKS: tuple[Peak, ...] = (
    Peak(
        cx=1180.0,
        cy=430.0,
        radius=430.0,
        harmonics=((2, 0.16, 0.4), (3, 0.10, 1.9), (5, 0.05, 3.1), (7, 0.03, 0.7)),
    ),
    Peak(
        cx=430.0,
        cy=880.0,
        radius=360.0,
        harmonics=((2, 0.18, 2.6), (3, 0.09, 0.2), (5, 0.06, 4.4)),
    ),
    Peak(
        cx=250.0,
        cy=180.0,
        radius=210.0,
        harmonics=((3, 0.20, 1.1), (4, 0.08, 2.2), (6, 0.04, 5.0)),
    ),
)


def radius_at(theta: float, peak: Peak) -> float:
    r = 1.0
    for frequency, amplitude, phase in peak.harmonics:
        r += amplitude * math.sin(frequency * theta + phase)
    return peak.radius * r


def contour_points(peak: Peak, level: float, squash: float = 1.0) -> list[tuple[float, float]]:
    """Points d'une courbe de niveau autour d'un sommet.

    ``level`` vaut 0 pour le sommet (petit rayon) et 1 pour la base (grand
    rayon). Chaque sommet dérive légèrement vers l'extérieur, ce qui fait que les
    courbes s'écartent comme sur un terrain réel plutôt que de se superposer.
    ``squash`` aplatit l'ellipse pour suggérer une vue en perspective.
    """
    points: list[tuple[float, float]] = []
    for index in range(STEPS):
        theta = 2 * math.pi * index / STEPS
        drift = 1.0 + level * 0.55
        dx = peak.cx * 0.16 * level
        dy = peak.cy * 0.16 * level
        r = radius_at(theta, peak) * (0.16 + 0.84 * level) * drift
        points.append(
            (peak.cx + dx + r * math.cos(theta), peak.cy + dy + r * math.sin(theta) * squash)
        )
    return points


def to_path(points: list[tuple[float, float]]) -> str:
    """Convertit une polyligne fermée en courbes de Bézier cubiques (Catmull-Rom)."""
    n = len(points)
    commands: list[str] = []
    for i in range(n):
        p0 = points[(i - 1) % n]
        p1 = points[i]
        p2 = points[(i + 1) % n]
        p3 = points[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        if i == 0:
            commands.append(f"M{p1[0]:.{DECIMALS}f},{p1[1]:.{DECIMALS}f}")
        commands.append(
            f"C{c1[0]:.{DECIMALS}f},{c1[1]:.{DECIMALS}f}"
            f" {c2[0]:.{DECIMALS}f},{c2[1]:.{DECIMALS}f}"
            f" {p2[0]:.{DECIMALS}f},{p2[1]:.{DECIMALS}f}"
        )
    commands.append("Z")
    return "".join(commands)


def build_svg(random_seed: int = 7) -> str:
    random.seed(random_seed)
    paths: list[str] = []
    levels = [0.10 + 0.90 * (i / (LEVELS - 1)) for i in range(LEVELS)]

    for peak_index, peak in enumerate(PEAKS):
        # Le sommet de gauche est plus écrasé : perspective de vallon.
        squash = 1.0 if peak_index != 1 else 0.62
        for index, level in enumerate(levels):
            # Les courbes les plus externes s'espacent, comme sur une carte.
            spacing = level + 0.035 * math.sin(index * 1.3 + peak_index)
            points = contour_points(peak, min(1.0, spacing), squash)
            opacity = 0.9 - 0.6 * level
            width = 1.2 if index % 4 else 1.9
            paths.append(
                f'<path d="{to_path(points)}" '
                f'stroke-width="{width}" stroke-opacity="{opacity:.2f}"/>'
            )

    body = "\n    ".join(paths)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}"
     preserveAspectRatio="xMidYMid slice" role="presentation" aria-hidden="true">
  <title>Courbes de niveau — générées par tools/generate_topography.py</title>
  <g fill="none" stroke="currentColor" stroke-linejoin="round">
    {body}
  </g>
</svg>
"""


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_svg(), encoding="utf-8")
    print(f"topography.svg écrit ({OUTPUT.stat().st_size // 1024} Ko)")
