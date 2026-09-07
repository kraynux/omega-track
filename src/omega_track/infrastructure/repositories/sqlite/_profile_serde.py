# Copyright (c) 2026 kraynux - Licence MIT
"""Serialisation partagee de TrackProfile - utilisee a la fois par
track_profile_repository.py (colonnes decomposees `modules_json`/
`options_json`) et track_run_repository.py (un seul blob
`profile_snapshot_json`, copie complete et autonome du profil au moment
du lancement, condition de `track replay`/D-013). Prefixe `_` : module
prive au sous-package sqlite/, jamais importe hors de lui."""
from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from omega_track.domain.entities.track_profile import ExecutionLimits, NeoTraceOptions, TrackProfile
from omega_track.domain.value_objects.identifiers import TrackProfileId


def _neotrace_to_dict(options: NeoTraceOptions) -> dict[str, Any]:
    return {
        "protocol": options.protocol,
        "timeout_seconds": options.timeout_seconds,
        "max_hops": options.max_hops,
        "enable_reverse_dns": options.enable_reverse_dns,
        "enable_mtr": options.enable_mtr,
    }


def _limits_to_dict(limits: ExecutionLimits) -> dict[str, Any]:
    return {
        "max_ipv4_enriched": limits.max_ipv4_enriched,
        "max_ipv6_enriched": limits.max_ipv6_enriched,
        "max_neotrace_ips": limits.max_neotrace_ips,
    }


def options_json_for(profile: TrackProfile) -> str:
    return json.dumps({
        "neotrace": _neotrace_to_dict(profile.neotrace),
        "limits": _limits_to_dict(profile.limits),
    })


def modules_json_for(profile: TrackProfile) -> str:
    return json.dumps(sorted(profile.modules))


def profile_snapshot_json(profile: TrackProfile) -> str:
    """Blob complet et autonome (id/name/modules/options/is_default/dates) -
    pour `track_runs.profile_snapshot_json`, jamais decompose en colonnes."""
    return json.dumps({
        "id": profile.id,
        "name": profile.name,
        "is_default": profile.is_default,
        "modules": sorted(profile.modules),
        "neotrace": _neotrace_to_dict(profile.neotrace),
        "limits": _limits_to_dict(profile.limits),
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    })


def profile_from_snapshot_json(raw: str) -> TrackProfile:
    data = json.loads(raw)
    return TrackProfile(
        id=TrackProfileId(data["id"]),
        name=data["name"],
        is_default=data["is_default"],
        modules=set(data["modules"]),
        neotrace=NeoTraceOptions(**data["neotrace"]),
        limits=ExecutionLimits(**data["limits"]),
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
    )


def profile_from_columns(
    *,
    id_: str,
    name: str,
    is_default: int,
    modules_json: str,
    options_json: str,
    created_at: str,
    updated_at: str,
) -> TrackProfile:
    options = json.loads(options_json)
    return TrackProfile(
        id=TrackProfileId(id_),
        name=name,
        is_default=bool(is_default),
        modules=set(json.loads(modules_json)),
        neotrace=NeoTraceOptions(**options["neotrace"]),
        limits=ExecutionLimits(**options["limits"]),
        created_at=datetime.fromisoformat(created_at),
        updated_at=datetime.fromisoformat(updated_at),
    )
