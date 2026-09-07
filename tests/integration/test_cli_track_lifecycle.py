# Copyright (c) 2026 kraynux - Licence MIT
"""Cycle de vie complet `target add/pin -> track run -> track status/show
-> export -> track replay -> track cancel` via la vraie CLI (Phase 9) -
conteneur reel (`bootstrap()`, vraie base SQLite, vrais repositories,
vrai TrackOrchestrator/ExportOrchestrator) a l'exception des 3
collecteurs reseau (dns/rdap/traceroute), remplaces par des fakes APRES
bootstrap : TrackOrchestrator capture ses dependances a la construction
(Phase 7, aucune re-lecture du container a l'appel), donc reassigner
`container.dns_collector` seul ne suffirait pas - le TrackOrchestrator
lui-meme est reconstruit ici avec les fakes, en reutilisant tout le
reste (repositories/event_publisher/log_correlation) tel que bootstrap()
l'a reellement cable. Seule facon de tester le cycle complet sans reseau
reel (D-014/Phase 6 : aucun test de ce projet ne depend du reseau)."""
from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest

from omega_track.app.bootstrap import bootstrap
from omega_track.app.container import DependencyContainer
from omega_track.application.orchestrators.track_orchestrator import TrackOrchestrator
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.dns import DnsFindingType
from omega_track.domain.entities.findings.path import NetworkPath
from omega_track.domain.entities.track_profile import NeoTraceOptions
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.interfaces.cli.main import run

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeDnsCollector:
    def resolve(self, domain: DomainName) -> list[CollectedRecord]:
        return [
            CollectedRecord(
                finding_type=DnsFindingType.A_RECORD.value,
                payload={"address": "93.184.216.34"},
                confidence=ConfidenceLevel.VERIFIED,
                source_name="dns",
                observed_at=_NOW,
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


class _FakeCtCollector:
    def collect_certificates(self, domain: DomainName) -> list[CollectedRecord]:
        return [
            CollectedRecord(
                finding_type="certificate.observed",
                payload={
                    "serial_number": "abc123", "issuer_name": "Let's Encrypt",
                    "not_before": None, "not_after": None,
                },
                confidence=ConfidenceLevel.DECLARED,
                source_name="crt.sh",
                observed_at=_NOW,
            )
        ]

    def distinct_log_count(self, domain: DomainName) -> int:
        return 1


@pytest.fixture
def container(tmp_path: Path) -> Iterator[DependencyContainer]:
    c = bootstrap(var_dir=tmp_path, console_logging=False)
    c.dns_collector = _FakeDnsCollector()
    c.rdap_collector = _FakeRdapCollector()
    c.traceroute_collector = _FakeTracerouteCollector()
    c.ct_collector = _FakeCtCollector()
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
        ct_collector=c.ct_collector,
    )
    yield c
    c.close()


def _add_and_pin_target(container: DependencyContainer, capsys: pytest.CaptureFixture[str]) -> str:
    assert run(container, ["target", "add", "example.com", "--json"]) == 0
    target_id = json.loads(capsys.readouterr().out)["id"]
    assert run(container, ["target", "pin", target_id, "--json"]) == 0
    capsys.readouterr()
    return str(target_id)


def test_full_lifecycle_run_status_show_export_replay(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    target_id = _add_and_pin_target(container, capsys)

    exit_code = run(container, ["track", "run", target_id, "--module", "dns", "--json"])
    result = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert result["status"] == "completed"
    run_id = result["id"]

    assert run(container, ["track", "status", run_id, "--json"]) == 0
    status = json.loads(capsys.readouterr().out)
    assert status["status"] == "completed"

    assert run(container, ["track", "show", run_id, "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["finding_count"] >= 1

    assert run(container, ["export", run_id, "--format", "json", "--json"]) == 0
    artifact = json.loads(capsys.readouterr().out)
    assert Path(artifact["output_path"]).exists()

    assert run(container, ["track", "replay", run_id, "--json"]) == 0
    replayed = json.loads(capsys.readouterr().out)
    assert replayed["id"] != run_id
    assert replayed["status"] == "completed"


def test_track_run_without_authorization_is_refused(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(container, ["target", "add", "example.com", "--json"]) == 0
    target_id = json.loads(capsys.readouterr().out)["id"]

    assert run(container, ["track", "run", target_id, "--module", "dns"]) == 2


def test_track_run_with_explicit_authorize_flag_succeeds(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(container, ["target", "add", "example.com", "--json"]) == 0
    target_id = json.loads(capsys.readouterr().out)["id"]
    capsys.readouterr()

    exit_code = run(container, ["track", "run", target_id, "--module", "dns", "--authorize", "--json"])
    assert exit_code == 0


def test_track_cancel_on_completed_run_is_a_no_op(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    target_id = _add_and_pin_target(container, capsys)
    run(container, ["track", "run", target_id, "--module", "dns", "--json"])
    run_id = json.loads(capsys.readouterr().out)["id"]

    assert run(container, ["track", "cancel", run_id, "--json"]) == 0
    cancelled = json.loads(capsys.readouterr().out)
    assert cancelled["status"] == "completed"


def test_track_status_missing_run_returns_unavailable_exit_code(container: DependencyContainer) -> None:
    assert run(container, ["track", "status", "missing-run-id"]) == 3


def test_export_with_invalid_format_returns_validation_exit_code(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    """argparse valide `--format` via `choices=` avant meme d'atteindre
    notre handler - rejete par _ArgumentParser.error(), qui leve
    SystemExit(1) (remappe depuis le 2 par defaut d'argparse, voir
    interfaces/cli/main.py::_ArgumentParser), jamais un retour de
    fonction normal - meme comportement que --help/--version deja
    couvert par test_cli_smoke.py."""
    target_id = _add_and_pin_target(container, capsys)
    run(container, ["track", "run", target_id, "--module", "dns", "--json"])
    run_id = json.loads(capsys.readouterr().out)["id"]

    with pytest.raises(SystemExit) as exc_info:
        run(container, ["export", run_id, "--format", "bogus"])
    assert exc_info.value.code == 1


def test_certificate_transparency_module_via_real_cli(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    target_id = _add_and_pin_target(container, capsys)

    exit_code = run(
        container, ["track", "run", target_id, "--module", "dns", "--module", "certificate_transparency", "--json"]
    )
    result = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert result["status"] == "completed"
    assert result["modules"]["certificate_transparency"]["status"] == "completed"

    run_id = result["id"]
    assert run(container, ["track", "show", run_id, "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["finding_count"] >= 2  # au moins le A record + le certificat observe
    assert report["relation_count"] >= 1  # au moins la relation certificate_san (D-011)
