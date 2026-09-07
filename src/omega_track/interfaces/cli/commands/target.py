# Copyright (c) 2026 kraynux - Licence MIT
"""Sous-commandes `target add|list|edit|pin|delete` (plan de dev §9)."""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from omega_track.application.commands.targets.create_target import create_target
from omega_track.application.commands.targets.delete_targets import delete_targets
from omega_track.application.commands.targets.pin_target import pin_target
from omega_track.application.commands.targets.update_target import update_target
from omega_track.application.queries.list_targets import list_targets
from omega_track.domain.entities.target import Target
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.interfaces.cli.commands._common import JSON_FLAG
from omega_track.interfaces.cli.presenters.console_presenter import print_target
from omega_track.interfaces.cli.presenters.json_presenter import print_json, target_to_dict
from omega_track.interfaces.cli.presenters.table_presenter import print_targets_table

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("target", help="gerer les cibles")
    target_subparsers = parser.add_subparsers(dest="target_action", required=True)

    add_parser = target_subparsers.add_parser("add", help="ajouter une cible", parents=[JSON_FLAG])
    add_parser.add_argument("value", help="IP ou domaine")
    add_parser.add_argument("--alias")
    add_parser.add_argument("--tag", action="append", dest="tags", default=[])

    target_subparsers.add_parser("list", help="lister les cibles", parents=[JSON_FLAG])

    edit_parser = target_subparsers.add_parser("edit", help="modifier alias/tags", parents=[JSON_FLAG])
    edit_parser.add_argument("target_id")
    edit_parser.add_argument("--alias")
    edit_parser.add_argument("--add-tag", action="append", dest="add_tags", default=[])
    edit_parser.add_argument("--remove-tag", action="append", dest="remove_tags", default=[])

    pin_parser = target_subparsers.add_parser("pin", help="epingler = autoriser (D-010)", parents=[JSON_FLAG])
    pin_parser.add_argument("target_id")

    delete_parser = target_subparsers.add_parser("delete", help="supprimer une ou plusieurs cibles")
    delete_parser.add_argument("target_ids", nargs="+")

    parser.set_defaults(handler=_handle)


def _handle(container: DependencyContainer, args: argparse.Namespace) -> int:
    if args.target_action == "add":
        target = create_target(
            target_repository=container.target_repository,
            raw_value=args.value,
            alias=args.alias,
            tags=set(args.tags),
            id_factory=container.id_factory,
            now=container.clock,
        )
        _present(args, target)
        return 0

    if args.target_action == "list":
        targets = list_targets(target_repository=container.target_repository)
        if args.json:
            print_json([target_to_dict(t) for t in targets])
        else:
            print_targets_table(targets)
        return 0

    if args.target_action == "edit":
        target = update_target(
            target_repository=container.target_repository,
            target_id=TargetId(args.target_id),
            alias=args.alias,
            add_tags=set(args.add_tags),
            remove_tags=set(args.remove_tags),
            now=container.clock,
        )
        _present(args, target)
        return 0

    if args.target_action == "pin":
        target = pin_target(target_repository=container.target_repository, target_id=TargetId(args.target_id), now=container.clock)
        _present(args, target)
        return 0

    if args.target_action == "delete":
        delete_targets(
            target_repository=container.target_repository, target_ids=[TargetId(i) for i in args.target_ids]
        )
        return 0

    raise AssertionError(f"sous-commande target inconnue : {args.target_action!r}")


def _present(args: argparse.Namespace, target: Target) -> None:
    if args.json:
        print_json(target_to_dict(target))
    else:
        print_target(target)
