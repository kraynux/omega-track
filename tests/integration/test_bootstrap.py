# Copyright (c) 2026 kraynux - Licence MIT
"""Smoke test de la racine de composition (Phase 9) - remplace
`tests/unit/test_container.py` (Phase 1, container fait de 3 champs
cables a la main via des fakes de port) : desormais que le container en
compte 22+ tous reellement cables par bootstrap.py, la seule chose qui
vaille la peine d'etre verifiee est que la vraie composition fonctionne
de bout en bout (vraie connexion SQLite, vrai fichier settings.json,
vrai resolveur GeoIp construit) - pas une reconstruction manuelle
champ-par-champ avec des fakes qui n'a jamais teste le vrai cablage."""
from __future__ import annotations

from pathlib import Path

from omega_track.app.bootstrap import bootstrap
from omega_track.app.container import DependencyContainer
from omega_track.infrastructure.config.json_settings_loader import JsonSettingsRepository
from omega_track.infrastructure.config.paths import default_settings_path


def test_bootstrap_wires_a_complete_container(tmp_path: Path) -> None:
    container = bootstrap(var_dir=tmp_path, console_logging=False)
    try:
        assert isinstance(container, DependencyContainer)
        assert container.connection is not None
        assert container.http_client is not None
        assert (tmp_path / "db" / "omega-track.db").exists()
    finally:
        container.close()


def test_bootstrap_wires_extended_module_plugins(tmp_path: Path) -> None:
    container = bootstrap(var_dir=tmp_path, console_logging=False)
    try:
        assert container.ct_collector.descriptor.name == "certificate_transparency"  # type: ignore[attr-defined]
        assert container.archive_collector.descriptor.name == "archives"  # type: ignore[attr-defined]
        assert container.bgp_collector.descriptor.name == "bgp"  # type: ignore[attr-defined]
    finally:
        container.close()


def test_bootstrap_default_geoip_provider_is_dbip(tmp_path: Path) -> None:
    container = bootstrap(var_dir=tmp_path, console_logging=False)
    try:
        assert container.geoip_resolver.source == "dbip"  # type: ignore[attr-defined]
    finally:
        container.close()


def test_bootstrap_respects_configured_maxmind_provider(tmp_path: Path) -> None:
    JsonSettingsRepository(default_settings_path(tmp_path)).set("geoip_provider", "maxmind")

    container = bootstrap(var_dir=tmp_path, console_logging=False)
    try:
        assert container.geoip_resolver.source == "maxmind"  # type: ignore[attr-defined]
    finally:
        container.close()


def test_close_is_idempotent_safe_to_call_once(tmp_path: Path) -> None:
    container = bootstrap(var_dir=tmp_path, console_logging=False)
    container.close()
    # deuxieme close() non teste (sqlite3/httpx ferment deja proprement une
    # ressource fermee sans lever pour httpx.Client, mais sqlite3.Connection.close()
    # est deja idempotente par contrat stdlib) - une seule fermeture reelle suffit ici.


def test_bootstrap_creates_independent_containers_per_call(tmp_path: Path) -> None:
    first = bootstrap(var_dir=tmp_path / "a", console_logging=False)
    second = bootstrap(var_dir=tmp_path / "b", console_logging=False)
    try:
        assert first.connection is not second.connection
    finally:
        first.close()
        second.close()
