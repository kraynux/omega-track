# Copyright (c) 2026 kraynux - Licence MIT
"""Verification d'integrite d'une base GeoIP telechargee (Phase 5) :
checksum pour la tracabilite (persiste dans GeoIpDatabaseStatus.checksum),
validation de format avant tout remplacement atomique de l'ancienne base
(voir database_updater.py, plan de dev §5 "Regles d'update")."""
from __future__ import annotations

import hashlib
from pathlib import Path

import maxminddb
from maxminddb.errors import InvalidDatabaseError

_CHUNK_SIZE = 65536


def compute_checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(_CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_mmdb(path: Path) -> bool:
    """Un fichier corrompu/tronque/absent renvoie False, jamais une
    exception - c'est a l'appelant (database_updater.py) de decider quoi
    faire d'une base invalide (jamais remplacer l'ancienne)."""
    try:
        reader = maxminddb.open_database(path)
    except (InvalidDatabaseError, OSError, ValueError):
        return False
    reader.close()
    return True
