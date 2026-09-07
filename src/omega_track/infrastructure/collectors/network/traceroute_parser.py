# Copyright (c) 2026 kraynux - Licence MIT
"""Parseur de sortie traceroute/tracepath classique Linux (Phase 6) -
pur, aucune dependance reseau. Deux fonctions publiques separees pour
IPv4/IPv6 (D-016, angle mort 7) : meme format texte, mais jamais suppose
interchangeable au niveau de l'API/des fixtures de test - seul
`_parse_hops` est partage en interne.

Format attendu par ligne de hop :
`  1  gateway (192.168.1.1)  1.234 ms  1.111 ms  1.098 ms`
ou, pour un hop non repondant : `  1  * * *`."""
from __future__ import annotations

import re

from omega_track.domain.entities.findings.path import NetworkHop
from omega_track.domain.value_objects.ip_address import IPAddress

_HOP_LINE_RE = re.compile(r"^\s*(\d+)\s+(.*)$")
_HOST_IP_RE = re.compile(r"(\S+)\s+\(([0-9a-fA-F:.]+)\)")
_RTT_RE = re.compile(r"([\d.]+)\s*ms")


def parse_traceroute_ipv4(output: str) -> list[NetworkHop]:
    return _parse_hops(output)


def parse_traceroute_ipv6(output: str) -> list[NetworkHop]:
    return _parse_hops(output)


def _parse_hops(output: str) -> list[NetworkHop]:
    hops: list[NetworkHop] = []
    for line in output.splitlines():
        match = _HOP_LINE_RE.match(line)
        if match is None:
            continue
        sequence = int(match.group(1))
        rest = match.group(2).strip()

        if not rest or set(rest.replace(" ", "")) <= {"*"}:
            hops.append(NetworkHop(sequence=sequence, ip=None))
            continue

        host_ip_match = _HOST_IP_RE.search(rest)
        if host_ip_match is None:
            hops.append(NetworkHop(sequence=sequence, ip=None))
            continue

        hostname_token, ip_text = host_ip_match.groups()
        ip = IPAddress.parse(ip_text)
        hostname = None if hostname_token == ip_text else hostname_token

        rtt_match = _RTT_RE.search(rest)
        rtt_ms = float(rtt_match.group(1)) if rtt_match else None

        hops.append(NetworkHop(sequence=sequence, ip=ip, hostname=hostname, rtt_ms=rtt_ms))
    return hops
