# Copyright (c) 2026 kraynux - Licence MIT
"""Budget d'enrichissement multi-IP/CDN (D-012, angle mort 3, plan de dev
§6 etape 3) - pure : decide quelles IPs recoivent un enrichissement complet
(RDAP+GeoIP) et lesquelles restent un finding brut non enrichi, avant
meme de savoir COMMENT l'enrichissement sera fait (aucun port ici)."""
from __future__ import annotations

from dataclasses import dataclass

from omega_track.domain.entities.track_profile import ExecutionLimits
from omega_track.domain.value_objects.ip_address import IPAddress


@dataclass(frozen=True, slots=True)
class EnrichmentBudget:
    enriched: list[IPAddress]
    """IPv4 puis IPv6, dans la limite de `limits.max_ipv4_enriched`/
    `max_ipv6_enriched` - candidates a RDAP+GeoIP."""
    excess: list[IPAddress]
    """Au-dela du budget : restent des findings bruts non enrichis
    (network.ip_observed), jamais silencieusement ignorees."""


def allocate_enrichment_budget(ips: list[IPAddress], *, limits: ExecutionLimits) -> EnrichmentBudget:
    ipv4 = [ip for ip in ips if ip.version == 4]
    ipv6 = [ip for ip in ips if ip.version == 6]
    enriched = ipv4[: limits.max_ipv4_enriched] + ipv6[: limits.max_ipv6_enriched]
    excess = ipv4[limits.max_ipv4_enriched :] + ipv6[limits.max_ipv6_enriched :]
    return EnrichmentBudget(enriched=enriched, excess=excess)


def select_neotrace_targets(budget: EnrichmentBudget, *, limits: ExecutionLimits) -> list[IPAddress]:
    """IPs effectivement ciblees par NeoTrace - bornees a
    `limits.max_neotrace_ips` parmi les IPs deja retenues pour
    l'enrichissement complet (jamais une IP en exces du budget)."""
    return budget.enriched[: limits.max_neotrace_ips]
