# Copyright (c) 2026 kraynux - Licence MIT
"""Sous-commande `history list [--target] [--status] [--tag] [--since]
[--until]` (plan de dev §9)."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from omega_track.application.queries.list_track_runs import list_track_runs
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.interfaces.cli.commands._common import JSON_FLAG
from omega_track.interfaces.cli.presenters.json_presenter import print_json, track_run_to_dict
from omega_track.interfaces.cli.presenters.table_presenter import print_track_runs_table

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("history", help="consulter l'historique des executions")
    history_subparsers = parser.add_subparsers(dest="history_action", required=True)

    list_parser = history_subparsers.add_parser("list", help="lister les executions", parents=[JSON_FLAG])
    list_parser.add_argument("--target")
    list_parser.add_argument("--status")
    list_parser.add_argument("--tag")
    list_parser.add_argument("--since", help="date ISO8601")
    list_parser.add_argument("--until", help="date ISO8601")

    parser.set_defaults(handler=_handle)


def _handle(container: DependencyContainer, args: argparse.Namespace) -> int:
    runs = list_track_runs(
        track_run_repository=container.track_run_repository,
        target_id=TargetId(args.target) if args.target else None,
        status=args.status,
        tag=args.tag,
        since=_parse_date(args.since),
        until=_parse_date(args.until),
    )
    if args.json:
        print_json([track_run_to_dict(r) for r in runs])
    else:
        print_track_runs_table(runs)
    return 0


def _parse_date(raw: str | None) -> datetime | None:
    if raw is None:
        return None
    parsed = datetime.fromisoformat(raw)
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=timezone.utc)
