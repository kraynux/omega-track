# Copyright (c) 2026 kraynux - Licence MIT
"""Bandeau texte OMEGA-TRACK affiche en haut de screens/home.py (logo fourni
par l'utilisateur, voir ~/DEV/TRACK/ascii.txt, section "MENU GENERAL" -
mêmes lettres que le bandeau de l'ecran de demarrage, sans le cadre de
boite : juste les 3 lignes de lettres, meme choix que omega-check pour son
badge d'accueil compact - confirme par l'utilisateur apres un aller-retour
("comme les autres [outils], c'est a retirer" : le cadre ajoute puis
retire dans la meme session, revenu a ce choix initial de la Phase 11).
Bytes extraits verbatim vers resources/ascii/wordmark.txt (source commune
avec widgets/splash_hero.py, pas de duplication a la main du meme art
dans deux fichiers).

Couleur par jetons de theme Rich/Textual (`$accent`=vif, `$foreground`
=clair) directement dans le markup - reactif au changement de theme."""
from __future__ import annotations

from functools import lru_cache
from importlib import resources

from textual.widgets import Static

_LINE_COLORS = ("$accent", "$foreground", "$accent")


@lru_cache(maxsize=1)
def _load_markup() -> str:
    raw = (resources.files("omega_track") / "resources" / "ascii" / "wordmark.txt").read_text(encoding="utf-8")
    lines = raw.splitlines()
    return "\n".join(f"[{color}]{line}[/]" for color, line in zip(_LINE_COLORS, lines, strict=True))


class HomeWordmark(Static):
    """Bandeau decoratif centre en haut de screens/home.py."""

    def __init__(self) -> None:
        super().__init__(_load_markup(), classes="omega-home-wordmark")
