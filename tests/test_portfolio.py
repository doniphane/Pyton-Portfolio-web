"""Tests du portfolio.

Ils couvrent ce qui casse silencieusement : une icône manquante, un filtre
d'URL falsifié, un projet sans image, une page qui plante.
"""

from __future__ import annotations

import re

import pytest
from markupsafe import escape

from app import create_app
from app.data.icons import ICONS
from app.data.profile import (
    FACTS,
    JOURNEY,
    PASSIONS,
    PROFILE,
    SKILL_GROUPS,
    SOCIALS,
    STATS,
)
from app.data.projects import PROJECTS, PROJECTS_BY_SLUG, filter_projects


@pytest.fixture(scope="module")
def client():
    app = create_app({"TESTING": True})
    return app.test_client()


def in_html(needle: str, html: str) -> bool:
    """Vérifie qu'un texte figure dans la page.

    Jinja échappe l'apostrophe en ``&#39;`` : on compare donc sur la version
    échappée, sinon les assertions échoueraient sur les titres accentués.
    """
    return str(escape(needle)) in html


# ── Données ──────────────────────────────────────────────────────────────── #


def test_slugs_uniques():
    assert len(PROJECTS_BY_SLUG) == len(PROJECTS)


def test_dates_et_versions_coherentes():
    for project in PROJECTS:
        # Une version ne peut pas précéder la date de création du projet.
        if project.versions:
            assert project.latest_version.date >= project.date
        # Les versions sont proposées de la plus ancienne à la plus récente.
        dates = [v.date for v in project.versions]
        assert dates == sorted(dates)


def test_chaque_projet_a_au_moins_un_lien():
    for project in PROJECTS:
        assert project.links, f"{project.slug} n'a ni site, ni dépôt, ni vidéo"


@pytest.mark.parametrize("project", PROJECTS, ids=lambda p: p.slug)
def test_images_presentes(project):
    assert project.image, f"{project.slug} n'a pas d'image"
    path = f"app/static/img/{project.image}"
    with open(path, "rb") as handle:
        assert handle.read(4) == b"RIFF", f"{project.image} n'est pas un WebP"


def test_toutes_les_icones_existent():
    """Évite le piège : une clé d'icône mal orthographiée lève une KeyError
    au moment du rendu, pas au moment de l'import."""
    used: set[str] = set()

    for stat in STATS:
        used.add(stat.icon)
    for fact in FACTS:
        used.add(fact.icon)
    for social in SOCIALS:
        used.add(social.icon)

    manquantes = used - set(ICONS)
    assert not manquantes, f"icônes absentes du jeu : {sorted(manquantes)}"


def test_selecteur_de_theme_present_sur_toutes_les_pages(client):
    """Sur téléphone le rail disparaît : le sélecteur de thème doit rester
    atteignable, sinon le thème sombre serait hors d'atteinte."""
    for url in ("/", "/projets/shinylivingdex"):
        html = client.get(url).get_data(as_text=True)
        assert 'class="theme-fab"' in html, url
        assert "data-theme-toggle" in html, url


def test_un_seul_titre_par_section(client):
    """Régression : chaque section avait un <h2> rendu par la macro et un second
    <h2 class="sr-only"> de secours. Les lecteurs d'écran annonçaient donc le
    même titre deux fois, et aria-labelledby pointait vers le mauvais."""
    import re

    html = client.get("/").get_data(as_text=True)
    titres = [
        re.sub(r"<[^>]+>", "", balise).strip()
        for balise in re.findall(r"<h2[^>]*>(.*?)</h2>", html, re.S)
    ]
    assert len(titres) == len(set(titres)), f"titres dupliqués : {titres}"
    assert set(titres) == {"À propos", "Compétences", "Projets", "Contact"}


def test_chaque_reference_aria_labo_Existe(client):
    """Un aria-labelledby pointant vers un id absent est silencieusement ignoré :
    la section perd alors son nom accessible."""
    import re

    html = client.get("/").get_data(as_text=True)
    ids = set(re.findall(r'id="([^"]+)"', html))
    for reference in re.findall(r'aria-labelledby="([^"]+)"', html):
        for cible in reference.split():
            assert cible in ids, f"aria-labelledby={cible} ne correspond à aucun id"


def test_les_icones_ne_sont_pas_echappees(client):
    """Régression : sans Markup, Jinja affiche le code SVG en clair."""
    html = client.get("/").get_data(as_text=True)
    assert "&lt;svg" not in html
    assert "<svg" in html


def test_bouton_de_theme_a_bien_ses_deux_icones(client):
    """Régression : ``Markup + str`` échappait les ``<span>`` du sélecteur de
    thème, qui se retrouvait sans icône visible."""
    for url in ("/", "/projets/shinylivingdex"):
        html = client.get(url).get_data(as_text=True)
        assert "&lt;span class=" not in html, f"{url}: balise échappée"
        assert html.count('data-theme-icon="light"') == 2, url
        assert html.count('data-theme-icon="dark"') == 2, url


def test_groupes_de_competences_coherents():
    keys = [g.key for g in SKILL_GROUPS]
    assert len(keys) == len(set(keys))
    for group in SKILL_GROUPS:
        assert group.skills, f"{group.key} est vide"
        assert all(1 <= s.level <= 3 for s in group.skills)


def test_parcours_et_passions_non_vides():
    assert len(JOURNEY) >= 3
    assert all(PASSIONS)
    assert PROFILE.email == SOCIALS[0].value


def test_chaque_etape_du_parcours_a_un_niveau():
    """Sans niveau d'étude, le parcours ne dit pas ce que valent les diplômes."""
    for step in JOURNEY:
        assert step.level, f"{step.title} n'a pas de niveau"
        assert step.level.startswith("Bac"), f"niveau inattendu : {step.level!r}"


def test_annees_du_parcours_completes(client):
    """Régression : une étape affichait « 2025 » au lieu de « 2024 — 2025 »,
    la première moitié de la période ayant disparu."""
    for step in JOURNEY:
        assert re.match(r"^\d{4}\s+—\s+\d{4}$", step.years), step.years

    html = client.get("/").get_data(as_text=True)
    for step in JOURNEY:
        assert step.years in html, f"{step.years} absent de la page"


# ── Filtres ──────────────────────────────────────────────────────────────── #


def test_filtre_par_statut():
    actifs = filter_projects(PROJECTS, status="actif")
    assert actifs
    assert all(p.status == "actif" for p in actifs)


def test_filtre_combine():
    resultat = filter_projects(PROJECTS, status="actif", year="2025")
    assert all(p.status == "actif" and p.year == "2025" for p in resultat)


def test_filtre_sans_resultat():
    assert filter_projects(PROJECTS, status="actif", year="1999") == []


# ── Pages ────────────────────────────────────────────────────────────────── #


def test_accueil(client):
    response = client.get("/")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert in_html(PROFILE.full_name, html)
    assert "topography.svg" in html


@pytest.mark.parametrize("url", ["/", "/?status=actif", "/?year=2025", "/?tech=Python",
                                 "/?status=inactif&year=2023&tech=JavaScript", "/?page=2"])
def test_page_accueil_avec_filtres(client, url):
    assert client.get(url).status_code == 200


def test_parametres_inconnus_retombent_sur_all(client):
    """Une URL bricölée ne doit ni planter, ni altérer la grille."""
    reference = client.get("/partials/projects").get_data(as_text=True)
    bricolee = client.get(
        "/partials/projects?status=inexistant&year=3000&tech=<script>"
    ).get_data(as_text=True)

    # Tous les filtres invalides sont ignorés : le rendu est celui sans filtre.
    assert bricolee == reference
    assert "<script>" not in bricolee


@pytest.mark.parametrize("project", PROJECTS, ids=lambda p: p.slug)
def test_page_projet(client, project):
    response = client.get(f"/projets/{project.slug}")
    assert response.status_code == 200
    assert in_html(project.title, response.get_data(as_text=True))


def test_projet_inconnu_donne_404(client):
    assert client.get("/projets/nexiste-pas").status_code == 404


# ── Fragments HTMX ───────────────────────────────────────────────────────── #


@pytest.mark.parametrize("group", SKILL_GROUPS, ids=lambda g: g.key)
def test_toutes_les_competences_sont_sur_la_page(client, group):
    """Les groupes sont rendus en bandeaux : aucun ne doit dépendre d'un clic
    pour être lu, et chacun porte bien son titre et son résumé."""
    html = client.get("/").get_data(as_text=True)
    assert in_html(group.label, html)
    assert in_html(group.summary, html)
    for skill in group.skills:
        assert in_html(skill.name, html)


def test_ancien_fragment_competences_supprime(client):
    """Le fragment existait pour les onglets ; il n'a plus de rôle."""
    assert client.get("/partials/skills/interfaces").status_code == 404


@pytest.mark.parametrize(
    ("params", "expected"),
    [
        ({}, "/"),
        ({"status": "actif"}, "/?status=actif"),
        ({"status": "actif", "year": "2025", "tech": "React"},
         "/?status=actif&year=2025&tech=React"),
        ({"status": "all", "year": "all", "tech": "all"}, "/"),
        ({"status": "actif", "page": "2"}, "/?status=actif&page=2"),
        # Les valeurs invalides retombent sur « all », donc disparaissent de l'URL.
        ({"status": "inexistant", "year": "3000"}, "/"),
    ],
)
def test_url_canonique_poussee_par_le_serveur(client, params, expected):
    """L'URL affichée doit rester partageable et rejouer la même sélection.

    Régression : avec ``hx-push-url="true"``, HTMX poussait l'adresse interne du
    fragment — partager le lien renvoyait un bout de HTML au lieu de la page.
    """
    response = client.get("/partials/projects", query_string=params)
    assert response.status_code == 200
    assert response.headers["HX-Push-Url"] == expected


def test_fragment_projets_filtre(client):
    response = client.get("/partials/projects?status=inactif")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    inactifs = [p for p in PROJECTS if p.status == "inactif"]
    assert in_html(inactifs[0].title, html)
    assert "Actif" not in html


def test_compteur_de_resultats_dans_le_fragment(client):
    """Le compteur doit être rafraîchi par l'échange HTMX : il vit dans le
    fragment, pas dans le formulaire."""
    html = client.get("/partials/projects?status=inactif").get_data(as_text=True)
    attendu = len([p for p in PROJECTS if p.status == "inactif"])
    assert f'<strong>{attendu}</strong> projet' in html


def test_fragment_projets_vide(client):
    """Aucun résultat doit rester une page valide avec une piste, pas une erreur."""
    # QueenChat est le seul projet Flutter, et il est actif : croiser les deux
    # filtres ne peut rien donner.
    response = client.get("/partials/projects?status=inactif&tech=Flutter")
    assert response.status_code == 200
    assert "Réinitialiser les filtres" in response.get_data(as_text=True)


@pytest.mark.parametrize("project", PROJECTS, ids=lambda p: p.slug)
def test_fragment_fiche_projet(client, project):
    response = client.get(f"/partials/projects/{project.slug}")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert in_html(project.title, html)
    for _, url, _ in project.links:
        assert escape(url) in html


# ── Fichiers publics ─────────────────────────────────────────────────────── #


def test_robots_et_sitemap(client):
    robots = client.get("/robots.txt")
    assert robots.status_code == 200
    assert b"Sitemap" in robots.data

    sitemap = client.get("/sitemap.xml")
    assert sitemap.status_code == 200
    assert sitemap.data.count(b"<url>") == len(PROJECTS) + 1


def test_statique_serti(client):
    for chemin in ("css/style.css", "fonts/fonts.css", "vendor/htmx.min.js",
                   "js/app.js", "img/topography.svg"):
        assert client.get(f"/static/{chemin}").status_code == 200, chemin


def test_pas_de_cache_statique_en_developpement():
    """Régression : un cache de 30 jours appliqué aussi en debug imposait un
    rechargement forcé du navigateur à chaque modification de CSS."""
    debug_app = create_app({"DEBUG": True, "TESTING": True})
    assert debug_app.config["SEND_FILE_MAX_AGE_DEFAULT"] == 0

    prod_app = create_app({"DEBUG": False, "TESTING": True})
    assert prod_app.config["SEND_FILE_MAX_AGE_DEFAULT"] > 0
