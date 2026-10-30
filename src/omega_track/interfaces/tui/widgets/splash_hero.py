# Copyright (c) 2026 kraynux - Licence MIT
"""Composition ASCII de l'ecran de demarrage. Logo fourni par l'utilisateur,
voir ~/DEV/TRACK/ascii.txt (legende de couleurs en tete du fichier) - motif
2D (plusieurs elements decoratifs partagent une meme ligne a des colonnes
differentes : boite LINUX WEB-TRACKER, banniere V1.5, pyramide DNS, schema
de trace, bandeau OMEGA-TRACK), contrairement au logo empile d'omega-check
qui autorise un centrage ligne par ligne (`str.center`). Ici chaque ligne
est chargee et reindentee tabs->espaces (`expandtabs`) mais JAMAIS recentree
individuellement : les positions colonne-a-colonne entre elements sont
signifiantes, seul le bloc entier (largeur = plus longue ligne) est centre
a l'ecran par le conteneur `Center()` de screens/splash.py.

Bytes de l'art extraits verbatim via `sed` depuis ~/DEV/TRACK/ascii.txt vers
resources/ascii/splash.txt (pas de retranscription a la main : art dense en
tabulations/caracteres de dessin de boite, une erreur de recopie serait
facile a manquer a la relecture).

Couleur par jetons de theme Rich/Textual (`$accent`=vif, `$foreground`
=clair) directement dans le markup - pas de couleurs hex figees (reactif au
changement de theme, meme mecanisme que CHECK). Regles fournies par
l'utilisateur (voir legende en tete d'ascii.txt) :
- cadres/"containers" : clair.
- bandeau OMEGA-TRACK (3 lignes, dans sa boite) : vif / clair / vif.
- tagline du bas : les "|" separateurs vifs, les mots clairs.
- nuances de blocs (█▓▒░) : simplifiees en un seul ton clair - une
  gradation Rich par caractere individuel serait impraticable pour un
  element purement decoratif et n'apporte rien de lisible dans un
  terminal reel."""
from __future__ import annotations

from functools import lru_cache
from importlib import resources

from textual.widgets import Static

_TAB_SIZE = 4
"""Verifie empiriquement contre resources/ascii/splash.txt : les lignes 0-2
(bordure/texte/bordure de la boite LINUX WEB-TRACKER) ne s'alignent sur la
meme colonne (31) qu'avec un taquet de 4 - un taquet de 8 (valeur par
defaut usuelle) decale la bordure superieure de 12 colonnes vers la
droite par rapport a son propre contenu (bug signale par l'utilisateur :
"splash ascii decale"). Toutes les lignes du bloc OMEGA-TRACK (index 5-9)
convergent aussi vers la meme longueur avec un taquet de 4, jamais avec 8."""

_WORDMARK_LINE_COLORS: dict[int, str] = {6: "$accent", 7: "$foreground", 8: "$accent"}
"""Index 0-based dans splash.txt des 3 lignes de lettres du bandeau
OMEGA-TRACK (entourees des bordures de boite aux index 5 et 9, coloriees
comme le reste du decor en $foreground)."""

_TAGLINE_INDEX = 21
"""Index 0-based de la ligne "TRACE | IP | OSINT | NETWORKS | EXPORT"."""


def _split_frame(line: str, color: str, frame_char: str = "│") -> str:
    """Ligne du type '│ texte │' -> cadre clair, texte dans `color`."""
    prefix, _, rest = line.partition(frame_char)
    inner, _, suffix = rest.rpartition(frame_char)
    return f"{prefix}[$foreground]{frame_char}[/][{color}]{inner}[/][$foreground]{frame_char}{suffix}[/]"


def _tagline(line: str) -> str:
    """'TRACE | IP | ...' -> mots clairs, '|' vifs."""
    parts = line.split("|")
    colored = [f"[$foreground]{part}[/]" for part in parts]
    return "[$accent]|[/]".join(colored)


@lru_cache(maxsize=1)
def _load_markup() -> str:
    raw = (resources.files("omega_track") / "resources" / "ascii" / "splash.txt").read_text(encoding="utf-8")
    lines = [line.expandtabs(_TAB_SIZE) for line in raw.splitlines()]
    rendered: list[str] = []
    for index, line in enumerate(lines):
        color = _WORDMARK_LINE_COLORS.get(index)
        if color is not None:
            rendered.append(_split_frame(line, color))
        elif index == _TAGLINE_INDEX:
            rendered.append(_tagline(line))
        else:
            rendered.append(f"[$foreground]{line}[/]")
    return "\n".join(rendered)


class SplashHero(Static):
    """Bloc decoratif de l'ecran de demarrage (screens/splash.py)."""

    def __init__(self) -> None:
        super().__init__(_load_markup(), classes="omega-splash-hero")
