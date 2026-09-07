# Copyright (c) 2026 kraynux - Licence MIT
"""Constantes applicatives partagees (Phase 8) - premiere necessite
reelle : chaque export doit indiquer une version de schema et une
version applicative (plan de dev §8 "Regles communes"), jusqu'ici
`__version__` etait duplique localement dans interfaces/cli/main.py sans
source unique."""
from __future__ import annotations

APP_VERSION = "0.1.0"
EXPORT_SCHEMA_VERSION = 1
"""Version du schema des artefacts exportes (JSON/HTML/...) - independante
de APP_VERSION, incrementee seulement si la FORME d'un export change de
maniere incompatible (D-018 : pas de moteur de migration, mais un export
deja ecrit sur disque doit rester interpretable en connaissant son
propre schema_version)."""

LOGGER_NAME = "omega_track"
"""Nom du logger applicatif (Phase 1) - vit ici plutot que dans
infrastructure/logging/config.py (qui le reexporte) : interfaces/ (Phase 9,
main.py::run dernier filet d'exception) doit pouvoir journaliser une
erreur inattendue sans importer infrastructure/ directement (Dependency
Rule/contrat import-linter "interfaces independant de infrastructure"),
et `core` est la seule couche que les deux peuvent importer sans
enfreindre la regle."""
