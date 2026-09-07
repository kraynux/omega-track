# Copyright (c) 2026 kraynux - Licence MIT
"""Preuve associee a un finding/une relation (plan de dev §4.2).
`ConfidenceLevel` vit dans core/enums.py (reexport omega_lib, D-001) -
jamais redefini ici (voir OMEGA_TRACK_PLAN_DEVELOPPEMENT.md §4.2)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Evidence:
    source: str
    """Nom de la source ayant produit cette preuve (ex. 'crt.sh', 'rdap',
    'dns-a-record') - voir docs/DATA_SOURCES.md pour la liste reelle."""
    collected_at: datetime
    reference: str | None = None
    """URL ou identifiant de reference chez la source, si applicable."""
    fingerprint: str | None = None
    """Empreinte du contenu source (ex. hash du certificat observe) -
    permet de detecter qu'une meme preuve a change entre deux collectes."""
    method: str | None = None
    """Comment la preuve a ete obtenue (ex. 'dns-query', 'http-get',
    'ct-log-search') - distinct de `source` (le fournisseur) : deux
    methodes differentes peuvent interroger la meme source."""
