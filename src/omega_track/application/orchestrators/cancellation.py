# Copyright (c) 2026 kraynux - Licence MIT
"""Token d'annulation cooperatif (plan de dev §7) - verifie entre les
phases ET a chaque iteration d'une boucle d'enrichissement par IP, jamais
preemptif : un appel de collecteur deja en cours (ex. un `subprocess.run`
de traceroute) va toujours a son terme, seul le DEMARRAGE du prochain
module/de la prochaine IP est empeche. Suffisant pour les criteres de
sortie reels de cette phase ("annulation propre sans donnees
corrompues") sans introduire de threads/asyncio dans des collecteurs
synchrones qui n'ont jamais ete concus pour ca (Phase 6)."""
from __future__ import annotations


class CancellationToken:
    def __init__(self) -> None:
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled
