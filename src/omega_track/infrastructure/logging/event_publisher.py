# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation par defaut de EventPublisher (Phase 7) - journalise via
le logger applicatif deja configure (`infrastructure/logging/config.py`),
sans dependance a Textual ni au CLI : la CLI (Phase 9) peut simplement
lire ce meme journal, la TUI (Phase 11) branchera son propre
EventPublisher (mise a jour de widgets) le moment venu, sans changer
TrackOrchestrator."""
from __future__ import annotations

import logging

from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.domain.value_objects.statuses import ModuleStatus
from omega_track.infrastructure.logging.config import LOGGER_NAME


class LoggingEventPublisher:
    """Implemente ports/services/event_publisher.py::EventPublisher."""

    def __init__(self, *, logger: logging.Logger | None = None) -> None:
        self._logger = logger if logger is not None else logging.getLogger(LOGGER_NAME)

    def publish_progress(self, track_run_id: TrackRunId, message: str, percentage: float) -> None:
        self._logger.info("progression %.0f%% : %s", percentage * 100, message)

    def publish_module_status(
        self, track_run_id: TrackRunId, module_name: str, status: ModuleStatus
    ) -> None:
        self._logger.info("module %s -> %s", module_name, status.value)
