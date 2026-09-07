# Copyright (c) 2026 kraynux - Licence MIT
"""Verifie que le domaine reste pur au moment de l'import - complementaire
d'import-linter (verifie tous les chemins possibles statiquement), pas un
remplacement : ce test s'assure juste que les modules deja ecrits
n'importent effectivement rien d'interdit au runtime, utile en CI meme
sans import-linter installe.

Bug trouve en ecrivant ce test : verifier `forbidden in sys.modules` de
facon absolue est faux dans une suite pytest complete - un AUTRE test du
meme run (`test_tui_smoke.py`) charge deja `textual` avant que ce fichier
ne s'execute, et `sys.modules` est un etat GLOBAL au process, jamais
reinitialise entre modules de test. Le seul check valide est un diff
avant/apres l'import du package cible, pas une presence absolue."""
from __future__ import annotations

import importlib
import sys


def _import_fresh(module_name: str) -> None:
    for name in list(sys.modules):
        if name == module_name or name.startswith(module_name + "."):
            del sys.modules[name]
    importlib.import_module(module_name)


def _newly_forbidden_modules(module_name: str, forbidden_prefixes: tuple[str, ...]) -> list[str]:
    """Modules interdits presents apres l'import de `module_name` mais
    absents avant - jamais un etat absolu de sys.modules (voir docstring)."""
    before = set(sys.modules)
    _import_fresh(module_name)
    after = set(sys.modules)
    newly_loaded = after - before
    return [
        name
        for name in newly_loaded
        if any(name == prefix or name.startswith(prefix + ".") for prefix in forbidden_prefixes)
    ]


_FORBIDDEN = ("textual", "sqlite3", "httpx", "dns", "jinja2")


def test_domain_package_imports_without_forbidden_tech() -> None:
    assert _newly_forbidden_modules("omega_track.domain", _FORBIDDEN) == []


def test_core_package_imports_without_forbidden_tech() -> None:
    assert _newly_forbidden_modules("omega_track.core", _FORBIDDEN) == []


def test_shared_package_imports_without_forbidden_tech() -> None:
    assert _newly_forbidden_modules("omega_track.shared", _FORBIDDEN) == []
