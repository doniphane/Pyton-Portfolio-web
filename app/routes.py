"""Routes du portfolio.

Trois familles d'endpoints :

* les pages complètes (``/`` et ``/projets/<slug>``) ;
* les fragments HTMX (``/partials/...``) qui renvoient du HTML, jamais du JSON ;
* les fichiers publics (``robots.txt``, ``sitemap.xml`` sont dans ``__init__``).
"""

from __future__ import annotations

from urllib.parse import urlencode

from flask import Blueprint, abort, render_template, request, url_for

from app.data.projects import (
    SORTED_PROJECTS,
    STATUS_FILTERS,
    YEARS,
    filter_projects,
    get_project,
    technologies_used,
)

main = Blueprint("main", __name__)

#: Nombre de projets affichés dans la grille. La pagination évite de charger
#: 20 cartes d'un coup sur mobile.
PAGE_SIZE = 9

_FILTER_PARAMS = ("status", "year", "tech")


def _filters_from_request() -> dict[str, str]:
    """Lit et valide les filtres présents dans l'URL.

    Les valeurs inconnues retombent sur « all » : une URL peut être falsifiée ou
    simplemente périmée après une refonte, la page doit toujours s'afficher.
    """
    raw = request.args

    status = raw.get("status", "all")
    if status not in {value for value, _ in STATUS_FILTERS}:
        status = "all"

    year = raw.get("year", "all")
    if year not in {"all", *YEARS}:
        year = "all"

    tech = raw.get("tech", "all")
    if tech not in {"all", *technologies_used()}:
        tech = "all"

    return {"status": status, "year": year, "tech": tech}


def _selected(techs: list[str], current: str) -> str:
    return " is-selected" if current in techs else ""


def _push_url(filters: dict[str, str], page: int = 1) -> str:
    """URL canonique et partageable correspondant à une sélection de filtres.

    Renvoyée dans l'en-tête ``HX-Push-Url`` : le navigateur affiche ``/?status=…
    &year=…`` et non l'URL interne du fragment. Recharger ou partager le lien
    redonne donc la page complète, pas un bout de HTML.
    """
    params = {name: value for name, value in filters.items() if value != "all"}
    if page > 1:
        params["page"] = str(page)
    query = urlencode(params)
    base = url_for("main.index")
    return f"{base}?{query}" if query else base


# --------------------------------------------------------------------------- #
# Pages
# --------------------------------------------------------------------------- #


@main.get("/")
def index():
    filters = _filters_from_request()
    page = request.args.get("page", 1, type=int)
    page = max(1, page)

    matches = filter_projects(SORTED_PROJECTS, **filters)
    pages = max(1, -(-len(matches) // PAGE_SIZE))
    page = min(page, pages)
    start = (page - 1) * PAGE_SIZE

    return render_template(
        "index.html",
        filters=filters,
        status_filters=STATUS_FILTERS,
        years=YEARS,
        techs=technologies_used(),
        projects=matches[start:start + PAGE_SIZE],
        total=len(matches),
        total_all=len(SORTED_PROJECTS),
        page=page,
        pages=pages,
        _selected=_selected,
    )


@main.get("/projets/<slug>")
def project_page(slug: str):
    """Page complète d'un projet — sert de repli sans JavaScript et de lien partageable."""
    project = get_project(slug) or abort(404)
    return render_template(
        "project.html",
        project=project,
        sorted_projects=list(SORTED_PROJECTS),
    )


# --------------------------------------------------------------------------- #
# Fragments HTMX
# --------------------------------------------------------------------------- #


@main.get("/partials/projects")
def partial_projects():
    """Grille de projets filtrée. L'URL est poussée dans la barre d'adresse
    par ``hx-push-url``, donc la sélection est partageable et rechargeable."""
    filters = _filters_from_request()
    page = max(1, request.args.get("page", 1, type=int))

    matches = filter_projects(SORTED_PROJECTS, **filters)
    pages = max(1, -(-len(matches) // PAGE_SIZE))
    page = min(page, pages)
    start = (page - 1) * PAGE_SIZE

    return render_template(
        "partials/projects_grid.html",
        projects=matches[start:start + PAGE_SIZE],
        total=len(matches),
        total_all=len(SORTED_PROJECTS),
        filters=filters,
        page=page,
        pages=pages,
        status_filters=STATUS_FILTERS,
        years=YEARS,
        techs=technologies_used(),
        _selected=_selected,
    ), 200, {"HX-Push-Url": _push_url(filters, page)}


@main.get("/partials/projects/<slug>")
def partial_project_detail(slug: str):
    """Fiche détaillée d'un projet, injectée sous la carte cliquée."""
    project = get_project(slug) or abort(404)
    return render_template("partials/project_detail.html", project=project)
