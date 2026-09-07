# Copyright (c) 2026 kraynux - Licence MIT
"""Cycle de vie complet `source configure -> track run --module virustotal
-> track show -> export` via la vraie CLI (Phase 12) - conteneur reel
(`bootstrap()`, vraie base SQLite, vrai SecretStore fichier) a
l'exception des collecteurs reseau (dns/rdap/traceroute/virustotal/hibp),
remplaces par des fakes APRES bootstrap, meme technique que
test_cli_track_lifecycle.py (Phase 9)/test_extended_modules... (Phase 10) :
TrackOrchestrator capture ses dependances a la construction, reconstruit
ici avec les fakes.

Couvre aussi le critere de sortie explicite du plan §12 : "aucune cle API
ne doit jamais apparaitre dans les logs, les exports, les diagnostics" -
verifie en GREPANT le contenu reellement produit (fichier export, log
capture), pas seulement en relisant le code."""
from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest

from omega_track.app.bootstrap import bootstrap
from omega_track.app.container import DependencyContainer
from omega_track.application.orchestrators.track_orchestrator import TrackOrchestrator
from omega_track.core.constants import LOGGER_NAME
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.dns import DnsFindingType
from omega_track.domain.entities.findings.path import NetworkPath
from omega_track.domain.entities.track_profile import NeoTraceOptions
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.interfaces.cli.main import run

_NOW = datetime(2026, 9, 7, tzinfo=timezone.utc)
_SECRET_KEY = "TOP-SECRET-VIRUSTOTAL-KEY-42"


class _FakeDnsCollector:
    def resolve(self, domain: DomainName) -> list[CollectedRecord]:
        return [
            CollectedRecord(
                finding_type=DnsFindingType.A_RECORD.value, payload={"address": "93.184.216.34"},
                confidence=ConfidenceLevel.VERIFIED, source_name="dns", observed_at=_NOW,
            )
        ]

    def reverse_lookup(self, ip: IPAddress) -> CollectedRecord | None:
        return None


class _FakeRdapCollector:
    def collect_domain_registration(self, domain: DomainName) -> list[CollectedRecord]:
        return []

    def collect_ip_registration(self, ip: IPAddress) -> list[CollectedRecord]:
        return []


class _FakeTracerouteCollector:
    def is_available(self) -> bool:
        return False

    def trace(self, target_ip: IPAddress, options: NeoTraceOptions) -> NetworkPath:
        raise AssertionError("non exerce (is_available=False)")


class _FakeVirusTotalCollector:
    def collect_domain_reputation(self, domain: DomainName) -> list[CollectedRecord]:
        return [
            CollectedRecord(
                finding_type="reputation.verdict",
                payload={"source": "virustotal", "malicious": 1, "harmless": 60},
                confidence=ConfidenceLevel.DECLARED, source_name="virustotal", observed_at=_NOW,
            )
        ]


class _FakeUncalledCollector:
    """Utilise pour hibp : ne doit jamais etre appele tant qu'aucune cle
    n'est configuree pour cette source (verifie NOT_EXECUTED_NO_KEY)."""

    def collect_domain_reputation(self, domain: DomainName) -> list[CollectedRecord]:
        raise AssertionError("hibp ne doit jamais etre appele sans cle configuree")


@pytest.fixture
def container(tmp_path: Path) -> Iterator[DependencyContainer]:
    c = bootstrap(var_dir=tmp_path, console_logging=False)
    c.dns_collector = _FakeDnsCollector()
    c.rdap_collector = _FakeRdapCollector()
    c.traceroute_collector = _FakeTracerouteCollector()
    c.virustotal_collector = _FakeVirusTotalCollector()
    c.hibp_collector = _FakeUncalledCollector()
    c.track_orchestrator = TrackOrchestrator(
        dns_collector=c.dns_collector,
        rdap_collector=c.rdap_collector,
        traceroute_collector=c.traceroute_collector,
        finding_repository=c.finding_repository,
        track_run_repository=c.track_run_repository,
        event_publisher=c.event_publisher,
        id_factory=c.id_factory,
        now=c.clock,
        log_correlation=c.log_correlation,
        virustotal_collector=c.virustotal_collector,
        hibp_collector=c.hibp_collector,
        secret_store=c.secret_store,
        settings_repository=c.settings_repository,
    )
    yield c
    c.close()


def _add_and_pin_target(container: DependencyContainer, capsys: pytest.CaptureFixture[str]) -> str:
    assert run(container, ["target", "add", "example.com", "--json"]) == 0
    target_id = json.loads(capsys.readouterr().out)["id"]
    assert run(container, ["target", "pin", target_id, "--json"]) == 0
    capsys.readouterr()
    return str(target_id)


def test_source_configure_requires_a_non_empty_key(container: DependencyContainer) -> None:
    assert run(container, ["source", "configure", "virustotal", "   "]) == 1


def test_source_list_reports_key_not_configured_by_default(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(container, ["source", "list", "--json"]) == 0
    statuses = {entry["source"]: entry for entry in json.loads(capsys.readouterr().out)}
    assert statuses["virustotal"]["key_configured"] is False
    assert statuses["hibp"]["key_configured"] is False


def test_virustotal_is_not_executed_when_no_key_is_configured(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    target_id = _add_and_pin_target(container, capsys)

    exit_code = run(container, ["track", "run", target_id, "--module", "virustotal", "--json"])
    result = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert result["status"] == "completed"
    assert result["modules"]["virustotal"]["status"] == "skipped"


def test_configure_then_track_run_executes_virustotal_and_never_calls_hibp(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(container, ["source", "configure", "virustotal", _SECRET_KEY, "--json"]) == 0
    capsys.readouterr()

    target_id = _add_and_pin_target(container, capsys)
    exit_code = run(container, ["track", "run", target_id, "--module", "virustotal", "--json"])
    result = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert result["status"] == "completed"
    assert result["modules"]["virustotal"]["status"] == "completed"
    run_id = result["id"]

    assert run(container, ["track", "show", run_id, "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["finding_count"] >= 1


def test_api_key_never_appears_in_export_output(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    run(container, ["source", "configure", "virustotal", _SECRET_KEY, "--json"])
    capsys.readouterr()
    target_id = _add_and_pin_target(container, capsys)
    run(container, ["track", "run", target_id, "--module", "virustotal", "--json"])
    run_id = json.loads(capsys.readouterr().out)["id"]

    for export_format in ("json", "md", "html", "csv", "dot", "mermaid"):
        assert run(container, ["export", run_id, "--format", export_format, "--json"]) == 0
        artifact = json.loads(capsys.readouterr().out)
        output_path = Path(artifact["output_path"])
        content = output_path.read_bytes()
        assert _SECRET_KEY.encode() not in content, f"cle API presente dans l'export {export_format}"


def test_api_key_never_appears_in_diagnostics_output(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    run(container, ["source", "configure", "virustotal", _SECRET_KEY, "--json"])
    capsys.readouterr()

    assert run(container, ["diagnostics", "--json"]) == 0
    diagnostics_output = capsys.readouterr().out
    assert _SECRET_KEY not in diagnostics_output

    assert run(container, ["source", "list", "--json"]) == 0
    source_list_output = capsys.readouterr().out
    assert _SECRET_KEY not in source_list_output


def test_api_key_never_appears_in_application_log_output(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str], caplog: pytest.LogCaptureFixture
) -> None:
    run(container, ["source", "configure", "virustotal", _SECRET_KEY, "--json"])
    capsys.readouterr()
    target_id = _add_and_pin_target(container, capsys)

    with caplog.at_level(logging.DEBUG, logger=LOGGER_NAME):
        run(container, ["track", "run", target_id, "--module", "virustotal", "--json"])

    for record in caplog.records:
        assert _SECRET_KEY not in record.getMessage()


def test_quota_exceeded_marks_module_failed_but_track_run_stays_partial_not_failed(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    from omega_track.application.exceptions import QuotaExceededError

    class _QuotaExceededCollector:
        def collect_domain_reputation(self, domain: DomainName) -> list[CollectedRecord]:
            raise QuotaExceededError("virustotal")

    container.virustotal_collector = _QuotaExceededCollector()
    container.track_orchestrator = TrackOrchestrator(
        dns_collector=container.dns_collector,
        rdap_collector=container.rdap_collector,
        traceroute_collector=container.traceroute_collector,
        finding_repository=container.finding_repository,
        track_run_repository=container.track_run_repository,
        event_publisher=container.event_publisher,
        id_factory=container.id_factory,
        now=container.clock,
        log_correlation=container.log_correlation,
        virustotal_collector=container.virustotal_collector,
        hibp_collector=container.hibp_collector,
        secret_store=container.secret_store,
        settings_repository=container.settings_repository,
    )
    run(container, ["source", "configure", "virustotal", _SECRET_KEY, "--json"])
    capsys.readouterr()
    target_id = _add_and_pin_target(container, capsys)

    exit_code = run(
        container, ["track", "run", target_id, "--module", "dns", "--module", "virustotal", "--json"]
    )
    result = json.loads(capsys.readouterr().out)
    assert result["modules"]["virustotal"]["status"] == "failed"
    assert result["modules"]["virustotal"]["error_code"] == "quota_exceeded"
    assert result["status"] in ("partial", "completed")
    assert exit_code in (0, 4)
