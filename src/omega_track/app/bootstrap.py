# Copyright (c) 2026 kraynux - Licence MIT
"""Racine de composition : construit un DependencyContainer avec les
adaptateurs concrets de production. Seul module autorise a importer a la
fois infrastructure/ ET app/container.py (Phase 9 : premier cablage reel,
voir container.py)."""
from __future__ import annotations

from pathlib import Path

import httpx
from omega_lib.infrastructure.terminal.detector import SystemTerminalDetector
from omega_lib.shared.clock import utc_now
from omega_lib.shared.ids import new_id

from omega_track.app.container import DependencyContainer
from omega_track.application.orchestrators.export_orchestrator import ExportOrchestrator
from omega_track.application.orchestrators.track_orchestrator import TrackOrchestrator
from omega_track.application.policies.provider_selection import resolve_active_geoip_provider
from omega_track.application.queries.get_source_disclosure import secret_name_for
from omega_track.infrastructure.collectors.archives.wayback_collector import WaybackCollector
from omega_track.infrastructure.collectors.bgp.ripe_stat_collector import RipeStatCollector
from omega_track.infrastructure.collectors.certificates.crtsh_collector import CrtShCollector
from omega_track.infrastructure.collectors.dns.dnspython_collector import DnsPythonCollector
from omega_track.infrastructure.collectors.dns.reverse_dns_collector import (
    DnsPythonReverseDnsResolver,
)
from omega_track.infrastructure.collectors.network.subprocess_traceroute_collector import (
    SubprocessTracerouteCollector,
)
from omega_track.infrastructure.collectors.rdap.http_rdap_collector import HttpRdapCollector
from omega_track.infrastructure.collectors.reputation.hibp_collector import HibpHttpCollector
from omega_track.infrastructure.collectors.reputation.virustotal_collector import (
    VirusTotalHttpCollector,
)
from omega_track.infrastructure.config import paths
from omega_track.infrastructure.config.json_settings_loader import JsonSettingsRepository
from omega_track.infrastructure.config.secret_store_adapter import FileSecretStore
from omega_track.infrastructure.exporters.csv_file_exporter import CsvFileExporter
from omega_track.infrastructure.exporters.graphviz_dot_exporter import GraphvizDotExporter
from omega_track.infrastructure.exporters.jinja2_html_exporter import Jinja2HtmlExporter
from omega_track.infrastructure.exporters.json_file_exporter import JsonFileExporter
from omega_track.infrastructure.exporters.markdown_file_exporter import MarkdownFileExporter
from omega_track.infrastructure.exporters.mermaid_file_exporter import MermaidFileExporter
from omega_track.infrastructure.geoip.database_updater import HttpDatabaseUpdater
from omega_track.infrastructure.geoip.dbip_resolver import build_dbip_resolver
from omega_track.infrastructure.geoip.maxmind_resolver import build_maxmind_resolver
from omega_track.infrastructure.logging.config import APP_LOG_FILENAME, configure_logging
from omega_track.infrastructure.logging.event_publisher import LoggingEventPublisher
from omega_track.infrastructure.logging.log_correlation_adapter import ContextVarLogCorrelation
from omega_track.infrastructure.repositories.sqlite.connection import open_connection
from omega_track.infrastructure.repositories.sqlite.export_repository import SqliteExportRepository
from omega_track.infrastructure.repositories.sqlite.finding_repository import (
    SqliteFindingRepository,
)
from omega_track.infrastructure.repositories.sqlite.geoip_database_repository import (
    SqliteGeoipDatabaseRepository,
)
from omega_track.infrastructure.repositories.sqlite.target_repository import SqliteTargetRepository
from omega_track.infrastructure.repositories.sqlite.track_profile_repository import (
    SqliteTrackProfileRepository,
)
from omega_track.infrastructure.repositories.sqlite.track_run_repository import (
    SqliteTrackRunRepository,
)
from omega_track.plugins.certificates.ct_plugin import CtPlugin
from omega_track.plugins.history.archive_plugin import ArchivePlugin
from omega_track.plugins.network.asn_enrichment_plugin import AsnEnrichmentPlugin
from omega_track.plugins.reputation.hibp_plugin import HibpPlugin
from omega_track.plugins.reputation.virustotal_plugin import VirusTotalPlugin

_GEOIP_PROVIDER_SETTING_KEY = "geoip_provider"


def bootstrap(*, var_dir: Path | None = None, console_logging: bool = True) -> DependencyContainer:
    """`console_logging=False` pour la TUI (voir __main__.py) : Textual
    prend le controle exclusif de l'ecran, une ecriture de log directe sur
    stderr pendant un track corromprait son rendu. Le CLI garde
    `console_logging=True` par defaut (utile pour le scriptable/debug)."""
    base = var_dir if var_dir is not None else paths.resolve_var_dir()
    configure_logging(log_path=base / APP_LOG_FILENAME, console=console_logging)

    now = utc_now
    connection = open_connection(paths.default_db_path(base))
    http_client = httpx.Client()

    settings_repository = JsonSettingsRepository(paths.default_settings_path(base))
    secret_store = FileSecretStore(paths.default_secrets_path(base))

    provider = resolve_active_geoip_provider(settings_repository.get(_GEOIP_PROVIDER_SETTING_KEY))
    geoip_resolver = build_dbip_resolver(base) if provider == "dbip" else build_maxmind_resolver(base)
    reverse_dns_resolver = DnsPythonReverseDnsResolver()

    dns_collector = DnsPythonCollector(now=now)
    rdap_collector = HttpRdapCollector(http_client=http_client, now=now)
    traceroute_collector = SubprocessTracerouteCollector(
        geoip_resolver=geoip_resolver, reverse_dns_resolver=reverse_dns_resolver
    )
    database_updater = HttpDatabaseUpdater(http_client=http_client, secret_store=secret_store, now=now)

    ct_collector = CtPlugin(CrtShCollector(http_client=http_client, now=now))
    archive_collector = ArchivePlugin(WaybackCollector(http_client=http_client, now=now))
    bgp_collector = AsnEnrichmentPlugin(RipeStatCollector(http_client=http_client, now=now))
    virustotal_collector = VirusTotalPlugin(
        VirusTotalHttpCollector(
            http_client=http_client,
            api_key=secret_store.get_secret(secret_name_for("virustotal")) or "",
            now=now,
        )
    )
    hibp_collector = HibpPlugin(
        HibpHttpCollector(
            http_client=http_client, api_key=secret_store.get_secret(secret_name_for("hibp")) or "", now=now
        )
    )

    target_repository = SqliteTargetRepository(connection)
    track_profile_repository = SqliteTrackProfileRepository(connection)
    track_run_repository = SqliteTrackRunRepository(connection)
    finding_repository = SqliteFindingRepository(connection)
    export_repository = SqliteExportRepository(connection)
    geoip_database_repository = SqliteGeoipDatabaseRepository(connection)

    event_publisher = LoggingEventPublisher()
    log_correlation = ContextVarLogCorrelation()

    track_orchestrator = TrackOrchestrator(
        dns_collector=dns_collector,
        rdap_collector=rdap_collector,
        traceroute_collector=traceroute_collector,
        finding_repository=finding_repository,
        track_run_repository=track_run_repository,
        event_publisher=event_publisher,
        id_factory=new_id,
        now=now,
        log_correlation=log_correlation,
        ct_collector=ct_collector,
        archive_collector=archive_collector,
        bgp_collector=bgp_collector,
        virustotal_collector=virustotal_collector,
        hibp_collector=hibp_collector,
        secret_store=secret_store,
        settings_repository=settings_repository,
    )
    export_orchestrator = ExportOrchestrator(
        track_run_repository=track_run_repository,
        target_repository=target_repository,
        finding_repository=finding_repository,
        export_repository=export_repository,
        exporters={
            "json": JsonFileExporter(),
            "markdown": MarkdownFileExporter(),
            "html": Jinja2HtmlExporter(),
            "csv": CsvFileExporter(),
            "dot": GraphvizDotExporter(),
            "mermaid": MermaidFileExporter(),
        },
        id_factory=new_id,
        now=now,
    )

    return DependencyContainer(
        clock=now,
        id_factory=new_id,
        terminal_detector=SystemTerminalDetector(),
        target_repository=target_repository,
        track_profile_repository=track_profile_repository,
        track_run_repository=track_run_repository,
        finding_repository=finding_repository,
        export_repository=export_repository,
        geoip_database_repository=geoip_database_repository,
        settings_repository=settings_repository,
        secret_store=secret_store,
        geoip_resolver=geoip_resolver,
        reverse_dns_resolver=reverse_dns_resolver,
        dns_collector=dns_collector,
        rdap_collector=rdap_collector,
        traceroute_collector=traceroute_collector,
        database_updater=database_updater,
        ct_collector=ct_collector,
        archive_collector=archive_collector,
        bgp_collector=bgp_collector,
        virustotal_collector=virustotal_collector,
        hibp_collector=hibp_collector,
        event_publisher=event_publisher,
        log_correlation=log_correlation,
        track_orchestrator=track_orchestrator,
        export_orchestrator=export_orchestrator,
        var_dir=base,
        default_exports_dir=paths.default_exports_dir(base),
        default_geoip_dir=paths.default_geoip_dir(base),
        default_screenshots_dir=paths.default_screenshots_dir(base),
        geoip_db_paths={
            "dbip": paths.default_geoip_db_path("dbip", base),
            "maxmind": paths.default_geoip_db_path("maxmind", base),
        },
        connection=connection,
        http_client=http_client,
    )
