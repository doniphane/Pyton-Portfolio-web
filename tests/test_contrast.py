"""Contrôle automatique du contraste de la palette.

Les valeurs vivent dans ``static/css/style.css`` ; on les relit pour ne pas
avoir deux endroits à maintenir. Le test échoue si un texte trop petit passe
sous 4,5:1 (WCAG 2.1 AA) sur l'un des trois fonds utilisés.

Ce fichier existe parce que les valeurs initiales échouaient : ``--text-faint``
valait 2,99:1 en thème clair, sur des étiquettes de 11 px.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

CSS = Path(__file__).resolve().parents[1] / "app" / "static" / "css" / "style.css"

#: Roles qui portent du texte de moins de 18 px : AA exige 4,5:1.
SMALL_TEXT_ROLES = ("text-muted", "text-faint", "accent", "link", "ok")
BACKGROUNDS = ("bg", "bg-tint", "surface")

MINIMUM = 4.5
MINIMUM_LARGE = 3.0  # titres ≥ 18 px, et éléments non textuels


def srgb(channel: int) -> float:
    c = channel / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(colour: str) -> float:
    h = colour.lstrip("#")
    if len(h) == 3:  # #fff -> #ffffff
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b)


def contrast(fg: str, bg: str) -> float:
    a, b = luminance(fg), luminance(bg)
    high, low = max(a, b), min(a, b)
    return (high + 0.05) / (low + 0.05)


def read_tokens() -> dict[str, dict[str, str]]:
    """Relit ``:root`` et ``[data-theme='dark']`` du fichier CSS."""
    css = CSS.read_text(encoding="utf-8")
    blocks: dict[str, dict[str, str]] = {}

    light = css.split(":root,\n[data-theme='light'] {", 1)[1].split("}", 1)[0]
    blocks["clair"] = dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{3,6})", light))

    dark = css.split("[data-theme='dark'] {", 1)[1].split("\n}", 1)[0]
    blocks["sombre"] = dict(re.findall(r"--([a-z0-9-]+):\s*(#[0-9a-fA-F]{3,6})", dark))

    return blocks


TOKENS = read_tokens()


@pytest.mark.parametrize("theme", sorted(TOKENS))
def test_jetons_presents(theme):
    for name in (*SMALL_TEXT_ROLES, *BACKGROUNDS, "text", "accent-on", "accent-wash"):
        assert name in TOKENS[theme], f"{theme}: jeton --{name} absent"


@pytest.mark.parametrize("theme", sorted(TOKENS))
@pytest.mark.parametrize("role", SMALL_TEXT_ROLES)
@pytest.mark.parametrize("background", BACKGROUNDS)
def test_contraste_texte_small(theme, role, background):
    ratio = contrast(TOKENS[theme][role], TOKENS[theme][background])
    assert ratio >= MINIMUM, (
        f"{theme}: --{role} sur --{background} = {ratio:.2f}:1, minimum {MINIMUM}:1"
    )


@pytest.mark.parametrize("theme", sorted(TOKENS))
def test_contraste_texte_principal(theme):
    ratio = contrast(TOKENS[theme]["text"], TOKENS[theme]["bg"])
    assert ratio >= 7.0, f"{theme}: texte principal = {ratio:.2f}:1"


@pytest.mark.parametrize("theme", sorted(TOKENS))
def test_contraste_bouton_primaire(theme):
    """Le texte du bouton principal doit passer sur le fond de l'accent."""
    ratio = contrast(TOKENS[theme]["accent-on"], TOKENS[theme]["accent"])
    assert ratio >= MINIMUM, f"{theme}: bouton primaire = {ratio:.2f}:1"


@pytest.mark.parametrize("theme", sorted(TOKENS))
def test_contour_des_elements_interactifs(theme):
    """--border-strong dessine le contour des boutons, des liens et des segments.

    C'est ce contour qui signale la présence d'un contrôle, donc 3:1 minimum
    (WCAG 1.4.11). --border ne sert qu'aux filets décoratifs entre cartes : la
    norme l'exempte, on ne le mesure donc pas.
    """
    for background in BACKGROUNDS:
        ratio = contrast(TOKENS[theme]["border-strong"], TOKENS[theme][background])
        assert ratio >= MINIMUM_LARGE, (
            f"{theme}: --border-strong sur --{background} = {ratio:.2f}:1"
        )


@pytest.mark.parametrize("theme", sorted(TOKENS))
@pytest.mark.parametrize("rank", [1, 2, 3])
def test_contraste_pastille_de_niveau(theme, rank):
    """Les pastilles « Bac », « Bac +2 », « Bac +3/+4 » portent du texte de
    10 px : le seuil AA de 4,5:1 s'applique, pas 3:1."""
    foreground = TOKENS[theme][f"badge-{rank}-fg"]
    background = TOKENS[theme][f"badge-{rank}-bg"]
    ratio = contrast(foreground, background)
    assert ratio >= MINIMUM, (
        f"{theme}: pastille niveau {rank} = {ratio:.2f}:1 "
        f"({foreground} sur {background})"
    )


@pytest.mark.parametrize("theme", sorted(TOKENS))
def test_anneau_de_focus_visible(theme):
    """Le focus doit être repérable sur tous les fonds, sinon il disparaît pour
    qui navigue au clavier."""
    for background in BACKGROUNDS:
        ratio = contrast(TOKENS[theme]["focus"], TOKENS[theme][background])
        assert ratio >= MINIMUM_LARGE, (
            f"{theme}: --focus sur --{background} = {ratio:.2f}:1"
        )


def test_le_css_est_la_seule_source_des_couleurs():
    """Garde-fou : les anciens tests passaient parce que la palette était
    dupliquée ailleurs. Il ne doit rester qu'un seul jeu de jetons."""
    css = CSS.read_text(encoding="utf-8")
    assert css.count("--text-faint:") == 2, "un seul jeton par thème"
    assert "prefers-color-scheme" not in css, (
        "le thème est posé par data-theme : pas de doublon dans une media query"
    )
