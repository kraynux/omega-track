# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de persistance des findings et relations d'un TrackRun (plan
de dev, Phase 3/4). Les deux vivent dans le meme port : produits par le
meme orchestrateur (Phase 7), toujours lus/ecrits ensemble pour un
TrackRun donne - mais restent deux tables distinctes (`findings`/
`relations`, Phase 4), jamais un aggregat root commun avec TrackRun
(voir track_run_repository.py)."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.relation import Relation
from omega_track.domain.value_objects.identifiers import TrackRunId


class FindingRepository(Protocol):
    def save_findings(self, findings: list[Finding]) -> None: ...

    def save_relations(self, relations: list[Relation]) -> None: ...

    def list_findings_for_run(self, track_run_id: TrackRunId) -> list[Finding]: ...

    def list_relations_for_run(self, track_run_id: TrackRunId) -> list[Relation]: ...

    def delete_for_run(self, track_run_id: TrackRunId) -> None:
        """Supprime findings ET relations d'un TrackRun (Phase 9,
        `cleanup history`) - necessaire car TrackRunRepository.delete()
        (Phase 4) ne nettoie que `track_runs`/`module_runs`, jamais
        `findings`/`relations` (pas de ON DELETE CASCADE, meme choix
        assume qu'ailleurs dans la suite pour DEEP/FOLD) : sans cette
        methode, purger un TrackRun laisserait des findings/relations
        orphelins."""
        ...
