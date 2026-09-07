# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import subprocess

import pytest

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.domain.entities.track_profile import NeoTraceOptions
from omega_track.domain.value_objects.asn import Asn
from omega_track.domain.value_objects.geo_location import GeoLocation
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.infrastructure.collectors.network.subprocess_traceroute_collector import (
    SubprocessTracerouteCollector,
)

_IPV4_OUTPUT = """\
traceroute to example.com (93.184.216.34), 30 hops max, 60 byte packets
 1  gateway (192.168.1.1)  1.234 ms  1.111 ms  1.098 ms
 2  93.184.216.34 (93.184.216.34)  20.123 ms  19.876 ms  19.654 ms
"""


class _FakeGeoIpResolver:
    def __init__(self) -> None:
        self.locate_calls: list[IPAddress] = []

    def locate(self, ip: IPAddress) -> GeoLocation | None:
        self.locate_calls.append(ip)
        return GeoLocation(country="US", source="fake")

    def lookup_asn(self, ip: IPAddress) -> Asn | None:
        return Asn(number=15133)


class _FakeReverseDnsResolver:
    def __init__(self) -> None:
        self.calls: list[IPAddress] = []

    def resolve_ptr(self, ip: IPAddress) -> str | None:
        self.calls.append(ip)
        return "resolved.example.com"


def _completed(stdout: str, *, returncode: int = 0, stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def test_is_available_true_when_traceroute_binary_present() -> None:
    collector = SubprocessTracerouteCollector(
        geoip_resolver=_FakeGeoIpResolver(), which_fn=lambda name: "/usr/bin/traceroute" if name == "traceroute" else None
    )
    assert collector.is_available()


def test_is_available_false_when_no_binary_present() -> None:
    collector = SubprocessTracerouteCollector(geoip_resolver=_FakeGeoIpResolver(), which_fn=lambda name: None)
    assert not collector.is_available()


def test_trace_raises_when_no_binary_available() -> None:
    collector = SubprocessTracerouteCollector(geoip_resolver=_FakeGeoIpResolver(), which_fn=lambda name: None)
    with pytest.raises(CollectorUnavailableError):
        collector.trace(IPAddress.parse("93.184.216.34"), NeoTraceOptions())


def test_trace_enriches_public_hops_via_geoip_and_reverse_dns() -> None:
    geoip = _FakeGeoIpResolver()
    reverse_dns = _FakeReverseDnsResolver()
    collector = SubprocessTracerouteCollector(
        geoip_resolver=geoip,
        reverse_dns_resolver=reverse_dns,
        run_fn=lambda args, timeout: _completed(_IPV4_OUTPUT),
        which_fn=lambda name: "/usr/bin/traceroute" if name == "traceroute" else None,
    )

    path = collector.trace(IPAddress.parse("93.184.216.34"), NeoTraceOptions())

    assert path.reached_target
    assert len(path.hops) == 2
    # premier hop prive (192.168.1.1) : jamais enrichi (identifie localement, sans lookup externe)
    assert path.hops[0].geo is None
    assert path.hops[0].asn is None
    # gateway (192.168.1.1) est deja nomme par le parseur - jamais ecrase par le reverse DNS
    assert path.hops[0].hostname == "gateway"
    # second hop public (93.184.216.34) : enrichi via GeoIP/ASN
    assert path.hops[1].geo is not None and path.hops[1].geo.country == "US"
    assert path.hops[1].asn == Asn(number=15133)
    # ce hop public n'a pas de nom fourni par traceroute - complete par reverse DNS
    assert path.hops[1].hostname == "resolved.example.com"


def test_trace_never_calls_geoip_or_reverse_dns_for_private_hops() -> None:
    geoip = _FakeGeoIpResolver()
    reverse_dns = _FakeReverseDnsResolver()
    private_output = " 1  router (192.168.1.1)  1.0 ms\n"
    collector = SubprocessTracerouteCollector(
        geoip_resolver=geoip,
        reverse_dns_resolver=reverse_dns,
        run_fn=lambda args, timeout: _completed(private_output),
        which_fn=lambda name: "/usr/bin/traceroute" if name == "traceroute" else None,
    )
    path = collector.trace(IPAddress.parse("93.184.216.34"), NeoTraceOptions())
    assert path.hops[0].geo is None
    assert path.hops[0].asn is None
    assert geoip.locate_calls == []
    assert reverse_dns.calls == []


def test_trace_deduplicates_repeated_hop_ips() -> None:
    geoip = _FakeGeoIpResolver()
    repeated_output = (
        " 1  a (1.1.1.1)  1.0 ms\n"
        " 2  a (1.1.1.1)  1.0 ms\n"
    )
    collector = SubprocessTracerouteCollector(
        geoip_resolver=geoip,
        run_fn=lambda args, timeout: _completed(repeated_output),
        which_fn=lambda name: "/usr/bin/traceroute" if name == "traceroute" else None,
    )
    collector.trace(IPAddress.parse("1.1.1.1"), NeoTraceOptions())
    assert len(geoip.locate_calls) == 1


def test_trace_raises_collector_unavailable_when_subprocess_times_out() -> None:
    """Regression : `subprocess.run` sans `timeout=` pouvait bloquer
    indefiniment (un binaire ignorant son propre flag `-w`), empechant
    meme l'annulation cooperative de reprendre la main - bug reel signale
    par l'utilisateur (module neotrace reste bloque sur RUNNING)."""

    def run_fn(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        raise subprocess.TimeoutExpired(cmd=args, timeout=timeout)

    collector = SubprocessTracerouteCollector(
        geoip_resolver=_FakeGeoIpResolver(),
        run_fn=run_fn,
        which_fn=lambda name: "/usr/bin/traceroute" if name == "traceroute" else None,
    )
    with pytest.raises(CollectorUnavailableError):
        collector.trace(IPAddress.parse("93.184.216.34"), NeoTraceOptions())


def test_trace_passes_a_bounded_timeout_derived_from_options() -> None:
    seen_timeouts: list[float] = []

    def run_fn(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        seen_timeouts.append(timeout)
        return _completed("")

    collector = SubprocessTracerouteCollector(
        geoip_resolver=_FakeGeoIpResolver(),
        run_fn=run_fn,
        which_fn=lambda name: "/usr/bin/traceroute" if name == "traceroute" else None,
    )
    collector.trace(
        IPAddress.parse("93.184.216.34"),
        NeoTraceOptions(timeout_seconds=2.0, max_hops=10),
    )
    assert seen_timeouts == [2.0 * 10 + 5.0]


def test_trace_raises_collector_unavailable_on_permission_error() -> None:
    collector = SubprocessTracerouteCollector(
        geoip_resolver=_FakeGeoIpResolver(),
        run_fn=lambda args, timeout: _completed("", returncode=1, stderr="traceroute: socket: Operation not permitted"),
        which_fn=lambda name: "/usr/bin/traceroute" if name == "traceroute" else None,
    )
    with pytest.raises(CollectorUnavailableError):
        collector.trace(IPAddress.parse("93.184.216.34"), NeoTraceOptions())


def test_trace_uses_ipv6_binary_selection_for_ipv6_target() -> None:
    seen_args: list[list[str]] = []

    def run_fn(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        seen_args.append(args)
        return _completed(" 1  a (2001:db8::1)  1.0 ms\n")

    def which_fn(name: str) -> str | None:
        return "/usr/bin/traceroute" if name in ("traceroute",) else None

    collector = SubprocessTracerouteCollector(geoip_resolver=_FakeGeoIpResolver(), run_fn=run_fn, which_fn=which_fn)
    collector.trace(IPAddress.parse("2001:db8::2"), NeoTraceOptions())

    assert seen_args[0][0] == "traceroute"
    assert "-6" in seen_args[0]


def test_trace_prefers_traceroute6_binary_when_available() -> None:
    seen_args: list[list[str]] = []

    def run_fn(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        seen_args.append(args)
        return _completed(" 1  a (2001:db8::1)  1.0 ms\n")

    def which_fn(name: str) -> str | None:
        return "/usr/bin/traceroute6" if name == "traceroute6" else None

    collector = SubprocessTracerouteCollector(geoip_resolver=_FakeGeoIpResolver(), run_fn=run_fn, which_fn=which_fn)
    collector.trace(IPAddress.parse("2001:db8::2"), NeoTraceOptions())

    assert seen_args[0][0] == "traceroute6"
    assert "-6" not in seen_args[0]


def test_trace_passes_protocol_and_limit_flags() -> None:
    seen_args: list[list[str]] = []

    def run_fn(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        seen_args.append(args)
        return _completed("")

    collector = SubprocessTracerouteCollector(
        geoip_resolver=_FakeGeoIpResolver(),
        run_fn=run_fn,
        which_fn=lambda name: "/usr/bin/traceroute" if name == "traceroute" else None,
    )
    collector.trace(
        IPAddress.parse("93.184.216.34"),
        NeoTraceOptions(protocol="tcp", timeout_seconds=3.0, max_hops=15),
    )
    args = seen_args[0]
    assert "-T" in args
    assert "-w" in args and args[args.index("-w") + 1] == "3"
    assert "-m" in args and args[args.index("-m") + 1] == "15"
