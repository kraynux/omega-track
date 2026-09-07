# Copyright (c) 2026 kraynux - Licence MIT
"""Sous-commandes `cleanup preview|run --older-than <days>` (plan de dev
§9) - `run` exige `--older-than` explicite ET `--yes` (aucune suppression
totale silencieuse par defaut, "Toutes les commandes destructives
exigent une confirmation ou --yes explicite"). `screenshots`/`exports`
(Phase 12, retour utilisateur, meme parite CLI/TUI que le reste de la
suite) videnrt entierement leur dossier - meme discipline `--yes`."""
from __future__ import annotations

import argparse
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from omega_track.application.commands.maintenance.cleanup_history import (
    cleanup_history,
    preview_history_cleanup,
)
from omega_track.application.commands.maintenance.clear_directory import clear_directory
from omega_track.interfaces.cli.commands._common import JSON_FLAG
from omega_track.interfaces.cli.presenters.console_presenter import (
    print_cleanup_preview,
    print_error,
)
from omega_track.interfaces.cli.presenters.json_presenter import print_json

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("cleanup", help="purger l'historique ancien ou des fichiers locaux")
    cleanup_subparsers = parser.add_subparsers(dest="cleanup_action", required=True)

    preview_parser = cleanup_subparsers.add_parser(
        "preview", help="apercu sans suppression", parents=[JSON_FLAG]
    )
    preview_parser.add_argument("--older-than", required=True, type=int, metavar="DAYS")

    run_parser = cleanup_subparsers.add_parser("run", help="supprimer reellement", parents=[JSON_FLAG])
    run_parser.add_argument("--older-than", required=True, type=int, metavar="DAYS")
    run_parser.add_argument("--yes", action="store_true", help="confirmation explicite requise")

    screenshots_parser = cleanup_subparsers.add_parser(
        "screenshots", help="vider le dossier des captures d'ecran", parents=[JSON_FLAG]
    )
    screenshots_parser.add_argument("--yes", action="store_true", help="confirmation explicite requise")

    exports_parser = cleanup_subparsers.add_parser(
        "exports", help="vider le dossier des exports", parents=[JSON_FLAG]
    )
    exports_parser.add_argument("--yes", action="store_true", help="confirmation explicite requise")

    parser.set_defaults(handler=_handle)


def _handle(container: DependencyContainer, args: argparse.Namespace) -> int:
    older_than = timedelta(days=args.older_than)

    if args.cleanup_action == "preview":
        preview = preview_history_cleanup(
            track_run_repository=container.track_run_repository, older_than=older_than, now=container.clock
        )
        if args.json:
            print_json({"count": preview.count, "track_run_ids": [str(i) for i in preview.track_run_ids]})
        else:
            print_cleanup_preview(preview)
        return 0

    if args.cleanup_action == "run":
        if not args.yes:
            print_error("suppression refusee sans --yes (aucune suppression silencieuse par defaut)")
            return 1
        result = cleanup_history(
            track_run_repository=container.track_run_repository,
            finding_repository=container.finding_repository,
            export_repository=container.export_repository,
            older_than=older_than,
            now=container.clock,
        )
        if args.json:
            print_json({"count": result.count, "track_run_ids": [str(i) for i in result.track_run_ids]})
        else:
            print(f"{result.count} execution(s) supprimee(s)")
        return 0

    if args.cleanup_action == "screenshots":
        return _clear_directory(args, container.default_screenshots_dir, "capture(s) d'ecran")

    if args.cleanup_action == "exports":
        return _clear_directory(args, container.default_exports_dir, "export(s)")

    raise AssertionError(f"sous-commande cleanup inconnue : {args.cleanup_action!r}")


def _clear_directory(args: argparse.Namespace, directory: Path, label: str) -> int:
    if not args.yes:
        print_error("suppression refusee sans --yes (aucune suppression silencieuse par defaut)")
        return 1
    deleted = clear_directory(directory)
    if args.json:
        print_json({"count": deleted})
    else:
        print(f"{deleted} {label} supprime(s)")
    return 0
