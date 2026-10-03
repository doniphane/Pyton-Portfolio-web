"""Contenu éditorial du portfolio : identité, parcours, compétences, passions.

Toute la donnée affichée par les templates vit ici, sous forme de structures
simples et immuables. Les templates n'ont qu'à les parcourir.
"""

from __future__ import annotations

from dataclasses import dataclass

# --------------------------------------------------------------------------- #
# Identité
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class Social:
    label: str
    value: str
    url: str
    icon: str


@dataclass(frozen=True, slots=True)
class Profile:
    first_name: str
    last_name: str
    initials: str
    role: str
    roles: tuple[str, ...]
    location: str
    email: str
    tagline: str
    bio: tuple[str, ...]
    cv_filename: str

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


PROFILE = Profile(
    first_name="Trules",
    last_name="Doniphane",
    initials="DT",
    role="Concepteur Développeur d'Applications",
    roles=(
        "Concepteur Développeur d'Applications",
        "Développeur Web / Web Mobile",
        "Passionné de Cybersécurité",
    ),
    location="Plate Saint-Leu, La Réunion",
    email="trulesdoniphane974@gmail.com",
    tagline=(
        "Développeur passionné spécialisé dans la création d'applications web "
        "modernes. J'allie créativité technique et innovation pour donner vie à "
        "vos projets digitaux."
    ),
    bio=(
        (
            "Je m'appelle Doniphane Trules, Concepteur Développeur d'Applications "
            "titulaire de mon diplôme, passionné par la technologie depuis mon plus "
            "jeune âge. Issu d'un BTS en électronique et communication, j'ai fait de "
            "ma reconversion dans le développement une véritable voie "
            "d'épanouissement."
        ),
        (
            "Aujourd'hui, je développe des sites et des logiciels pour moi-même, mon "
            "entourage et toutes les personnes qui en ont besoin. J'allie créativité "
            "technique et polyvalence pour apporter des solutions concrètes et utiles "
            "au quotidien."
        ),
    ),
    cv_filename="CV_Doniphane_Trules.pdf",
)


# --------------------------------------------------------------------------- #
# Chiffres clés
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class Stat:
    value: str
    label: str
    icon: str


STATS: tuple[Stat, ...] = (
    Stat("20+", "Technologies", "code"),
    Stat("3", "Diplômes", "graduation-cap"),
    Stat("100%", "Autonome", "compass"),
)


# --------------------------------------------------------------------------- #
# Parcours
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class JourneyStep:
    years: str
    title: str
    level: str  # diplôme visé : « Bac », « Bac +2 », « Bac +3/+4 »
    place: str | None
    description: str

    @property
    def level_rank(self) -> int:
        """1 = Bac, 2 = Bac +2, 3 = Bac +3/+4.

        Dérivé du libellé plutôt que saisi à part, pour que les deux ne
        puissent pas diverger. Sert à teinter la pastille de niveau.
        """
        if "+3" in self.level:
            return 3
        if "+2" in self.level:
            return 2
        return 1


JOURNEY: tuple[JourneyStep, ...] = (
    JourneyStep(
        years="2024 — 2025",
        title="Concepteur Développeur d'Applications",
        level="Bac +3/+4",
        place="Ariane Formation",
        description=(
            "J'ai approfondi mes compétences en développement et élargi mon "
            "expertise pour concevoir des applications complètes de A à Z."
        ),
    ),
    JourneyStep(
        years="2022 — 2023",
        title="Développeur Web & Web Mobile",
        level="Bac +2",
        place="Institut de Formation de la Réunion (IFR)",
        description="Bases solides acquises en développement front-end et back-end.",
    ),
    JourneyStep(
        years="2020 — 2022",
        title="BTS Électronique et Communication",
        level="Bac +2",
        place=None,
        description=(
            "Compréhension approfondie des systèmes informatiques et approche "
            "analytique des problèmes techniques."
        ),
    ),
    JourneyStep(
        years="2019 — 2020",
        title="Bac Pro Sciences Numériques",
        level="Bac",
        place="Lycée de Trois Bassins, La Réunion",
        description=(
            "Initiation aux technologies numériques et bases de ma reconversion "
            "vers le développement web."
        ),
    ),
)


# --------------------------------------------------------------------------- #
# Compétences — 3 groupes, rendus en bandeaux par la page
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class Skill:
    name: str
    level: int  # 1 = notions, 3 = maîtrise


@dataclass(frozen=True, slots=True)
class SkillGroup:
    key: str
    label: str
    summary: str
    skills: tuple[Skill, ...]


SKILL_GROUPS: tuple[SkillGroup, ...] = (
    SkillGroup(
        key="interfaces",
        label="Front-end",
        summary=(
            ""
        ),
        skills=(
            Skill("HTML", 3),
            Skill("CSS", 3),
            Skill("JavaScript", 2),
            Skill("Jinja2", 3),
            Skill("HTMX", 3),
            Skill("Tailwind CSS", 3),
            Skill("React / Next.js", 2),
            Skill("Flutter", 2),
        ),
    ),
    SkillGroup(
        key="backend",
        label="Back-end",
        summary=(
            ""
        ),
        skills=(
            Skill("Python", 3),
            Skill("Flask", 3),
            Skill("API REST", 3),
            Skill("PostgreSQL", 2),
            Skill("PHP", 2),
            Skill("Symfony / Laravel", 2),
            Skill("Node.js", 2),
        ),
    ),
    SkillGroup(
        key="outils",
        label="Outils & systèmes",
        summary="",
        skills=(
            Skill("Linux", 2),
            Skill("Git / GitHub", 3),
            Skill("Windows", 2),
            Skill("MySQL / MariaDB", 2),
            Skill("MongoDB", 2),
            Skill("Supabase", 2),
            Skill("WordPress", 2),
            Skill("IA / LLM", 2),
            Skill("Docker", 4)
        ),
    ),
)

#: Index par clé, pour le routeur. Les bandeaux de la section « Compétences »
#: parcourent ``SKILL_GROUPS`` directement et n'en ont pas besoin.
SKILL_GROUPS_BY_KEY: dict[str, SkillGroup] = {g.key: g for g in SKILL_GROUPS}


# --------------------------------------------------------------------------- #
# Passions & coordonnées
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class Passion:
    title: str
    description: str
    tags: tuple[str, ...]


PASSIONS: tuple[Passion, ...] = (
    Passion(
        title="Création vidéo",
        description=(
            "Je produis et monte des vidéos pour partager mes projets et ma passion "
            "avec ma communauté."
        ),
        tags=("Montage", "Présentation"),
    ),
    Passion(
        title="Réparation informatique",
        description=(
            "Passionné par le matériel, je répare et optimise des ordinateurs : "
            "assemblage de PC, diagnostic de pannes."
        ),
        tags=("Assemblage PC", "Diagnostic", "Optimisation"),
    ),
    Passion(
        title="Intelligence artificielle",
        description=(
            "Je m'intéresse de près à l'IA et à ses applications pour intégrer des "
            "solutions intelligentes dans mes projets."
        ),
        tags=("Automation", "Chatbots", "Création assistée"),
    ),
)


@dataclass(frozen=True, slots=True)
class Fact:
    label: str
    value: str
    icon: str


FACTS: tuple[Fact, ...] = (
    Fact("Localisation", PROFILE.location, "map-pin"),
    Fact("Mobilité", "Full remote France & DOM", "compass"),
    Fact("Langues", "Français, Anglais technique", "globe"),
    Fact("Disponibilité", "Projets freelance & CDI", "clock"),
)


SOCIALS: tuple[Social, ...] = (
    Social(
        label="Email",
        value=PROFILE.email,
        url=f"mailto:{PROFILE.email}",
        icon="mail",
    ),
    Social(
        label="GitHub",
        value="github.com/doniphane",
        url="https://github.com/doniphane",
        icon="github",
    ),
    Social(
        label="LinkedIn",
        value="in/doniphane-trules",
        url="https://www.linkedin.com/in/doniphane-trules-970638318/",
        icon="linkedin",
    ),
    Social(
        label="YouTube",
        value="@noelson9749",
        url="https://www.youtube.com/@noelson9749/videos",
        icon="youtube",
    ),
)


# --------------------------------------------------------------------------- #
# Colophon — le site parle de lui-même
# --------------------------------------------------------------------------- #


@dataclass(frozen=True, slots=True)
class StackItem:
    name: str
    role: str


STACK: tuple[StackItem, ...] = (
    StackItem("Python 3.12", "Application"),
    StackItem("Flask", "Serveur WSGI"),
    StackItem("Jinja2", "Templates"),
    StackItem("HTMX", "Hypermedia"),
    StackItem("CSS", "Styles maison"),
    StackItem("Gunicorn", "Exécution en production"),
)
