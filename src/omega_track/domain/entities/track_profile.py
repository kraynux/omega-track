# Copyright (c) 2026 kraynux - Licence MIT
"""Profil de track : modules actives, options NeoTrace, limites,
politique reseau et sources autorisees (plan de dev §4.1)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from omega_track.domain.exceptions.profile import UnknownModuleError
from omega_track.domain.value_objects.identifiers import TrackProfileId
from omega_track.shared.i18n import _

KNOWN_MODULES: frozenset[str] = frozenset({
    "dns",
    "reverse_dns",
    "rdap",
    "neotrace",
    "certificate_transparency",
    "archives",
    "bgp",
    "reputation_free",
    "virustotal",
    "hibp",
    "organization",
})
"""Registre des modules valides - un profil qui reference un nom hors de
cette liste leve UnknownModuleError, jamais accepte silencieusement.

"reputation_keyed" (Phase 2) remplace par "virustotal"/"hibp" (Phase 12) :
deux sources independantes, chacune avec sa propre cle/son propre quota/
son propre statut - les regrouper sous un seul module aurait rendu le
statut d'un ModuleRun ambigu ("PARTIAL" ne dirait pas laquelle des deux a
echoue), alors que le patron plugin etabli en Phase 10 (CT/archives/BGP)
associe deja strictement 1 module = 1 source = 1 statut."""

_MVP_MODULES: frozenset[str] = frozenset({"dns", "reverse_dns", "rdap", "neotrace"})
"""Modules disponibles des la Phase 6 (MVP), sans cle ni source a clé -
les autres arrivent en Phase 10 (gratuits) et Phase 12 (a cle)."""


@dataclass(frozen=True, slots=True)
class NeoTraceOptions:
    protocol: str = "icmp"
    """icmp/udp/tcp - valeurs compatibles par plateforme (Phase 6)."""
    timeout_seconds: float = 2.0
    max_hops: int = 30
    enable_reverse_dns: bool = True
    enable_mtr: bool = False
    """Extension opt-in (Phase 6) - jamais active par defaut."""


@dataclass(frozen=True, slots=True)
class ExecutionLimits:
    """Budget d'enrichissement par defaut (D-012, angle mort 3) - evite
    l'explosion de findings sur un domaine CDN/anycast. Les deux budgets
    de temps (Phase 7 §7 "Definir les budgets") sont cooperatifs, pas
    preemptifs : `global_timeout_seconds` est verifie par
    TrackOrchestrator entre deux phases/modules (jamais au milieu d'un
    appel de collecteur deja en cours) ; `module_timeout_seconds` est
    seulement transmis aux collecteurs qui exposent deja leur propre
    mecanisme de timeout par requete (ex. HttpRdapCollector), jamais
    impose de force par un deuxieme mecanisme independant."""

    max_ipv4_enriched: int = 5
    max_ipv6_enriched: int = 5
    max_neotrace_ips: int = 3
    global_timeout_seconds: float = 120.0
    module_timeout_seconds: float = 30.0


@dataclass
class TrackProfile:
    id: TrackProfileId
    name: str
    modules: set[str]
    created_at: datetime
    updated_at: datetime
    is_default: bool = False
    neotrace: NeoTraceOptions = field(default_factory=NeoTraceOptions)
    limits: ExecutionLimits = field(default_factory=ExecutionLimits)

    def __post_init__(self) -> None:
        unknown = self.modules - KNOWN_MODULES
        if unknown:
            raise UnknownModuleError(_("module(s) inconnu(s) : {value}").format(value=sorted(unknown)))

    def enabled_mvp_modules(self) -> set[str]:
        return self.modules & _MVP_MODULES

    def enabled_extended_modules(self) -> set[str]:
        return self.modules - _MVP_MODULES
