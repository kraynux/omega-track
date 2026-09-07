# Copyright (c) 2026 kraynux - Licence MIT
"""Sous-commandes `source list|info <name>|configure <name> <key>|clear
<name>` (plan de dev §12) - `info`/`configure` affichent TOUJOURS le
texte de divulgation (cle requise/quota/donnees envoyees/confidentialite)
avant d'enregistrer quoi que ce soit : `configure` sans avoir vu ce texte
est impossible, il s'affiche dans le meme appel, avant la persistance
de la cle (voir application/queries/get_source_disclosure.py)."""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING, Any

from omega_track.application.commands.reputation.clear_source_key import clear_source_key
from omega_track.application.commands.reputation.configure_source_key import configure_source_key
from omega_track.application.queries.get_source_disclosure import (
    SourceDisclosure,
    get_source_disclosure,
    list_known_reputation_sources,
)
from omega_track.application.queries.get_source_status import SourceStatusView, get_source_status
from omega_track.interfaces.cli.commands._common import JSON_FLAG
from omega_track.interfaces.cli.presenters.json_presenter import print_json

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("source", help="gerer les sources de reputation a cle")
    source_subparsers = parser.add_subparsers(dest="source_action", required=True)

    source_subparsers.add_parser("list", help="statut de toutes les sources connues", parents=[JSON_FLAG])

    info_parser = source_subparsers.add_parser(
        "info", help="cle requise/quota/donnees envoyees/confidentialite", parents=[JSON_FLAG]
    )
    info_parser.add_argument("name", choices=list_known_reputation_sources())

    configure_parser = source_subparsers.add_parser(
        "configure", help="afficher la divulgation puis enregistrer une cle", parents=[JSON_FLAG]
    )
    configure_parser.add_argument("name", choices=list_known_reputation_sources())
    configure_parser.add_argument("key")

    clear_parser = source_subparsers.add_parser("clear", help="retirer une cle deja configuree", parents=[JSON_FLAG])
    clear_parser.add_argument("name", choices=list_known_reputation_sources())

    parser.set_defaults(handler=_handle)


def _handle(container: DependencyContainer, args: argparse.Namespace) -> int:
    if args.source_action == "list":
        statuses = [
            get_source_status(
                secret_store=container.secret_store,
                settings_repository=container.settings_repository,
                source_name=name,
                now=container.clock,
            )
            for name in list_known_reputation_sources()
        ]
        if args.json:
            print_json([_status_to_dict(view) for view in statuses])
        else:
            for view in statuses:
                backoff = ""
                if view.in_backoff and view.backoff_until is not None:
                    backoff = f" (en attente jusqu'a {view.backoff_until.isoformat()})"
                print(f"{view.source_name} : cle {'configuree' if view.key_configured else 'absente'}{backoff}")
        return 0

    if args.source_action == "info":
        disclosure = get_source_disclosure(args.name)
        if args.json:
            print_json(_disclosure_to_dict(disclosure))
        else:
            _print_disclosure(disclosure)
        return 0

    if args.source_action == "configure":
        disclosure = get_source_disclosure(args.name)
        _print_disclosure(disclosure)
        configure_source_key(secret_store=container.secret_store, source_name=args.name, api_key=args.key)
        if args.json:
            print_json({"source": args.name, "configured": True})
        else:
            print(f"cle enregistree pour {args.name}")
        return 0

    if args.source_action == "clear":
        clear_source_key(secret_store=container.secret_store, source_name=args.name)
        if args.json:
            print_json({"source": args.name, "configured": False})
        else:
            print(f"cle retiree pour {args.name}")
        return 0

    raise AssertionError(f"sous-commande source inconnue : {args.source_action!r}")


def _print_disclosure(disclosure: SourceDisclosure) -> None:
    payant = " (SOURCE PAYANTE)" if disclosure.is_paid else ""
    print(f"=== {disclosure.source_name}{payant} ===")
    print(f"Quota : {disclosure.quota_notice}")
    print(f"Donnees envoyees : {disclosure.data_sent_notice}")
    print(f"Confidentialite : {disclosure.privacy_notice}")


def _disclosure_to_dict(disclosure: SourceDisclosure) -> dict[str, Any]:
    return {
        "source": disclosure.source_name,
        "is_paid": disclosure.is_paid,
        "quota_notice": disclosure.quota_notice,
        "data_sent_notice": disclosure.data_sent_notice,
        "privacy_notice": disclosure.privacy_notice,
    }


def _status_to_dict(view: SourceStatusView) -> dict[str, Any]:
    return {
        "source": view.source_name,
        "key_configured": view.key_configured,
        "in_backoff": view.in_backoff,
        "backoff_until": view.backoff_until.isoformat() if view.backoff_until else None,
    }
