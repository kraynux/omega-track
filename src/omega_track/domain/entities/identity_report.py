# Copyright (c) 2026 kraynux - Licence MIT
"""Vue agregee produite a partir d'un TrackRun (plan de dev §4.1) :
identite, reseau, DNS, certificats, reputation, organisation, timeline,
graphe. L'agregation elle-meme (`summarize`) est pure - la collecte des
donnees source (lecture SQLite) reste une responsabilite d'application/
orchestrators/report_builder.py (Phase 8), qui appelle cette classe une
fois les donnees deja en memoire.

`target_value`/`profile_snapshot` ajoutes en Phase 8 (absents du plan
initial) : tout export doit indiquer cible/profil/modules/limites (plan
de dev §8 "Regles communes") - sans ces deux champs, un IdentityReport
n'aurait aucun moyen de porter cette information jusqu'aux exporteurs,
qui ne recoivent jamais autre chose que (IdentityReport, ExportOptions)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.path import NetworkPath
from omega_track.domain.entities.relation import Cluster, Relation
from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.value_objects.identifiers import TargetId, TrackRunId
from omega_track.domain.value_objects.target_value import TargetValue


@dataclass
class IdentityReport:
    track_run_id: TrackRunId
    target_id: TargetId
    target_value: TargetValue
    profile_snapshot: TrackProfile
    generated_at: datetime
    findings: list[Finding] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)
    clusters: list[Cluster] = field(default_factory=list)
    paths: list[NetworkPath] = field(default_factory=list)

    def findings_by_type_prefix(self, prefix: str) -> list[Finding]:
        """Ex. `findings_by_type_prefix("dns.")` pour l'onglet DNS d'un
        ecran de resultats (Phase 11) - le prefixe correspond a la
        famille (voir domain/entities/findings/*.py)."""
        return [f for f in self.findings if f.finding_type.startswith(prefix)]

    def summarize(self) -> dict[str, int]:
        """Compte des findings par niveau de confiance - une aide de
        lecture, jamais un verdict de securite (plan de dev §4.4 : "le
        score global n'est jamais un verdict de securite")."""
        counts = {level.value: 0 for level in ConfidenceLevel}
        for finding in self.findings:
            counts[finding.confidence.value] += 1
        return counts
