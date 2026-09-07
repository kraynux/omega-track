# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.application.orchestrators._context import PhaseContext
from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.application.orchestrators.phases.network_path_phase import run_network_path_phase
from omega_track.domain.entities.findings.path import NetworkHop, NetworkPath
from omega_track.domain.entities.track_profile import NeoTraceOptions
from omega_track.domain.entities.track_run import ModuleRun
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.identifiers import ModuleRunId, TrackRunId
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.domain.value_objects.statuses import ModuleStatus

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeEventPublisher:
    def publish_progress(self, track_run_id: TrackRunId, message: str, percentage: float) -> None:
        pass

    def publish_module_status(self, track_run_id: TrackRunId, module_name: str, status: ModuleStatus) -> None:
        pass


class _FakeTracerouteCollector:
    def __init__(self, *, available: bool = True, paths: dict[str, NetworkPath] | None = None, errors: set[str] | None = None) -> None:
        self._available = available
        self._paths = paths or {}
        self._errors = errors or set()
        self.trace_calls: list[str] = []

    def is_available(self) -> bool:
        return self._available

    def trace(self, target_ip: IPAddress, options: NeoTraceOptions) -> NetworkPath:
        self.trace_calls.append(str(target_ip))
        if str(target_ip) in self._errors:
            raise CollectorUnavailableError("traceroute")
        return self._paths[str(target_ip)]


def _context(*, cancelled: bool = False) -> PhaseContext:
    token = CancellationToken()
    if cancelled:
        token.cancel()
    counter = iter(f"id-{n}" for n in range(1, 1000))
    return PhaseContext(
        track_run_id=TrackRunId("run-1"),
        id_factory=counter.__next__,
        now=lambda: _NOW,
        event_publisher=_FakeEventPublisher(),
        cancellation_token=token,
    )


def _module_runs() -> dict[str, ModuleRun]:
    return {
        "neotrace": ModuleRun(
            id=ModuleRunId("mr-neotrace"), module_name="neotrace", status=ModuleStatus.PENDING,
            collection_mode=CollectionMode.ACTIVE_LIGHT,
        )
    }


def _path(target: str) -> NetworkPath:
    ip = IPAddress.parse(target)
    return NetworkPath(target_ip=ip, protocol="icmp", hops=[NetworkHop(sequence=1, ip=ip, rtt_ms=1.0)])


def test_skipped_when_no_targets() -> None:
    module_runs = _module_runs()
    result = run_network_path_phase(
        context=_context(), module_runs=module_runs, targets=[], options=NeoTraceOptions(),
        traceroute_collector=_FakeTracerouteCollector(),
    )
    assert module_runs["neotrace"].status == ModuleStatus.SKIPPED
    assert result.findings == []


def test_skipped_when_binary_unavailable() -> None:
    module_runs = _module_runs()
    result = run_network_path_phase(
        context=_context(),
        module_runs=module_runs,
        targets=[IPAddress.parse("1.1.1.1")],
        options=NeoTraceOptions(),
        traceroute_collector=_FakeTracerouteCollector(available=False),
    )
    assert module_runs["neotrace"].status == ModuleStatus.SKIPPED
    assert not result.degraded


def test_completes_and_produces_hop_findings() -> None:
    module_runs = _module_runs()
    target = IPAddress.parse("1.1.1.1")
    collector = _FakeTracerouteCollector(paths={"1.1.1.1": _path("1.1.1.1")})

    result = run_network_path_phase(
        context=_context(), module_runs=module_runs, targets=[target], options=NeoTraceOptions(),
        traceroute_collector=collector,
    )

    assert module_runs["neotrace"].status == ModuleStatus.COMPLETED
    assert len(result.paths) == 1
    assert len(result.findings) == 1
    assert result.findings[0].finding_type == "path.hop"
    assert not result.degraded


def test_partial_when_one_target_fails() -> None:
    module_runs = _module_runs()
    ok_ip = IPAddress.parse("1.1.1.1")
    bad_ip = IPAddress.parse("1.1.1.2")
    collector = _FakeTracerouteCollector(paths={"1.1.1.1": _path("1.1.1.1")}, errors={"1.1.1.2"})

    result = run_network_path_phase(
        context=_context(), module_runs=module_runs, targets=[ok_ip, bad_ip], options=NeoTraceOptions(),
        traceroute_collector=collector,
    )

    assert module_runs["neotrace"].status == ModuleStatus.PARTIAL
    assert result.degraded
    assert len(result.paths) == 1


def test_failed_when_all_targets_fail() -> None:
    module_runs = _module_runs()
    bad_ip = IPAddress.parse("1.1.1.2")
    collector = _FakeTracerouteCollector(errors={"1.1.1.2"})

    result = run_network_path_phase(
        context=_context(), module_runs=module_runs, targets=[bad_ip], options=NeoTraceOptions(),
        traceroute_collector=collector,
    )

    assert module_runs["neotrace"].status == ModuleStatus.FAILED
    assert result.degraded


def test_cancelled_mid_run_stops_remaining_targets() -> None:
    module_runs = _module_runs()
    token = CancellationToken()
    counter = iter(f"id-{n}" for n in range(1, 1000))
    context = PhaseContext(
        track_run_id=TrackRunId("run-1"),
        id_factory=counter.__next__,
        now=lambda: _NOW,
        event_publisher=_FakeEventPublisher(),
        cancellation_token=token,
    )

    class _CancellingCollector:
        def __init__(self) -> None:
            self.calls = 0

        def is_available(self) -> bool:
            return True

        def trace(self, target_ip: IPAddress, options: NeoTraceOptions) -> NetworkPath:
            self.calls += 1
            token.cancel()  # simule une annulation utilisateur pendant l'execution
            return _path(str(target_ip))

    collector = _CancellingCollector()
    result = run_network_path_phase(
        context=context,
        module_runs=module_runs,
        targets=[IPAddress.parse("1.1.1.1"), IPAddress.parse("1.1.1.2")],
        options=NeoTraceOptions(),
        traceroute_collector=collector,
    )

    assert collector.calls == 1
    assert module_runs["neotrace"].status == ModuleStatus.CANCELLED
    assert len(result.paths) == 1
