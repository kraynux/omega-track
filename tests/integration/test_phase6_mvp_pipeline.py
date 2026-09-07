# Copyright (c) 2026 kraynux - Licence MIT
"""Preuve du critere de sortie de la Phase 6 : "Un domaine ou une IP peut
produire un rapport persistant : DNS/RDAP/GeoIP/NeoTrace/resume. Le
resultat reste exploitable meme avec un ou plusieurs modules en erreur."

Assemble ici, ad hoc, les vrais collecteurs de la Phase 6 (DNS/RDAP/
traceroute, GeoIP deja reel depuis la Phase 5) + le budget D-012 + la
conversion CollectedRecord -> Finding + la persistance SQLite reelle de
la Phase 4. Ce n'est PAS le TrackOrchestrator (Phase 7, qui apportera
progression/annulation/parallelisme autour d'un enchainement equivalent)
ni report_builder.py (Phase 8, qui reconstruit un IdentityReport depuis
les findings deja persistes pour l'export) - seulement la preuve que les
pieces de la Phase 6 se combinent reellement, y compris quand un module
echoue (RDAP simule en erreur sur une IP)."""
from __future__ import annotations

import itertools
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import dns.resolver
import httpx

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.application.policies.execution_budget import (
    allocate_enrichment_budget,
    select_neotrace_targets,
)
from omega_track.domain.entities.findings.network import NetworkFindingType
from omega_track.domain.entities.findings.path import PathFindingType
from omega_track.domain.entities.track_profile import ExecutionLimits, NeoTraceOptions
from omega_track.domain.services.finding_builder import build_finding
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import ModuleRunId, TrackRunId
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.infrastructure.collectors.dns.dnspython_collector import DnsPythonCollector
from omega_track.infrastructure.collectors.network.subprocess_traceroute_collector import (
    SubprocessTracerouteCollector,
)
from omega_track.infrastructure.collectors.rdap.http_rdap_collector import HttpRdapCollector
from omega_track.infrastructure.geoip.mmdb_reader import MmdbGeoIpResolver, MmdbReader
from omega_track.infrastructure.repositories.sqlite.finding_repository import (
    SqliteFindingRepository,
)

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)
_RUN_ID = TrackRunId("run-phase6")
_MODULE_RUN_ID = ModuleRunId("module-1")


class _FakeMmdbDatabase:
    """Simule une base GeoIP locale sans fichier .mmdb reel (deja le
    patron de test etabli en Phase 5 - voir MmdbReader.opener)."""

    def get(self, ip: str) -> dict[str, object] | None:
        return {"country": {"iso_code": "US"}}

    def close(self) -> None:
        pass


class _NoPtrResolver:
    """ReverseDnsResolver factice : jamais de PTR trouve, pour garder ce
    test concentre sur GeoIP/ASN plutot que sur une 3e source PTR."""

    def resolve_ptr(self, ip: IPAddress) -> str | None:
        return None


def _geoip_resolver() -> MmdbGeoIpResolver:
    reader = MmdbReader(Path("/unused.mmdb"), opener=lambda _path: _FakeMmdbDatabase())
    return MmdbGeoIpResolver(reader, source="dbip")


def _dns_resolve_fn(name: str, rdtype: str) -> list[str]:
    answers = {
        "A": ["93.184.216.34", "93.184.216.35"],
        "AAAA": ["2606:2800:220:1:248:1893:25c8:1946"],
    }
    if rdtype not in answers:
        raise dns.resolver.NoAnswer()
    return answers[rdtype]


def _traceroute_run(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
    target = args[-1]
    stdout = f" 1  gateway (192.168.1.1)  1.0 ms\n 2  {target} ({target})  10.0 ms\n"
    return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr="")


def test_mvp_pipeline_produces_a_persistent_report_even_with_a_failing_module(
    connection: sqlite3.Connection,
) -> None:
    domain = DomainName.parse("example.com")
    limits = ExecutionLimits()
    id_factory = (str(n) for n in itertools.count(1)).__next__
    collected: list[tuple[CollectedRecord, CollectionMode]] = []

    # 1-2. DNS (resolveur systeme simule)
    dns_collector = DnsPythonCollector(now=lambda: _NOW, resolve_fn=_dns_resolve_fn)
    dns_records = dns_collector.resolve(domain)
    collected += [(record, CollectionMode.ACTIVE_LIGHT) for record in dns_records]

    resolved_ips = [
        IPAddress.parse(record.payload["address"])
        for record in dns_records
        if record.finding_type in ("dns.a_record", "dns.aaaa_record")
    ]

    # 3. Budget d'enrichissement (D-012)
    budget = allocate_enrichment_budget(resolved_ips, limits=limits)
    for excess_ip in budget.excess:
        collected.append(
            (
                CollectedRecord(
                    finding_type=NetworkFindingType.IP_OBSERVED.value,
                    payload={"address": str(excess_ip)},
                    confidence=dns_records[0].confidence,
                    source_name="dns",
                    observed_at=_NOW,
                ),
                CollectionMode.ACTIVE_LIGHT,
            )
        )

    # 4. RDAP domaine + IPs retenues - une IP simulee en echec (429) : ne bloque pas le run (D-015)
    def rdap_handler(request: httpx.Request) -> httpx.Response:
        if str(request.url).endswith("93.184.216.35"):
            return httpx.Response(429)
        return httpx.Response(200, json={"handle": "NET-1", "name": "EXAMPLE-NET", "country": "US"})

    rdap_collector = HttpRdapCollector(
        http_client=httpx.Client(transport=httpx.MockTransport(rdap_handler)), now=lambda: _NOW
    )
    collected += [
        (record, CollectionMode.PASSIVE_PUBLIC)
        for record in rdap_collector.collect_domain_registration(domain)
    ]

    rdap_module_degraded = False
    for ip in budget.enriched:
        try:
            collected += [
                (record, CollectionMode.PASSIVE_PUBLIC)
                for record in rdap_collector.collect_ip_registration(ip)
            ]
        except CollectorUnavailableError:
            rdap_module_degraded = True

    assert rdap_module_degraded, "le test doit exercer le chemin d'echec RDAP, sinon il ne prouve rien"

    # 5-6. NeoTrace sur les IPs effectivement utilisees (D-012, cap 3) + enrichissement GeoIP/hops
    neotrace_targets = select_neotrace_targets(budget, limits=limits)
    traceroute_collector = SubprocessTracerouteCollector(
        geoip_resolver=_geoip_resolver(),
        reverse_dns_resolver=_NoPtrResolver(),
        run_fn=_traceroute_run,
        which_fn=lambda name: "/usr/bin/traceroute" if name == "traceroute" else None,
    )
    for target_ip in neotrace_targets:
        path = traceroute_collector.trace(target_ip, NeoTraceOptions())
        for hop in path.hops:
            if hop.ip is None:
                continue
            payload = {
                "sequence": hop.sequence,
                "ip": str(hop.ip),
                "hostname": hop.hostname,
                "rtt_ms": hop.rtt_ms,
            }
            collected.append(
                (
                    CollectedRecord(
                        finding_type=PathFindingType.HOP.value,
                        payload=payload,
                        confidence=dns_records[0].confidence,
                        source_name="neotrace",
                        observed_at=_NOW,
                    ),
                    CollectionMode.ACTIVE_LIGHT,
                )
            )

    # 7-8. Conversion + persistance reelle (Phase 4)
    findings = [
        build_finding(
            record,
            track_run_id=_RUN_ID,
            module_run_id=_MODULE_RUN_ID,
            collection_mode=mode,
            id_factory=id_factory,
            now=lambda: _NOW,
        )
        for record, mode in collected
    ]

    repository = SqliteFindingRepository(connection)
    repository.save_findings(findings)

    persisted = repository.list_findings_for_run(_RUN_ID)
    persisted_types = {finding.finding_type for finding in persisted}

    assert "dns.a_record" in persisted_types
    assert "dns.aaaa_record" in persisted_types
    assert "network.ip_observed" not in persisted_types  # aucune IP en exces avec ce budget par defaut
    assert "network.netblock" in persisted_types
    assert "path.hop" in persisted_types
    assert len(persisted) == len(findings)
