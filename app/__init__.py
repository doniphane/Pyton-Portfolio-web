"""Application Flask du portfolio.

Point d'entrée : ``create_app()``. Les routes sont dans ``app.routes``.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from flask import Flask, render_template, request
from markupsafe import Markup

from app.data.icons import svg as icon_svg
from app.data.profile import (
    FACTS,
    JOURNEY,
    PASSIONS,
    PROFILE,
    SKILL_GROUPS,
    SKILL_GROUPS_BY_KEY,
    SOCIALS,
    STACK,
    STATS,
)
from app.data.projects import PROJECTS, PROJECTS_BY_SLUG
from app.routes import main

PACKAGE_DIR = Path(__file__).resolve().parent

#: Entrées du rail de navigation, dans l'ordre d'apparition sur la page.
RAIL_ITEMS: tuple[tuple[str, str, str], ...] = (
    ("accueil", "Accueil", "sparkle"),
    ("a-propos", "À propos", "graduation-cap"),
    ("competences", "Compétences", "code"),
    ("projets", "Projets", "layers"),
    ("contact", "Contact", "mail"),
)

#: Les deux moitiés du sélecteur de thème. La feuille de style affiche celle qui
#: correspond au thème actif en masquant l'autre.
#:
#: La chaîne est assemblée d'abord, puis marquée une seule fois : ``Markup + str``
#: échapperait le HTML et les ``<span>`` disparaîtraient de la page.
THEME_ICONS = Markup(
    '<span class="theme-toggle__icon" data-theme-icon="light">'
    f'{icon_svg("sun", size=19)}</span>'
    '<span class="theme-toggle__icon" data-theme-icon="dark">'
    f'{icon_svg("moon", size=19)}</span>'
)



def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(PACKAGE_DIR / "static"),
        static_url_path="/static",
        template_folder=str(PACKAGE_DIR / "templates"),
    )

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-change-me"),
        SITE_URL=os.environ.get("SITE_URL", "http://127.0.0.1:5000"),
        TEMPLATES_AUTO_RELOAD=os.environ.get("FLASK_DEBUG") == "1",
    )
    if test_config:
        app.config.update(test_config)

    # Les fichiers statiques sont servis avec une longue durée de cache en
    # production, et sans cache en développement — sinon il faut un
    # rechargement forcé du navigateur à chaque modification de CSS.
    if not app.debug:
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 60 * 60 * 24 * 30
    else:
        app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    app.register_blueprint(main)

    # -- Contexte disponible dans tous les templates ----------------------- #

    @app.context_processor
    def inject_globals() -> dict:
        return {
            "profile": PROFILE,
            "skill_groups": SKILL_GROUPS,
            "stats": STATS,
            "journey": JOURNEY,
            "facts": FACTS,
            "passions": PASSIONS,
            "socials": SOCIALS,
            "stack": STACK,
            "current_year": datetime.now(UTC).year,
            "current_path": request.path,
            "site_url": app.config["SITE_URL"].rstrip("/"),
            "icon": icon_svg,
            "rail_items": [
                {"id": item_id, "label": label, "icon": icon_name}
                for item_id, label, icon_name in RAIL_ITEMS
            ],
            "theme_icons": THEME_ICONS,
            "theme_default": "light",
        }

    # -- Filtres Jinja ------------------------------------------------------ #

    @app.template_filter("month_year")
    def month_year(value) -> str:
        """Formate une date en « mars 2026 », en français."""
        months = (
            "janvier", "février", "mars", "avril", "mai", "juin",
            "juillet", "août", "septembre", "octobre", "novembre", "décembre",
        )
        return f"{months[value.month - 1]} {value.year}"

    @app.template_filter("domain")
    def domain(url: str) -> str:
        """Retire le schéma et le slash final d'une URL pour l'afficher court."""
        trimmed = url.split("://", 1)[-1].rstrip("/")
        return trimmed.removeprefix("www.")

    # -- Gestion d'erreurs -------------------------------------------------- #

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):  # pragma: no cover
        return render_template("errors/500.html"), 500

    # -- Fichiers robots / plan du site ------------------------------------ #

    @app.get("/robots.txt")
    def robots():
        body = f"User-agent: *\nAllow: /\nSitemap: {app.config['SITE_URL']}/sitemap.xml\n"
        return body, 200, {"Content-Type": "text/plain; charset=utf-8"}

    @app.get("/sitemap.xml")
    def sitemap():
        urls = ["/"] + [f"/projets/{p.slug}" for p in PROJECTS]
        base = app.config["SITE_URL"].rstrip("/")
        body = ['<?xml version="1.0" encoding="UTF-8"?>',
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for path in urls:
            body.append(f"  <url><loc>{base}{path}</loc></url>")
        body.append("</urlset>")
        return "\n".join(body), 200, {"Content-Type": "application/xml; charset=utf-8"}

    return app


__all__ = ["create_app", "PROFILE", "SKILL_GROUPS_BY_KEY", "PROJECTS_BY_SLUG"]
