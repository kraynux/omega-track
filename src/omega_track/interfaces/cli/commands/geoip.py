# Copyright (c) 2026 kraynux - Licence MIT
"""Sous-commandes `geoip status|update [--provider dbip|maxmind]` (plan
de dev §9)."""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from omega_track.application.commands.geoip.configure_provider import select_geoip_provider
from omega_track.application.commands.geoip.update_database import update_geoip_database
from omega_track.application.policies.provider_selection import resolve_active_geoip_provider
from omega_track.application.queries.get_geoip_status import get_geoip_database_status
from omega_track.interfaces.cli.commands._common import JSON_FLAG
from omega_track.interfaces.cli.presenters.json_presenter import geoip_status_to_dict, print_json

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer

_SETTING_KEY = "geoip_provider"


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("geoip", help="gerer les bases GeoIP locales")
    geoip_subparsers = parser.add_subparsers(dest="geoip_action", required=True)

    geoip_subparsers.add_parser("status", help="etat de la base active", parents=[JSON_FLAG])

    update_parser = geoip_subparsers.add_parser(
        "update", help="telecharger la derniere base", parents=[JSON_FLAG]
    )
    update_parser.add_argument("--provider", choices=["dbip", "maxmind"])

    parser.set_defaults(handler=_handle)


def _handle(container: DependencyContainer, args: argparse.Namespace) -> int:
    active_provider = resolve_active_geoip_provider(container.settings_repository.get(_SETTING_KEY))

    if args.geoip_action == "status":
        view = get_geoip_database_status(
            geoip_database_repository=container.geoip_database_repository, provider=active_provider, now=container.clock
        )
        if args.json:
            print_json(
                {
                    "provider": view.provider,
                    "status": geoip_status_to_dict(view.status),
                    "is_stale": view.is_stale,
                    "age_seconds": view.age.total_seconds() if view.age else None,
                }
            )
        else:
            if view.status is None:
                print(f"base GeoIP ({view.provider}) : absente")
            else:
                stale = " (perimee)" if view.is_stale else ""
                print(f"base GeoIP ({view.provider}) : {view.status.status}{stale} - {view.status.local_path}")
        return 0

    if args.geoip_action == "update":
        provider = args.provider or active_provider
        if args.provider is not None:
            select_geoip_provider(settings_repository=container.settings_repository, provider=args.provider)

        status = update_geoip_database(
            geoip_database_repository=container.geoip_database_repository,
            database_updater=container.database_updater,
            provider=provider,
            destination=container.geoip_db_paths[provider],
            now=container.clock,
        )
        if args.json:
            print_json(geoip_status_to_dict(status))
        else:
            print(f"base GeoIP ({provider}) : {status.status} - {status.local_path}")
        return 0

    raise AssertionError(f"sous-commande geoip inconnue : {args.geoip_action!r}")
