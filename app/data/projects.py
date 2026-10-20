"""Catalogue des projets.

Chaque projet porte ses versions successives, ce qui permet d'afficher un
historique de développement plutôt qu'une simple liste.

Fonctions de filtrage utilisées par les routes HTMX : le tri, le filtrage par
statut et par technologie sont faits en Python, pas en JavaScript.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date
from typing import Literal

Status = Literal["actif", "inactif"]


@dataclass(frozen=True, slots=True)
class Version:
    label: str
    date: date
    changes: tuple[str, ...]
    technologies: tuple[str, ...] = ()
    url: str | None = None
    repo: str | None = None
    video: str | None = None

    @property
    def date_label(self) -> str:
        return self.date.strftime("%b %Y").replace(".", "")


@dataclass(frozen=True, slots=True)
class Project:
    slug: str
    title: str
    summary: str
    technologies: tuple[str, ...]
    date: date
    status: Status
    image: str | None = None
    url: str | None = None
    repo: str | None = None
    video: str | None = None
    versions: tuple[Version, ...] = ()

    # -- champs affichés ---------------------------------------------------- #

    @property
    def year(self) -> str:
        return str(self.date.year)

    @property
    def date_label(self) -> str:
        return self.date.strftime("%b %Y").replace(".", "")

    @property
    def status_label(self) -> str:
        return "En ligne" if self.status == "actif" else "Archivé"

    @property
    def latest_version(self) -> Version | None:
        """Version la plus récente de l'historique, s'il existe."""
        return max(self.versions, key=lambda version: version.date, default=None)

    @property
    def links(self) -> tuple[tuple[str, str, str], ...]:
        """(libellé, url, icône) pour chaque lien externe du projet."""
        out: list[tuple[str, str, str]] = []
        if self.url:
            out.append(("Voir le site", self.url, "external"))
        if self.repo:
            out.append(("Code source", self.repo, "github"))
        if self.video:
            out.append(("Vidéo", self.video, "play"))
        return tuple(out)


def _d(value: str) -> date:
    return date.fromisoformat(value)


PROJECTS: tuple[Project, ...] = (
    # ------------------------------------------------------------------ 2026
    Project(
        slug="flow-yoga",
        title="Flow-yoga",
        summary="Landing page pour un projet client de yoga en ligne.",
        technologies=("Next.js", "PHP", "Tailwind CSS"),
        date=_d("2026-05-15"),
        status="inactif",
        image="flow-yoga.webp",
        video="https://youtu.be/4RyzZ5tAV5s",
    ),
    Project(
        slug="queenchat-mobile",
        title="QueenChat",
        summary=(
            "Ma première expérience de développement d'application mobile, "
            "conçue et écrite en Flutter et Dart."
        ),
        technologies=("Flutter", "Dart", "Mobile"),
        date=_d("2026-02-03"),
        status="actif",
        image="queenchat.webp",
        repo="https://github.com/doniphane/DEV-MOBILE-queenchatmobile",
        video="https://youtu.be/61yANF92EEg",
        versions=(
            Version(
                label="v1.01",
                date=_d("2026-02-03"),
                changes=(
                    "Nouvelle UI/UX sur l'interface",
                ),
                technologies=("Flutter", "Dart", "Mobile"),
                repo="https://github.com/doniphane/DEV-MOBILE-queenchatmobile",
                video="https://youtu.be/61yANF92EEg",
            ),
        ),
    ),
    Project(
        slug="devchallenge-pokedex-2026-week-04",
        title="DevChallenge — Pokédex 2026 Week 04",
        summary=(
            "Défi hebdomadaire proposé par Yohandev :Construire un Pokédex "
            "alimenté par l'API officielle Pokémon, avec recherche et filtres."
        ),
        technologies=("React", "Tailwind CSS", "API Pokémon"),
        date=_d("2026-02-03"),
        status="actif",
        image="pokedex.webp",
        url="https://dev-challenge-pokedex-2026-week-04-lei6dmqwh.vercel.app/",
        repo="https://github.com/doniphane/dev-challenge-pokedex--2026-WEEK-04",
    ),
    Project(
        slug="devchallenge-qualite-eau",
        title="DevChallenge — Qualité de l'eau",
        summary=(
            "Suivi de la qualité de l'eau par commune à partir de l'API "
            "gouvernementale. Un deuxième défi de Yohandev, relevé de bout en bout."
        ),
        technologies=("Vue.js", "Tailwind CSS", "API gouvernementale"),
        date=_d("2025-12-16"),
        status="actif",
        image="qualite-eau.webp",
        url="https://dev-challenge-qualite-eau.vercel.app/",
        repo="https://github.com/doniphane/devChallenge-qualit--eau",
        video="https://youtu.be/VYv7INsB7Cg",
    ),
    # ------------------------------------------------------------------ 2025
    Project(
        slug="blog-team-kuroizana",
        title="Blog de la Team Kuroizana",
        summary=(
            "Plateforme de quiz en ligne pour faire passer des quiz à des élèves : "
            "création des questionnaires, attribution et suivi des résultats."
        ),
        technologies=("Next.js", "Tailwind CSS", "PostgreSQL"),
        date=_d("2025-11-21"),
        status="inactif",
        image="kuroizana-blog.webp",
        url="https://teamkuroizanablog.vercel.app/",
    ),
    Project(
        slug="acadyo-quizz",
        title="Acadyo Quizz",
        summary=(
            "Plateforme de quiz en ligne pour faire passer des quiz à des élèves, "
            "avec back-end Symfony et base MySQL."
        ),
        technologies=("React", "Tailwind CSS", "MySQL", "Symfony"),
        date=_d("2025-10-01"),
        status="inactif",
        image="acadyo-quizz.webp",
        url="https://acadyoquizz.noelsonnelly.xyz/login",
        video="https://www.youtube.com/watch?v=-urkSHoTkkI",
    ),
    Project(
        slug="shinylivingdex",
        title="ShinyLivingdex",
        summary=(
            "Mon Pokédex personnel : compter et suivre mes shinies capturés. "
            "Seconde version du projet, après migration de la base de données."
        ),
        technologies=("Next.js", "Tailwind CSS", "PostgreSQL"),
        date=_d("2025-09-13"),
        status="actif",
        image="shiny-livingdex.webp",
        url="https://pokelivingdex.noelson-elisa.com/",
        video="https://youtu.be/swb4gEdYtEg",
        versions=(
            Version(
                label="v1.0",
                date=_d("2024-07-20"),
                changes=(
                    "Première version du Pokédex",
                    "Interface de base pour compter les shinies",
                    "Compteurs et fiches Pokémon",
                ),
                technologies=("Next.js", "Tailwind CSS", "Supabase"),
                url="https://v0-pokemon-website-delta.vercel.app/",
                repo="https://github.com/doniphane/pokedex-shiny-",
            ),
            Version(
                label="v2.0",
                date=_d("2025-09-13"),
                changes=(
                    "Migration de Supabase vers PostgreSQL",
                    "Interface repensée et navigation plus rapide",
                    "Ajout des fonctionnalités avancées",
                    "Optimisation des performances de chargement",
                ),
                technologies=("Next.js", "Tailwind CSS", "PostgreSQL"),
                url="https://pokelivingdex.noelson-elisa.com/",
                video="https://youtu.be/swb4gEdYtEg",
            ),
        ),
    ),
    Project(
        slug="compressimgs",
        title="Compressimgs",
        summary=(
            "Application web de compression d'images : convertir un grand volume "
            "d'images en un temps record, entièrement dans le navigateur."
        ),
        technologies=("React", "Tailwind CSS"),
        date=_d("2025-08-08"),
        status="inactif",
        image="compressimgs.webp",
        url="https://compressimg.noelson-elisa.com/",
        video="https://www.youtube.com/watch?v=kiCCLAqtImg",
        versions=(
            Version(
                label="v1.0",
                date=_d("2025-08-08"),
                changes=(
                    "Première version de l'application",
                    "Compression par lot d'images",
                    "Réglages de qualité et de format de sortie",
                ),
                technologies=("React", "Tailwind CSS"),
                url="https://compressimg.noelson-elisa.com/",
                video="https://www.youtube.com/watch?v=kiCCLAqtImg",
            ),
            Version(
                label="v2.0",
                date=_d("2025-08-08"),
                changes=(
                    "Interface de compression revue",
                    "Traitement en masse plus rapide",
                    "Ajout des fonctionnalités avancées",
                ),
                technologies=("React", "Tailwind CSS"),
                url="https://compressimg.noelson-elisa.com/",
                video="https://www.youtube.com/watch?v=kiCCLAqtImg",
            ),
        ),
    ),
    Project(
        slug="challenge-ai-365",
        title="ChallengeAI365Days",
        summary=(
            "Un défi personnel : publier une image générée chaque jour pendant un "
            "an. Un workflow n8n enchaîne la génération et la publication "
            "automatisée."
        ),
        technologies=("React", "Tailwind CSS", "n8n"),
        date=_d("2025-07-17"),
        status="inactif",
        image="challenge-ai-365.webp",
        url="https://challenge365days.noelsonnelly.xyz/",
        versions=(
            Version(
                label="v1.0",
                date=_d("2025-07-17"),
                changes=(
                    "Lancement du challenge de 365 jours",
                    "Galerie d'images générées",
                    "Intégration d'un workflow n8n",
                    "Publication automatique quotidienne",
                ),
                technologies=("React", "Tailwind CSS", "n8n"),
                url="https://challenge365days.noelsonnelly.xyz/",
            ),
        ),
    ),
    # ------------------------------------------------------------------ 2024
    Project(
        slug="kuroizana-chat",
        title="Kuroizana-chat",
        summary=(
            "Chat en temps réel pour discuter avec mes amis de CTF : salons, "
            "authentification et diffusion des messages côté serveur."
        ),
        technologies=("PHP", "Tailwind CSS", "MySQL"),
        date=_d("2024-04-15"),
        status="inactif",
        image="kuroizana-chat.webp",
        url="https://kuroizanachat.noelson-elisa.com/",
        repo="https://github.com/doniphane/Kuroizana-chat",
        versions=(
            Version(
                label="v1.0",
                date=_d("2024-04-15"),
                changes=(
                    "Application de chat en temps réel",
                    "Interface utilisateur avec Tailwind CSS",
                    "Base de données MySQL",
                    "Système d'authentification",
                ),
                technologies=("PHP", "Tailwind CSS", "MySQL"),
                url="https://kuroizanachat.noelson-elisa.com/",
                repo="https://github.com/doniphane/Kuroizana-chat",
            ),
        ),
    ),
    Project(
        slug="ghibli-app-react",
        title="GhibliApp",
        summary=(
            "Application React qui consomme l'API publique Studio Ghibli pour "
            "afficher, trier et mettre en favori les films du studio."
        ),
        technologies=("React", "Tailwind CSS", "API REST"),
        date=_d("2024-02-10"),
        status="actif",
        image="ghibli-app.webp",
        url="https://ghibli-app-react.onrender.com/",
        repo="https://github.com/doniphane/ghibli-app-React",
        versions=(
            Version(
                label="v1.0",
                date=_d("2024-02-10"),
                changes=(
                    "Application React complète",
                    "Intégration de l'API Studio Ghibli",
                    "Système de favoris",
                    "Recherche et tri des films",
                ),
                technologies=("React", "Tailwind CSS"),
                url="https://ghibli-app-react.onrender.com/",
                repo="https://github.com/doniphane/ghibli-app-React",
            ),
        ),
    ),
    Project(
        slug="pokedex-shiny",
        title="Pokédex Shiny",
        summary=(
            "Premier projet du Pokédex : une page web pour compter mes shinies "
            "capturés, les toutes premières sur une base Supabase."
        ),
        technologies=("Next.js", "Tailwind CSS", "Supabase"),
        date=_d("2024-07-20"),
        status="inactif",
        image="pokedex.webp",
        url="https://v0-pokemon-website-delta.vercel.app/",
        repo="https://github.com/doniphane/pokedex-shiny-",
    ),
    # ------------------------------------------------------------------ 2023
    Project(
        slug="world-explorer",
        title="WorldExplorer",
        summary=(
            "Explorateur de pays alimenté par l'API REST Countries : drapeaux, "
            "capitales et régions du monde."
        ),
        technologies=("React", "CSS", "JavaScript", "HTML"),
        date=_d("2023-12-05"),
        status="actif",
        image="world-explorer.webp",
        url="https://worldexplorer.onrender.com/",
        repo="https://github.com/doniphane/worldexplorer",
        versions=(
            Version(
                label="v1.0",
                date=_d("2023-12-05"),
                changes=(
                    "Application d'exploration mondiale",
                    "Intégration de l'API REST Countries",
                    "Affichage des drapeaux et informations pays",
                    "Interface responsive",
                ),
                technologies=("React", "CSS", "JavaScript", "HTML"),
                url="https://worldexplorer.onrender.com/",
                repo="https://github.com/doniphane/worldexplorer",
            ),
        ),
    ),
    Project(
        slug="openlibrary",
        title="Ma bibliothèque",
        summary=(
            "Bibliothèque virtuelle construite sur l'API OpenLibrary : recherche "
            "d'ouvrages, couverture et fiche détaillée."
        ),
        technologies=("React", "CSS", "JavaScript"),
        date=_d("2023-11-15"),
        status="actif",
        image="openlibrary.webp",
        url="https://doniphane.github.io/Ma-bibliotheque/",
        repo="https://github.com/doniphane/openlibrary/",
        versions=(
            Version(
                label="v1.0",
                date=_d("2023-11-15"),
                changes=(
                    "Bibliothèque virtuelle",
                    "Intégration de l'API OpenLibrary",
                    "Recherche de livres",
                    "Interface de consultation",
                ),
                technologies=("HTML", "CSS", "JavaScript"),
                url="https://doniphane.github.io/Ma-bibliotheque/",
                repo="https://github.com/doniphane/Ma-bibliotheque",
            ),
            Version(
                label="v2.0",
                date=_d("2026-10-01"),
                changes=(
                    "Refonte de toute l'UI/UX du site",
                    "Mise à jour de React vers la dernière version",
                ),
                technologies=("React", "CSS", "JavaScript"),
                url="https://doniphane.github.io/Ma-bibliotheque/",
                repo="https://github.com/doniphane/Ma-bibliotheque",
            ),
        ),
    ),
    Project(
        slug="videotheque-ghibli",
        title="Vidéothèque Ghibli",
        summary=(
            "Récupération des films via une API, projet réalisé en formation "
            "pour compléter la bibliothèque."
        ),
        technologies=("HTML", "Tailwind CSS", "JavaScript"),
        date=_d("2023-10-01"),
        status="actif",
        image="videotheque-ghibli.webp",
        url="https://doniphane.github.io/Ma-videotech/",
        repo="https://github.com/doniphane/Ma-videotech",
    ),
    Project(
        slug="random-user",
        title="RandomUser",
        summary=(
            "Générateur de profils utilisateurs à partir de l'API RandomUser, "
            "projet de formation."
        ),
        technologies=("HTML", "CSS", "JavaScript"),
        date=_d("2023-09-12"),
        status="actif",
        image="randomuser.webp",
        url="https://doniphane.github.io/Randomuser-api/",
        repo="https://github.com/doniphane/Randomuser-api",
        versions=(
            Version(
                label="v1.0",
                date=_d("2023-09-12"),
                changes=(
                    "Générateur d'utilisateurs aléatoires",
                    "Intégration de l'API RandomUser",
                    "Affichage des profils utilisateurs",
                    "Projet de formation",
                ),
                technologies=("HTML", "CSS", "JavaScript"),
                url="https://doniphane.github.io/Randomuser-api/",
                repo="https://github.com/doniphane/Randomuser-api",
            ),
        ),
    ),
    Project(
        slug="calendrier-interactif",
        title="Calendrier interactif",
        summary=(
            "Agenda web : création d'un calendrier mensuel, gestion d'événements "
            "et affichage des rendez-vous."
        ),
        technologies=("HTML", "CSS", "JavaScript", "PHP"),
        date=_d("2023-08-22"),
        status="actif",
        image="calendrier.webp",
        repo="https://github.com/doniphane/Agenda",
        versions=(
            Version(
                label="v1.0",
                date=_d("2023-08-22"),
                changes=(
                    "Calendrier interactif complet",
                    "Gestion d'événements",
                    "Interface utilisateur intuitive",
                    "Back-end PHP",
                ),
                technologies=("HTML", "CSS", "JavaScript", "PHP"),
                repo="https://github.com/doniphane/Agenda",
            ),
        ),
    ),
    Project(
        slug="tropizzcartour",
        title="Tropizzcartour",
        summary="Site fictif de location de voiture, avec catalogue et réservation.",
        technologies=("HTML", "Tailwind CSS", "JavaScript", "PHP"),
        date=_d("2023-07-18"),
        status="inactif",
        image="tropizzcartour.webp",
        repo="https://github.com/doniphane/Tropizcartours",
        versions=(
            Version(
                label="v1.0",
                date=_d("2023-07-18"),
                changes=(
                    "Site de location de voiture",
                    "Interface avec Tailwind CSS",
                    "Système de réservation",
                    "Back-end PHP",
                ),
                technologies=("HTML", "Tailwind CSS", "JavaScript", "PHP"),
                repo="https://github.com/doniphane/Tropizcartours",
            ),
        ),
    ),
    Project(
        slug="cybergardien",
        title="Cybergardien",
        summary=(
            "Site d'une association fictive de cybersécurité : pages "
            "institutionnelles et contenus de sensibilisation."
        ),
        technologies=("HTML", "CSS", "JavaScript"),
        date=_d("2023-06-25"),
        status="actif",
        image="cybergardien.webp",
        url="https://doniphane.github.io/Cyber-Gardien-Projet-Assos-Fictif-/",
        repo="https://github.com/doniphane/Cyber-Gardien-Projet-Assos-Fictif-",
        versions=(
            Version(
                label="v1.0",
                date=_d("2023-06-25"),
                changes=(
                    "Site d'association fictive",
                    "Thème cybersécurité",
                    "Interface responsive",
                    "Pages institutionnelles",
                ),
                technologies=("HTML", "CSS", "JavaScript"),
                url="https://doniphane.github.io/Cyber-Gardien-Projet-Assos-Fictif-/",
                repo="https://github.com/doniphane/Cyber-Gardien-Projet-Assos-Fictif-",
            ),
        ),
    ),
    Project(
        slug="rest-country",
        title="RestCountry",
        summary=(
            "Premier projet d'appel API : récupération et affichage des drapeaux "
            "du monde, entièrement en JavaScript."
        ),
        technologies=("HTML", "CSS", "JavaScript"),
        date=_d("2023-05-30"),
        status="actif",
        image="restcountry.webp",
        url="https://doniphane.github.io/FLag",
        repo="https://github.com/doniphane/FLag",
        versions=(
            Version(
                label="v1.0",
                date=_d("2023-05-30"),
                changes=(
                    "Application de drapeaux",
                    "Intégration de l'API REST Countries",
                    "Affichage des drapeaux par pays",
                    "Interface simple et efficace",
                ),
                technologies=("HTML", "CSS", "JavaScript"),
                url="https://doniphane.github.io/FLag",
                repo="https://github.com/doniphane/FLag",
            ),
        ),
    ),
)


# --------------------------------------------------------------------------- #
# Index & helpers
# --------------------------------------------------------------------------- #

PROJECTS_BY_SLUG: dict[str, Project] = {p.slug: p for p in PROJECTS}

SORTED_PROJECTS: tuple[Project, ...] = tuple(
    sorted(PROJECTS, key=lambda p: p.date, reverse=True)
)

YEARS: tuple[str, ...] = tuple(sorted({p.year for p in PROJECTS}, reverse=True))

STATUS_FILTERS: tuple[tuple[str, str], ...] = (
    ("all", "Tous"),
    ("actif", "En ligne"),
    ("inactif", "Archivés"),
)


def technologies_used() -> tuple[str, ...]:
    """Technos présentes dans le catalogue, par ordre d'apparition."""
    seen: dict[str, None] = {}
    for project in SORTED_PROJECTS:
        for tech in project.technologies:
            seen.setdefault(tech, None)
    return tuple(seen)


def filter_projects(
    projects: Iterable[Project],
    *,
    status: str = "all",
    year: str = "all",
    tech: str = "all",
) -> list[Project]:
    """Filtre le catalogue. Utilisé par la route HTMX des filtres."""
    result = list(projects)
    if status != "all":
        result = [p for p in result if p.status == status]
    if year != "all":
        result = [p for p in result if p.year == year]
    if tech != "all":
        result = [p for p in result if tech in p.technologies]
    return result


def get_project(slug: str) -> Project | None:
    return PROJECTS_BY_SLUG.get(slug)
