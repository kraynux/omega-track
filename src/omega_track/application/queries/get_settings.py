# Copyright (c) 2026 kraynux - Licence MIT
"""Use case GetSettings (plan de dev §9 `config show`) - `config set
<key> <value>` n'a pas d'equivalent use case dedie : c'est un passage
generique cle/valeur (`SettingsRepository.set`, D-008) sans aucune
logique metier a encapsuler, la CLI (Phase 9) l'appelle directement -
meme discipline que CHECK pour ses reglages generiques."""
from __future__ import annotations

from omega_track.ports.repositories.settings_repository import SettingsRepository


def get_settings(*, settings_repository: SettingsRepository) -> dict[str, str]:
    return settings_repository.all()
