# Copyright (c) 2026 kraynux - Licence MIT
"""Serialisation JSON machine-readable des entites (plan de dev §9,
critere de sortie "sortie JSON machine-readable disponible pour les
commandes de listing, consultation et track") - propre a la CLI, ne
reutilise jamais infrastructure/exporters/_report_view.py (prive a ce
sous-package, et interfaces/ ne peut de toute facon pas importer
infrastructure/ directement - contrat import-linter)."""
from __future__ import annotations

import json
import sys
from typing import Any

from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus
from omega_track.domain.entities.target import Target
from omega_track.domain.entities.track_run import TrackRun


def target_to_dict(target: Target) -> dict[str, Any]:
    return {
        "id": str(target.id),
        "value": str(target.value),
        "kind": target.kind.value,
        "alias": target.alias,
        "tags": sorted(target.tags),
        "pinned": target.pinned,
        "last_track_at": target.last_track_at.isoformat() if target.last_track_at else None,
        "last_status": target.last_status,
    }


def track_run_to_dict(run: TrackRun) -> dict[str, Any]:
    return {
        "id": str(run.id),
        "target_id": str(run.target_id),
        "status": run.status.value,
        "progress": run.progress,
        "created_at": run.created_at.isoformat(),
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        "tags": sorted(run.tags),
        "error_summary": run.error_summary,
        "modules": {
            name: {
                "status": module_run.status.value,
                "error_code": module_run.error_code,
                "error_detail": module_run.error_detail,
            }
            for name, module_run in run.module_runs.items()
        },
    }


def geoip_status_to_dict(status: GeoIpDatabaseStatus | None) -> dict[str, Any] | None:
    if status is None:
        return None
    return {
        "provider": status.provider,
        "edition": status.edition,
        "local_path": status.local_path,
        "checksum": status.checksum,
        "downloaded_at": status.downloaded_at.isoformat(),
        "published_at": status.published_at.isoformat() if status.published_at else None,
        "status": status.status,
    }


def print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False), file=sys.stdout)
