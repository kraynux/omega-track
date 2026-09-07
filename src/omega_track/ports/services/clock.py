# Copyright (c) 2026 kraynux - Licence MIT
"""Alias de type pour l'horloge injectee - un simple `Callable`, pas une
classe Protocol : meme convention que CHECK
(`app/container.py::DependencyContainer.clock: Callable[[], datetime]`),
pas besoin d'une abstraction plus lourde pour une fonction a zero argument."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

Clock = Callable[[], datetime]
