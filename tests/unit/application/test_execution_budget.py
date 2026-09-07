# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_track.application.policies.execution_budget import (
    allocate_enrichment_budget,
    select_neotrace_targets,
)
from omega_track.domain.entities.track_profile import ExecutionLimits
from omega_track.domain.value_objects.ip_address import IPAddress

_LIMITS = ExecutionLimits(max_ipv4_enriched=5, max_ipv6_enriched=5, max_neotrace_ips=3)


def _ips(*addresses: str) -> list[IPAddress]:
    return [IPAddress.parse(a) for a in addresses]


def test_within_budget_everything_is_enriched() -> None:
    ips = _ips("1.1.1.1", "1.1.1.2", "2606:4700:4700::1111")
    budget = allocate_enrichment_budget(ips, limits=_LIMITS)
    assert budget.enriched == ips
    assert budget.excess == []


def test_excess_ipv4_beyond_budget_is_not_enriched() -> None:
    ips = _ips("1.1.1.1", "1.1.1.2", "1.1.1.3", "1.1.1.4", "1.1.1.5", "1.1.1.6", "1.1.1.7")
    budget = allocate_enrichment_budget(ips, limits=_LIMITS)
    assert len(budget.enriched) == 5
    assert budget.excess == ips[5:]


def test_ipv4_and_ipv6_budgets_are_independent() -> None:
    ipv4 = _ips("1.1.1.1", "1.1.1.2", "1.1.1.3", "1.1.1.4", "1.1.1.5", "1.1.1.6")
    ipv6 = _ips("2606:4700:4700::1111", "2606:4700:4700::1001")
    budget = allocate_enrichment_budget(ipv4 + ipv6, limits=_LIMITS)
    assert len(budget.enriched) == 5 + 2
    assert budget.excess == [ipv4[5]]


def test_neotrace_targets_are_capped_and_drawn_from_enriched_only() -> None:
    ips = _ips("1.1.1.1", "1.1.1.2", "1.1.1.3", "1.1.1.4", "1.1.1.5", "1.1.1.6")
    budget = allocate_enrichment_budget(ips, limits=_LIMITS)
    targets = select_neotrace_targets(budget, limits=_LIMITS)
    assert targets == ips[:3]
    assert all(target in budget.enriched for target in targets)
