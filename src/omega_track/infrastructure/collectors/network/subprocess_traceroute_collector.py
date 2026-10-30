# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de TracerouteCollector (Phase 6, plan de dev
"NeoTrace MVP") - adapte `traceroute`/`tracepath` selon disponibilite et
version IP (D-016 : binaire/flags reellement differents en IPv6, jamais
la meme commande simplement filtree). `is_available()`/la selection de
binaire constituent la detection de capacites au bootstrap ; l'absence de
binaire ou une erreur de permission a l'execution levent
CollectorUnavailableError - "etat degrade traceroute indisponible",
jamais confondu avec un hop non repondant (`NetworkHop(ip=None)`, produit
uniquement par le parseur sur une sortie reellement obtenue).

`run_fn`/`which_fn` injectables (meme convention que le reste du projet) :
les tests ne lancent jamais de vrai sous-processus."""
from __future__ import annotations

import shutil
import subprocess
from collections.abc import Callable
from dataclasses import replace

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.domain.entities.findings.path import NetworkHop, NetworkPath
from omega_track.domain.entities.track_profile import NeoTraceOptions
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.infrastructure.collectors.network.traceroute_parser import (
    parse_traceroute_ipv4,
    parse_traceroute_ipv6,
)
from omega_track.ports.services.geoip_resolver import GeoIpResolver
from omega_track.ports.services.reverse_dns_resolver import ReverseDnsResolver
from omega_track.shared.i18n import _

RunFn = Callable[[list[str], float], "subprocess.CompletedProcess[str]"]
WhichFn = Callable[[str], str | None]

_PERMISSION_MARKERS = ("operation not permitted", "permission denied")


_TIMEOUT_MARGIN_SECONDS = 5.0
"""Marge ajoutee au budget theorique (timeout_seconds * max_hops) avant
de considerer le sous-processus lui-meme bloque - un binaire qui ignore
son propre flag `-w` (ou une resolution DNS interne lente sur certains
systemes) peut sinon bloquer `subprocess.run` indefiniment, ce qu'aucun
timeout Python ne bornait jusqu'ici (bug reel signale par l'utilisateur :
le module neotrace restait bloque sur RUNNING sans jamais se terminer,
et l'annulation cooperative - verifiee seulement ENTRE deux appels de
collecteur, cancellation.py - ne peut rien faire tant que cet appel
unique ne rend jamais la main)."""


def _default_run(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, check=False, timeout=timeout)


class SubprocessTracerouteCollector:
    """Implemente ports/collectors/traceroute_collector.py::TracerouteCollector."""

    def __init__(
        self,
        *,
        geoip_resolver: GeoIpResolver,
        reverse_dns_resolver: ReverseDnsResolver | None = None,
        run_fn: RunFn = _default_run,
        which_fn: WhichFn = shutil.which,
    ) -> None:
        self._geoip_resolver = geoip_resolver
        self._reverse_dns_resolver = reverse_dns_resolver
        self._run_fn = run_fn
        self._which_fn = which_fn

    def is_available(self) -> bool:
        return self._select_binary(4) is not None

    def trace(self, target_ip: IPAddress, options: NeoTraceOptions) -> NetworkPath:
        selection = self._select_binary(target_ip.version)
        if selection is None:
            raise CollectorUnavailableError("traceroute", _("aucun binaire disponible"))
        binary, extra_flags = selection

        args = [binary, *_protocol_flags(options.protocol), *extra_flags]
        args += ["-w", str(int(options.timeout_seconds)), "-m", str(options.max_hops), str(target_ip)]
        timeout = options.timeout_seconds * options.max_hops + _TIMEOUT_MARGIN_SECONDS

        try:
            result = self._run_fn(args, timeout)
        except subprocess.TimeoutExpired as exc:
            raise CollectorUnavailableError("traceroute", _("délai dépassé ({timeout:.0f}s)").format(timeout=timeout)) from exc
        except OSError as exc:
            raise CollectorUnavailableError("traceroute", str(exc)) from exc

        if result.returncode != 0 and _looks_like_permission_error(result.stderr):
            raise CollectorUnavailableError("traceroute", _("permissions insuffisantes"))

        parser = parse_traceroute_ipv6 if target_ip.version == 6 else parse_traceroute_ipv4
        hops = parser(result.stdout)
        enriched_hops = self._enrich_hops(hops, enable_reverse_dns=options.enable_reverse_dns)
        return NetworkPath(target_ip=target_ip, protocol=options.protocol, hops=enriched_hops)

    def _select_binary(self, ip_version: int) -> tuple[str, list[str]] | None:
        if ip_version == 6:
            if self._which_fn("traceroute6"):
                return "traceroute6", []
            if self._which_fn("traceroute"):
                return "traceroute", ["-6"]
            if self._which_fn("tracepath6"):
                return "tracepath6", []
            if self._which_fn("tracepath"):
                return "tracepath", ["-6"]
            return None
        if self._which_fn("traceroute"):
            return "traceroute", []
        if self._which_fn("tracepath"):
            return "tracepath", []
        return None

    def _enrich_hops(self, hops: list[NetworkHop], *, enable_reverse_dns: bool) -> list[NetworkHop]:
        cache: dict[IPAddress, NetworkHop] = {}
        enriched: list[NetworkHop] = []
        for hop in hops:
            if hop.ip is None:
                enriched.append(hop)
                continue
            if hop.ip not in cache:
                geo = self._geoip_resolver.locate(hop.ip) if hop.ip.is_public else None
                asn = self._geoip_resolver.lookup_asn(hop.ip) if hop.ip.is_public else None
                hostname = hop.hostname
                if (
                    hostname is None
                    and hop.ip.is_public
                    and enable_reverse_dns
                    and self._reverse_dns_resolver is not None
                ):
                    hostname = self._reverse_dns_resolver.resolve_ptr(hop.ip)
                cache[hop.ip] = replace(hop, geo=geo, asn=asn, hostname=hostname)
            cached = cache[hop.ip]
            enriched.append(replace(hop, geo=cached.geo, asn=cached.asn, hostname=cached.hostname))
        return enriched


def _protocol_flags(protocol: str) -> list[str]:
    if protocol == "icmp":
        return ["-I"]
    if protocol == "tcp":
        return ["-T"]
    return []


def _looks_like_permission_error(stderr: str) -> bool:
    lowered = stderr.lower()
    return any(marker in lowered for marker in _PERMISSION_MARKERS)
