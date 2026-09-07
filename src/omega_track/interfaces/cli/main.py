# Copyright (c) 2026 kraynux - Licence MIT
"""Dispatch CLI scriptable (Phase 9 - remplace le squelette de la
Phase 1). Codes de sortie documentes plan de dev §9 (un par cas, pas un
simple succes/echec) : centralises ici, jamais duplique par sous-commande."""
from __future__ import annotations

import argparse
import logging
from typing import TYPE_CHECKING, NoReturn, cast

from omega_track.application.exceptions import (
    ApiKeyMissingError,
    ApplicationError,
    CollectorUnavailableError,
    GeoIpDownloadError,
    MaxMindCredentialsMissingError,
    TargetNotFoundError,
    TrackRunNotFoundError,
    UnknownExportFormatError,
    UnknownGeoIpProviderError,
    UnknownReputationSourceError,
)
from omega_track.core.constants import APP_VERSION, LOGGER_NAME
from omega_track.core.errors import OmegaTrackError
from omega_track.domain.exceptions.target import DuplicateTargetError, InvalidTargetValueError
from omega_track.domain.exceptions.track import (
    InvalidTrackTransitionError,
    TargetNotAuthorizedError,
)
from omega_track.interfaces.cli.commands import (
    cleanup,
    config,
    diagnostics,
    export,
    geoip,
    history,
    source,
    target,
    track,
)
from omega_track.interfaces.cli.presenters.console_presenter import print_error

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer

EXIT_SUCCESS = 0
EXIT_VALIDATION = 1
EXIT_UNAUTHORIZED = 2
EXIT_UNAVAILABLE = 3
EXIT_PARTIAL = 4
EXIT_INTERNAL = 5
EXIT_CANCELLED = 130

_VALIDATION_ERRORS = (
    InvalidTargetValueError,
    DuplicateTargetError,
    UnknownExportFormatError,
    UnknownGeoIpProviderError,
    InvalidTrackTransitionError,
    MaxMindCredentialsMissingError,
    ApiKeyMissingError,
    UnknownReputationSourceError,
)
_UNAVAILABLE_ERRORS = (TargetNotFoundError, TrackRunNotFoundError, CollectorUnavailableError, GeoIpDownloadError)

_COMMAND_MODULES = (target, track, history, export, geoip, source, config, cleanup, diagnostics)


class _ArgumentParser(argparse.ArgumentParser):
    """Argparse quitte par defaut avec le code 2 sur une erreur d'usage -
    entre en collision avec le code 2 du plan ("cible non autorisee").
    Remappe vers 1 ("erreur de validation"), coherent avec le tableau de
    codes de sortie du plan de dev §9."""

    def error(self, message: str) -> NoReturn:
        self.print_usage()
        self.exit(EXIT_VALIDATION, f"{self.prog}: error: {message}\n")


def build_parser() -> _ArgumentParser:
    parser = _ArgumentParser(
        prog="omega-track",
        description="Profilage d'identite numerique et observation de chemin reseau.",
    )
    parser.add_argument("--version", action="version", version=f"omega-track {APP_VERSION}")
    subparsers = parser.add_subparsers(dest="command")
    for module in _COMMAND_MODULES:
        module.add_subparser(subparsers)
    return parser


def run(container: DependencyContainer, argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "handler"):
        parser.print_help()
        return EXIT_SUCCESS

    try:
        return cast(int, args.handler(container, args))
    except KeyboardInterrupt:
        return EXIT_CANCELLED
    except TargetNotAuthorizedError as exc:
        print_error(str(exc))
        return EXIT_UNAUTHORIZED
    except _VALIDATION_ERRORS as exc:
        print_error(str(exc))
        return EXIT_VALIDATION
    except _UNAVAILABLE_ERRORS as exc:
        print_error(str(exc))
        return EXIT_UNAVAILABLE
    except (OmegaTrackError, ApplicationError) as exc:
        print_error(str(exc))
        return EXIT_INTERNAL
    except Exception as exc:
        logging.getLogger(LOGGER_NAME).exception("erreur interne inattendue")
        print_error(f"erreur interne inattendue : {exc}")
        return EXIT_INTERNAL
