# Copyright (c) 2026 kraynux - Licence MIT
"""Sous-commandes `track run|status|show|cancel|replay` (plan de dev
§9). `track run`/`track replay` installent un gestionnaire SIGINT local
(restaure apres coup, jamais laisse actif au-dela de l'appel) qui annule
le `CancellationToken` du TrackOrchestrator - c'est la seule vraie forme
d'annulation "en direct" possible ici : TrackOrchestrator (Phase 7) est
synchrone/bloquant par choix assume, donc SIGINT sur ce meme processus
est le seul point d'observation possible pendant l'execution (voir
application/commands/tracking/cancel_track.py pour le cas "run reste
bloque apres un crash du processus qui l'executait")."""
from __future__ import annotations

import argparse
import signal
from typing import TYPE_CHECKING

from omega_track.application.commands.tracking.cancel_track import cancel_track
from omega_track.application.commands.tracking.replay_track import replay_track
from omega_track.application.commands.tracking.start_track import start_track
from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.application.queries.get_identity_report import get_identity_report
from omega_track.application.queries.get_target import get_target
from omega_track.application.queries.get_track_run import get_track_run
from omega_track.domain.value_objects.identifiers import TargetId, TrackRunId
from omega_track.domain.value_objects.statuses import TrackStatus
from omega_track.interfaces.cli.commands._common import JSON_FLAG
from omega_track.interfaces.cli.presenters.console_presenter import print_track_run
from omega_track.interfaces.cli.presenters.json_presenter import print_json, track_run_to_dict

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer
    from omega_track.domain.entities.track_run import TrackRun

EXIT_COMPLETED = 0
EXIT_UNAVAILABLE = 3
EXIT_PARTIAL = 4
EXIT_CANCELLED = 130

_STATUS_EXIT_CODES: dict[TrackStatus, int] = {
    TrackStatus.COMPLETED: EXIT_COMPLETED,
    TrackStatus.PARTIAL: EXIT_PARTIAL,
    # FAILED : aucun module n'a produit de resultat exploitable - la cause
    # est systematiquement une source indisponible (CollectorUnavailableError,
    # voir TrackOrchestrator._finalize), d'ou le meme code que "ressource
    # indisponible" plutot que "5 - erreur interne" (le run s'est termine
    # proprement, ce n'est pas un echec inattendu).
    TrackStatus.FAILED: EXIT_UNAVAILABLE,
    TrackStatus.CANCELLED: EXIT_CANCELLED,
}


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("track", help="lancer et consulter des executions")
    track_subparsers = parser.add_subparsers(dest="track_action", required=True)

    run_parser = track_subparsers.add_parser("run", help="lancer un TrackRun", parents=[JSON_FLAG])
    run_parser.add_argument("target_id")
    run_parser.add_argument("--profile", help="reserve a un usage futur (profils nommes, hors MVP)")
    run_parser.add_argument("--module", action="append", dest="modules", default=[])
    run_parser.add_argument("--tag", action="append", dest="tags", default=[])
    run_parser.add_argument("--authorize", action="store_true")

    status_parser = track_subparsers.add_parser("status", help="statut/progression d'un run", parents=[JSON_FLAG])
    status_parser.add_argument("run_id")

    show_parser = track_subparsers.add_parser("show", help="rapport complet d'un run termine", parents=[JSON_FLAG])
    show_parser.add_argument("run_id")

    cancel_parser = track_subparsers.add_parser(
        "cancel", help="marquer un run bloque comme annule", parents=[JSON_FLAG]
    )
    cancel_parser.add_argument("run_id")

    replay_parser = track_subparsers.add_parser(
        "replay", help="nouveau run contre la resolution actuelle (D-013)", parents=[JSON_FLAG]
    )
    replay_parser.add_argument("run_id")
    replay_parser.add_argument("--authorize", action="store_true")

    parser.set_defaults(handler=_handle)


def _handle(container: DependencyContainer, args: argparse.Namespace) -> int:
    if args.track_action == "run":
        target = get_target(target_repository=container.target_repository, target_id=TargetId(args.target_id))
        token = CancellationToken()
        with _SigintCancels(token):
            result = start_track(
                target_repository=container.target_repository,
                track_run_repository=container.track_run_repository,
                track_orchestrator=container.track_orchestrator,
                target_id=target.id,
                modules=set(args.modules) if args.modules else None,
                tags=set(args.tags),
                explicit_authorization=args.authorize,
                cancellation_token=token,
                id_factory=container.id_factory,
                now=container.clock,
            )
        return _present_run_result(args, result)

    if args.track_action == "status":
        run = get_track_run(track_run_repository=container.track_run_repository, track_run_id=TrackRunId(args.run_id))
        _present_run(args, run)
        return EXIT_COMPLETED

    if args.track_action == "show":
        report = get_identity_report(
            track_run_id=TrackRunId(args.run_id),
            track_run_repository=container.track_run_repository,
            target_repository=container.target_repository,
            finding_repository=container.finding_repository,
            now=container.clock,
        )
        if args.json:
            print_json(
                {
                    "track_run_id": str(report.track_run_id),
                    "target": str(report.target_value),
                    "generated_at": report.generated_at.isoformat(),
                    "summary": report.summarize(),
                    "finding_count": len(report.findings),
                    "relation_count": len(report.relations),
                    "path_count": len(report.paths),
                }
            )
        else:
            print(f"rapport pour {report.track_run_id} - cible {report.target_value}")
            print(f"  {len(report.findings)} finding(s), {len(report.relations)} relation(s), {len(report.paths)} chemin(s)")
            print(f"  resume : {report.summarize()}")
        return EXIT_COMPLETED

    if args.track_action == "cancel":
        run = cancel_track(track_run_repository=container.track_run_repository, track_run_id=TrackRunId(args.run_id), now=container.clock)
        _present_run(args, run)
        return EXIT_COMPLETED

    if args.track_action == "replay":
        token = CancellationToken()
        with _SigintCancels(token):
            result = replay_track(
                target_repository=container.target_repository,
                track_run_repository=container.track_run_repository,
                track_orchestrator=container.track_orchestrator,
                original_track_run_id=TrackRunId(args.run_id),
                explicit_authorization=args.authorize,
                cancellation_token=token,
                id_factory=container.id_factory,
                now=container.clock,
            )
        return _present_run_result(args, result)

    raise AssertionError(f"sous-commande track inconnue : {args.track_action!r}")


def _present_run(args: argparse.Namespace, run: TrackRun) -> None:
    if args.json:
        print_json(track_run_to_dict(run))
    else:
        print_track_run(run)


def _present_run_result(args: argparse.Namespace, run: TrackRun) -> int:
    _present_run(args, run)
    return _STATUS_EXIT_CODES.get(run.status, EXIT_UNAVAILABLE)


class _SigintCancels:
    """Installe un gestionnaire SIGINT le temps du `with`, restaure
    l'ancien ensuite - jamais laisse actif au-dela de l'appel bloquant
    qu'il protege."""

    def __init__(self, token: CancellationToken) -> None:
        self._token = token
        self._previous: object = None

    def __enter__(self) -> None:
        self._previous = signal.signal(signal.SIGINT, lambda *_: self._token.cancel())

    def __exit__(self, *_exc_info: object) -> None:
        signal.signal(signal.SIGINT, self._previous)  # type: ignore[arg-type]
