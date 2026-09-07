# Copyright (c) 2026 kraynux - Licence MIT
"""Sous-commandes `config show|set <key> <value>` (plan de dev §9) -
`set` appelle SettingsRepository.set directement (pas de use case dedie,
voir application/queries/get_settings.py : passage generique cle/valeur
sans logique metier a encapsuler)."""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from omega_track.application.queries.get_settings import get_settings
from omega_track.interfaces.cli.commands._common import JSON_FLAG
from omega_track.interfaces.cli.presenters.json_presenter import print_json

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("config", help="reglages applicatifs")
    config_subparsers = parser.add_subparsers(dest="config_action", required=True)

    config_subparsers.add_parser("show", help="afficher tous les reglages", parents=[JSON_FLAG])

    set_parser = config_subparsers.add_parser("set", help="modifier un reglage")
    set_parser.add_argument("key")
    set_parser.add_argument("value")

    parser.set_defaults(handler=_handle)


def _handle(container: DependencyContainer, args: argparse.Namespace) -> int:
    if args.config_action == "show":
        settings = get_settings(settings_repository=container.settings_repository)
        if args.json:
            print_json(settings)
        else:
            for key, value in sorted(settings.items()):
                print(f"{key} = {value}")
        return 0

    if args.config_action == "set":
        container.settings_repository.set(args.key, args.value)
        return 0

    raise AssertionError(f"sous-commande config inconnue : {args.config_action!r}")
