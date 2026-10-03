"""Jeu d'icônes SVG inline (trait 1.5, grille 24×24, style Lucide).

Inlinées plutôt qu'inlinées-par-sprite : il n'y a pas de requête réseau, le
HTML reste lisible et la couleur suit ``currentColor`` du texte environnant.
"""

from __future__ import annotations

from markupsafe import Markup

ICONS: dict[str, str] = {
    "arrow-down": '<path d="M12 4v16"/><path d="m6 14 6 6 6-6"/>',
    "arrow-left": '<path d="M20 12H4"/><path d="m10 6-6 6 6 6"/>',
    "check": '<path d="m4 12.5 5 5L20 6.5"/>',
    "chevron-left": '<path d="m15 5-7 7 7 7"/>',
    "chevron-right": '<path d="m9 5 7 7-7 7"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "code": '<path d="m8 6-6 6 6 6"/><path d="m16 6 6 6-6 6"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5 5-2Z"/>',
    "download": '<path d="M12 3v12"/><path d="m7 11 5 5 5-5"/><path d="M4 20h16"/>',
    "external": '<path d="M14 4h6v6"/><path d="M20 4 10 14"/>'
    '<path d="M19 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h4"/>',
    "file-text": '<path d="M14 3v5h5"/><path d="M19 8v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7Z"/>'
    '<path d="M9 13h6M9 17h4"/>',
    "filter": '<path d="M3 5h18l-7 8.5V20l-4 1.5v-8L3 5Z"/>',
    "github": '<path d="M9 19c-4 1.5-4-2.5-6-3"/><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5"/>'
    '<path d="M21 8.5c0 3.5-3 5.5-6 5.5a7.6 7.6 0 0 1-1 3.5v4"/><path d="M9 14a9 9 0 0 1-4-1.7"/>'
    '<path d="M15 3a13 13 0 0 1 3 2.2 12.8 12.8 0 0 1 0 3.3"/><path d="M9 5.2A12.8 12.8 0 0 1 12 5"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
    '<path d="M12 3a15 15 0 0 1 0 18 15 15 0 0 1 0-18Z"/>',
    "graduation-cap": '<path d="M22 10 12 5 2 10l10 5 10-5Z"/><path d="M6 12.5V17c0 1.7 2.7 3 6 3s6-1.3 6-3v-4.5"/>',
    "layers": '<path d="M12 2.5 2.5 7.2 12 12l9.5-4.8L12 2.5Z"/><path d="m2.5 12 9.5 4.8 9.5-4.8"/>'
    '<path d="m2.5 16.8 9.5 4.7 9.5-4.7"/>',
    "linkedin": '<path d="M16 8.5a5.5 5.5 0 0 1 5.5 5.5V21h-4v-6.5a1.5 1.5 0 0 0-3 0V21h-4V9h4v1.4"/>'
    '<path d="M6.5 9v12"/><circle cx="6.5" cy="5.5" r="1.8"/>',
    "mail": '<rect x="2.5" y="4.5" width="19" height="15" rx="2"/><path d="m3 7 8.3 5.4a1.5 1.5 0 0 0 1.4 0L21 7"/>',
    "map-pin": '<path d="M20 10.2c0 4.8-8 11.3-8 11.3S4 15 4 10.2a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="2.8"/>',
    "moon": '<path d="M20.5 14.8A8.7 8.7 0 0 1 9.2 3.5a8.8 8.8 0 1 0 11.3 11.3Z"/>',
    "play": '<circle cx="12" cy="12" r="9"/><path d="m10.2 8.4 5.6 3.6-5.6 3.6V8.4Z"/>',
    "sparkle": '<path d="M12 3.2 13.7 8.3 18.8 10 13.7 11.7 12 16.8 10.3 11.7 5.2 10 10.3 8.3 12 3.2Z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M4.7 4.7l1.4 1.4M17.9 17.9l1.4 1.4"/>'
    '<path d="M2.5 12h2M19.5 12h2M4.7 19.3l1.4-1.4M17.9 6.1l1.4-1.4"/>',
    "youtube": '<path d="M21.6 8.2a2.6 2.6 0 0 0-1.8-1.8C18.2 6 12 6 12 6s-6.2 0-7.8.4A2.6 2.6 0 0 0 2.4 8.2"/>'
    '<path d="M2.4 8.2A24 24 0 0 0 2 12c0 1.3.1 2.6.4 3.8a2.6 2.6 0 0 0 1.8 1.8C5.8 18 12 18 12 18s6.2 0 7.8-.4a2.6 2.6 0 0 0 1.8-1.8"/>'
    '<path d="M10.2 9.2 15 12l-4.8 2.8V9.2Z"/>',
    "x": '<path d="M6.5 6.5 17.5 17.5M17.5 6.5 6.5 17.5"/>',
}


def svg(name: str, *, size: int = 20, class_: str | None = None) -> Markup:
    """Retourne le balisage SVG d'une icône.

    ``class_`` peut porter la classe CSS qui pilote couleur et taille.

    Le résultat est marqué comme ``Markup`` : sans cela, l'échappement
    automatique de Jinja afficherait le code SVG en clair dans la page.
    """
    body = ICONS.get(name)
    if body is None:
        raise KeyError(f"icône inconnue : {name!r}")
    classes = f' class="{class_}"' if class_ else ""
    return Markup(
        f'<svg{classes} width="{size}" height="{size}" viewBox="0 0 24 24" fill="none"'
        ' stroke="currentColor" stroke-width="1.5" stroke-linecap="round"'
        f' stroke-linejoin="round" aria-hidden="true" focusable="false">{body}</svg>'
    )
