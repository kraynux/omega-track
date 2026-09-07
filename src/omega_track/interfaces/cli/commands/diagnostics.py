# Copyright (c) 2026 kraynux - Licence MIT
"""Commande `diagnostics` (plan de dev §9 - "versions, capacites
locales, chemins, base GeoIP")."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from typing import TYPE_CHECKING

from omega_track.application.policies.provider_selection import resolve_active_geoip_provider
from omega_track.application.queries.diagnostics import run_diagnostics
from omega_track.interfaces.cli.presenters.console_presenter import print_diagnostics
from omega_track.interfaces.cli.presenters.json_presenter import geoip_status_to_dict, print_json

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer

_SETTING_KEY = "geoip_provider"


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("diagnostics", help="versions, capacites locales, chemins, base GeoIP")
    parser.add_argument("--json", action="store_true")
    parser.set_defaults(handler=_handle)


def _handle(container: DependencyContainer, args: argparse.Namespace) -> int:
    provider = resolve_active_geoip_provider(container.settings_repository.get(_SETTING_KEY))
    report = run_diagnostics(
        traceroute_collector=container.traceroute_collector,
        geoip_database_repository=container.geoip_database_repository,
        geoip_provider=provider,
        var_dir=container.var_dir,
        now=container.clock,
    )
    if args.json:
        payload = asdict(report)
        payload["geoip_status"] = {
            "provider": report.geoip_status.provider,
            "status": geoip_status_to_dict(report.geoip_status.status),
            "is_stale": report.geoip_status.is_stale,
        }
        print_json(payload)
    else:
        print_diagnostics(report)
    return 0
