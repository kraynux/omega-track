# Copyright (c) 2026 kraynux - Licence MIT
"""Parent argparse partage par toutes les sous-commandes (Phase 9) -
prive (meme convention que application/orchestrators/_context.py).

`--json` doit etre declare sur CHAQUE sous-parseur feuille, jamais sur
son parent : argparse route les arguments restants uniquement vers le
sous-parseur actif une fois `add_parser()` selectionne, un parent ne
peut pas recevoir un flag place APRES le nom de la sous-commande (bug
reel trouve en testant `target add example.com --json` : "unrecognized
arguments: --json" tant que `--json` restait sur le parseur `target`
plutot que sur `target add` lui-meme) - `parents=[JSON_FLAG]` sur
chaque `add_parser()` evite de repeter cette declaration partout."""
from __future__ import annotations

import argparse

JSON_FLAG = argparse.ArgumentParser(add_help=False)
JSON_FLAG.add_argument("--json", action="store_true", help="sortie JSON machine-readable")
