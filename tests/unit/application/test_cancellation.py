# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_track.application.orchestrators.cancellation import CancellationToken


def test_token_starts_not_cancelled() -> None:
    assert not CancellationToken().is_cancelled


def test_cancel_flips_the_flag() -> None:
    token = CancellationToken()
    token.cancel()
    assert token.is_cancelled
