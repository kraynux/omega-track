# Copyright (c) 2026 kraynux - Licence MIT
"""Options d'export (plan de dev, Phase 8 : "tous les exporteurs
recoivent IdentityReport et ExportOptions"). Absent de ARBORESCENCE.md,
ajoute par necessite pour que les ports exporters/ (Phase 3) aient une
signature complete des maintenant - enrichi en Phase 8 si de nouvelles
options apparaissent (jamais retire, seulement etendu).

`export_theme` ajoute en Phase 12 (retour utilisateur : "il manque la
logique d'export jinja2 avec les 5 themes comme les autres outils") -
independant du theme d'interface TUI actif au moment de l'export (D-007/
D-008, meme separation que CHECK/omega-scan/omega-stress) : catalogue
`omega_lib.theme.policies.EXPORT_PALETTES`."""
from __future__ import annotations

from dataclasses import dataclass, field

from omega_track.core.export_theme import DEFAULT_EXPORT_THEME
from omega_track.domain.value_objects.statuses import RedactionPolicy


@dataclass(frozen=True, slots=True)
class ExportOptions:
    redaction_policy: RedactionPolicy = RedactionPolicy.NONE
    include_relations_graph: bool = True
    export_theme: str = field(default_factory=lambda: DEFAULT_EXPORT_THEME)
