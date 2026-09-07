# Copyright (c) 2026 kraynux - Licence MIT
"""Configuration du logger applicatif technique (stdlib logging). Porte
depuis omega-check/infrastructure/logging/config.py (D-007/D-008), etendu
d'un correlation ID absent chez CHECK/DEEP/FOLD : chaque ligne journalisee
pendant un TrackRun doit pouvoir se recouper avec les findings persistes
du meme run (SQLite), pas seulement rester un flux texte isole - d'ou
`track_run_id` porte par un `logging.Filter`, jamais reconstruit a la main
dans chaque appel de logger."""
from __future__ import annotations

import contextvars
import logging
import sys
from pathlib import Path

from omega_track.core.constants import LOGGER_NAME

APP_LOG_FILENAME = "app.log"
DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s [%(track_run_id)s]: %(message)s"
_NO_RUN = "-"

_current_track_run_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "track_run_id", default=_NO_RUN
)


class _TrackRunIdFilter(logging.Filter):
    """Injecte `record.track_run_id` depuis le contexte courant - permet
    au formatter de le referencer sans que chaque site d'appel de logger
    n'ait a le passer explicitement en `extra=`."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.track_run_id = _current_track_run_id.get()
        return True


def set_current_track_run_id(track_run_id: str | None) -> contextvars.Token[str]:
    """A appeler par l'orchestrateur (Phase 7) au debut d'un TrackRun,
    et a annuler (voir `reset_current_track_run_id`) a sa fin - meme
    discipline qu'un context manager, pour ne jamais laisser un ID de run
    termine "fuiter" sur les lignes de log d'un run suivant."""
    return _current_track_run_id.set(track_run_id if track_run_id is not None else _NO_RUN)


def reset_current_track_run_id(token: contextvars.Token[str]) -> None:
    _current_track_run_id.reset(token)


def configure_logging(*, log_path: Path, level: int = logging.INFO, console: bool = True) -> logging.Logger:
    """Configure et retourne le logger applicatif nomme 'omega_track', avec
    un handler fichier (toujours actif) et un handler console optionnel.
    Idempotent : rappeler cette fonction remplace les handlers existants
    plutot que d'en accumuler (utile en tests).

    `console=False` sous la TUI (voir app/bootstrap.py) : Textual controle
    l'ecran en mode alternatif, une ecriture directe sur stderr pendant un
    track corromprait son rendu - meme raisonnement que CHECK."""
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.handlers.clear()
    logger.filters.clear()
    logger.propagate = False
    logger.addFilter(_TrackRunIdFilter())

    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
