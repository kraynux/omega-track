# Copyright (c) 2026 kraynux - Licence MIT
"""Identifiants types (plan de dev §4.2) - `NewType` plutot qu'une classe
enveloppe : cout zero a l'execution, verifie seulement par le typeur
statique, suffisant pour empecher de passer un TrackRunId a la place d'un
TargetId par erreur de copier-coller. La generation reelle (UUID4 via
`omega_track.shared.ids.new_id`) est une responsabilite d'application/,
jamais du domaine lui-meme (le domaine ne genere jamais ses propres
identifiants, il les recoit deja formes)."""
from __future__ import annotations

from typing import NewType

TargetId = NewType("TargetId", str)
TrackProfileId = NewType("TrackProfileId", str)
"""Absent de la liste explicite du plan de dev §4.2 mais necessaire au
meme titre : `track_profiles` a bien sa propre cle primaire dans le
schema SQLite (Phase 4) - meme discipline, pas une exception."""
TrackRunId = NewType("TrackRunId", str)
ModuleRunId = NewType("ModuleRunId", str)
"""Idem TrackProfileId : `module_runs.id` est une cle primaire reelle du
schema (Phase 4), meme si absente de l'enumeration du plan de dev §4.2."""
FindingId = NewType("FindingId", str)
RelationId = NewType("RelationId", str)
"""Idem - `relations.id` est une cle primaire reelle du schema (Phase 4)."""
ExportId = NewType("ExportId", str)
