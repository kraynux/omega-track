# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import logging

import pytest

from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.domain.value_objects.statuses import ModuleStatus
from omega_track.infrastructure.logging.config import LOGGER_NAME
from omega_track.infrastructure.logging.event_publisher import LoggingEventPublisher


def test_publish_progress_logs_percentage_and_message(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("test-event-publisher-progress")
    logger.setLevel(logging.INFO)
    publisher = LoggingEventPublisher(logger=logger)

    with caplog.at_level(logging.INFO, logger=logger.name):
        publisher.publish_progress(TrackRunId("run-1"), "identite terminee", 0.5)

    assert "progression 50% : identite terminee" in caplog.text


def test_publish_module_status_logs_module_and_status(caplog: pytest.LogCaptureFixture) -> None:
    logger = logging.getLogger("test-event-publisher-module-status")
    logger.setLevel(logging.INFO)
    publisher = LoggingEventPublisher(logger=logger)

    with caplog.at_level(logging.INFO, logger=logger.name):
        publisher.publish_module_status(TrackRunId("run-1"), "dns", ModuleStatus.COMPLETED)

    assert "module dns -> completed" in caplog.text


def test_default_logger_is_the_application_logger(caplog: pytest.LogCaptureFixture) -> None:
    publisher = LoggingEventPublisher()

    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        publisher.publish_progress(TrackRunId("run-1"), "test", 1.0)

    assert any(record.name == LOGGER_NAME for record in caplog.records)
