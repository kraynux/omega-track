# Copyright (c) 2026 kraynux - Licence MIT
"""Cablage des adaptateurs concrets derriere les ports - consomme
uniquement par app/bootstrap.py (racine de composition) et par
interfaces/ (sous TYPE_CHECKING uniquement, jamais a l'execution).

Phase 9 : premiere extension reelle depuis la Phase 1 (les Phases 3-8
ont chacune construit leurs propres ports/adaptateurs mais aucune
n'avait encore de consommateur reel qui justifie de les cabler ici -
meme discipline documentee a chaque phase concernee). `sqlite3.Connection`/
`httpx.Client` sont importes directement ici (jamais dans core/domain/
application/ports) : `app/` est la racine de composition, hors des
contrats d'import-linter de confinement technologique, meme patron reel
que `omega_check.app.dependency_container.DependencyContainer`."""
from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import httpx
from omega_lib.ports.declaration import ContactSupportServices

from omega_track.application.orchestrators.export_orchestrator import ExportOrchestrator
from omega_track.application.orchestrators.track_orchestrator import TrackOrchestrator
from omega_track.ports.collectors.archive_collector import ArchiveCollector
from omega_track.ports.collectors.bgp_collector import BgpCollector
from omega_track.ports.collectors.certificate_transparency_collector import (
    CertificateTransparencyCollector,
)
from omega_track.ports.collectors.dns_collector import DnsCollector
from omega_track.ports.collectors.rdap_collector import RdapCollector
from omega_track.ports.collectors.reputation_collector import ReputationCollector
from omega_track.ports.collectors.traceroute_collector import TracerouteCollector
from omega_track.ports.repositories.export_repository import ExportRepository
from omega_track.ports.repositories.finding_repository import FindingRepository
from omega_track.ports.repositories.geoip_database_repository import GeoipDatabaseRepository
from omega_track.ports.repositories.settings_repository import SettingsRepository
from omega_track.ports.repositories.target_repository import TargetRepository
from omega_track.ports.repositories.track_profile_repository import TrackProfileRepository
from omega_track.ports.repositories.track_run_repository import TrackRunRepository
from omega_track.ports.services.database_updater import DatabaseUpdater
from omega_track.ports.services.event_publisher import EventPublisher
from omega_track.ports.services.geoip_resolver import GeoIpResolver
from omega_track.ports.services.log_correlation import LogCorrelation
from omega_track.ports.services.reverse_dns_resolver import ReverseDnsResolver
from omega_track.ports.services.secret_store import SecretStore
from omega_track.ports.terminal_detector import TerminalDetector
from omega_track.shared.typing import IdFactory


@dataclass
class DependencyContainer:
    clock: Callable[[], datetime]
    id_factory: IdFactory
    terminal_detector: TerminalDetector

    target_repository: TargetRepository
    track_profile_repository: TrackProfileRepository
    track_run_repository: TrackRunRepository
    finding_repository: FindingRepository
    export_repository: ExportRepository
    geoip_database_repository: GeoipDatabaseRepository
    settings_repository: SettingsRepository
    secret_store: SecretStore

    geoip_resolver: GeoIpResolver
    reverse_dns_resolver: ReverseDnsResolver
    dns_collector: DnsCollector
    rdap_collector: RdapCollector
    traceroute_collector: TracerouteCollector
    database_updater: DatabaseUpdater
    ct_collector: CertificateTransparencyCollector
    archive_collector: ArchiveCollector
    bgp_collector: BgpCollector
    virustotal_collector: ReputationCollector
    hibp_collector: ReputationCollector

    event_publisher: EventPublisher
    log_correlation: LogCorrelation
    track_orchestrator: TrackOrchestrator
    export_orchestrator: ExportOrchestrator

    var_dir: Path
    default_exports_dir: Path
    default_geoip_dir: Path
    default_screenshots_dir: Path
    geoip_db_paths: dict[str, Path]
    """Chemin du fichier MMDB par fournisseur ('dbip'/'maxmind'), deja
    resolu par bootstrap.py via infrastructure/config/paths.py -
    interfaces/ ne peut pas appeler cette fonction directement (contrat
    import-linter "interfaces independant de infrastructure"), donc la
    CLI (Phase 9, commande `geoip update`) consomme ce dict deja resolu
    plutot que de dupliquer la convention de nommage elle-meme."""

    connection: sqlite3.Connection
    http_client: httpx.Client
    contact_support: ContactSupportServices | None = None
    """Aide -> Contact et support (omega-lib, D-016, 2026-11-09) : declaration anonyme une seule
    fois, mises a jour, navigateur. None : bouton masque (conteneur partiel des tests)."""

    def close(self) -> None:
        self.connection.close()
        self.http_client.close()
