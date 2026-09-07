# Copyright (c) 2026 kraynux - Licence MIT
"""Vues intermediaires partagees entre les 6 exporteurs (Phase 8) - prive
(meme convention que infrastructure/repositories/sqlite/_profile_serde.py) :
transforme IdentityReport/ExportOptions en dicts simples, jamais
serialises directement (chaque exporteur choisit ensuite son propre
format de sortie a partir des memes donnees). La redaction (docs/
PRIVACY.md §3) est deja appliquee par l'appelant (export_orchestrator.py)
avant que le rapport n'atteigne un exporteur - ces vues ne connaissent
jamais `RedactionPolicy` autrement que pour l'afficher dans l'en-tete."""
from __future__ import annotations

from typing import Any

from omega_track.core.constants import APP_VERSION, EXPORT_SCHEMA_VERSION
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.path import NetworkHop, NetworkPath
from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.entities.relation import Cluster, Relation
from omega_track.domain.value_objects.export_options import ExportOptions


def build_header(report: IdentityReport, options: ExportOptions) -> dict[str, Any]:
    profile = report.profile_snapshot
    return {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "app_version": APP_VERSION,
        "track_run_id": str(report.track_run_id),
        "target": str(report.target_value),
        "generated_at": report.generated_at.isoformat(),
        "profile": profile.name,
        "modules": sorted(profile.modules),
        "limits": {
            "max_ipv4_enriched": profile.limits.max_ipv4_enriched,
            "max_ipv6_enriched": profile.limits.max_ipv6_enriched,
            "max_neotrace_ips": profile.limits.max_neotrace_ips,
        },
        "redaction_policy": options.redaction_policy.value,
        "sources": sorted({finding.source_name for finding in report.findings}),
        "export_theme": options.export_theme,
    }


def finding_to_dict(finding: Finding) -> dict[str, Any]:
    return {
        "id": str(finding.id),
        "finding_type": finding.finding_type,
        "payload": finding.payload,
        "confidence": finding.confidence.value,
        "collection_mode": finding.collection_mode.value,
        "source_name": finding.source_name,
        "observed_at": finding.observed_at.isoformat(),
    }


def relation_to_dict(relation: Relation) -> dict[str, Any]:
    return {
        "id": str(relation.id),
        "source": relation.source_entity_ref,
        "target": relation.target_entity_ref,
        "relation_type": relation.relation_type.value,
        "confidence": relation.confidence.value,
    }


def cluster_to_dict(cluster: Cluster) -> dict[str, Any]:
    return {"id": cluster.id, "members": sorted(cluster.member_refs), "label": cluster.label}


def hop_to_dict(hop: NetworkHop) -> dict[str, Any]:
    return {
        "sequence": hop.sequence,
        "ip": str(hop.ip) if hop.ip is not None else None,
        "hostname": hop.hostname,
        "rtt_ms": hop.rtt_ms,
        "asn": hop.asn.number if hop.asn else None,
        "geo_country": hop.geo.country if hop.geo else None,
    }


def path_to_dict(path: NetworkPath) -> dict[str, Any]:
    return {
        "target_ip": str(path.target_ip),
        "protocol": path.protocol,
        "reached_target": path.reached_target,
        "non_responding_count": path.non_responding_count,
        "average_rtt_ms": path.average_rtt_ms,
        "hops": [hop_to_dict(hop) for hop in path.hops],
    }
