"""Génère ``app/static/img/og-card.svg``.

La carte de partage Twitter/LinkedIn. On produit un SVG (vectoriel, 8 Ko) que
les réseaux sociaux acceptent ; à la différence d'un PNG, il reste net sur les
écrans à haute densité.

    python3 tools/generate_og_card.py
"""

from __future__ import annotations

from pathlib import Path

OUTPUT = Path(__file__).resolve().parents[1] / "app" / "static" / "img" / "og-card.svg"

WIDTH, HEIGHT = 1200, 630

# Mêmes teintes que la feuille de style, en dur : le SVG n'a pas accès aux
# variables CSS du document.
PAPER = "#0c1011"
BASALT = "#1a2122"
BORDER = "#2b3435"
TEXT = "#e9ede6"
MUTED = "#9ba59e"
ACCENT = "#ef5c9c"

NAME = "Trules Doniphane"
ROLE = "Concepteur Développeur d'Applications"
LINE = "Python · Flask · Jinja2 · HTMX"


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def contours() -> str:
    """Quelques courbes de niveau en filigrane, dans l'esprit du hero."""
    rings = []
    for index in range(9):
        radius = 120 + index * 34
        rings.append(
            f'<ellipse cx="980" cy="330" rx="{radius * 1.25:.0f}" ry="{radius:.0f}"'
            f' fill="none" stroke="{BORDER}" stroke-width="1.4"'
            f' opacity="{0.9 - index * 0.08:.2f}"/>'
        )
    return "\n    ".join(rings)


def build() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"
     viewBox="0 0 {WIDTH} {HEIGHT}" role="img"
     aria-label="{esc(NAME)}, {esc(ROLE)}">
  <title>{esc(NAME)} — {esc(ROLE)}</title>
  <rect width="{WIDTH}" height="{HEIGHT}" fill="{PAPER}"/>

  <g>
    {contours()}
  </g>

  <circle cx="104" cy="98" r="30" fill="none" stroke="{BORDER}" stroke-width="2"/>
  <text x="104" y="107" text-anchor="middle" fill="{TEXT}"
        font-family="Georgia, serif" font-size="26" font-weight="700"
        font-style="italic">DT</text>

  <text x="64" y="300" fill="{TEXT}" font-family="Georgia, serif"
        font-size="86" font-weight="700" font-style="italic">{esc(NAME)}</text>

  <text x="64" y="366" fill="{TEXT}" font-family="Helvetica, Arial, sans-serif"
        font-size="40">{esc(ROLE)}</text>

  <rect x="64" y="424" width="86" height="4" fill="{ACCENT}"/>

  <text x="64" y="492" fill="{MUTED}" font-family="Menlo, monospace"
        font-size="26" letter-spacing="1">{esc(LINE)}</text>

  <text x="64" y="560" fill="{MUTED}" font-family="Helvetica, Arial, sans-serif"
        font-size="24">La Réunion · France</text>
</svg>
"""


if __name__ == "__main__":
    OUTPUT.write_text(build(), encoding="utf-8")
    print(f"og-card.svg écrit ({OUTPUT.stat().st_size // 1024} Ko)")
