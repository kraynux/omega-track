# Copyright (c) 2026 kraynux - Licence MIT
"""Catalogue statique des plugins connus (plan de dev §10/§12) -
decouverte simple par dict plutot qu'un mecanisme d'enregistrement
dynamique : 5 entrees (CT/archives/BGP Phase 10, VirusTotal/HIBP
Phase 12), aucun besoin reel de plus tant que Phase 13 (organisation)
n'introduit pas davantage de plugins - un registre dynamique (entry
points, scan de paquets) serait une anticipation sans justification
actuelle."""
from __future__ import annotations

from omega_track.plugins.certificates.ct_plugin import DESCRIPTOR as CT_DESCRIPTOR
from omega_track.plugins.descriptor import PluginDescriptor
from omega_track.plugins.history.archive_plugin import DESCRIPTOR as ARCHIVE_DESCRIPTOR
from omega_track.plugins.network.asn_enrichment_plugin import DESCRIPTOR as BGP_DESCRIPTOR
from omega_track.plugins.reputation.hibp_plugin import DESCRIPTOR as HIBP_DESCRIPTOR
from omega_track.plugins.reputation.virustotal_plugin import DESCRIPTOR as VIRUSTOTAL_DESCRIPTOR

PLUGIN_DESCRIPTORS: dict[str, PluginDescriptor] = {
    CT_DESCRIPTOR.name: CT_DESCRIPTOR,
    ARCHIVE_DESCRIPTOR.name: ARCHIVE_DESCRIPTOR,
    BGP_DESCRIPTOR.name: BGP_DESCRIPTOR,
    VIRUSTOTAL_DESCRIPTOR.name: VIRUSTOTAL_DESCRIPTOR,
    HIBP_DESCRIPTOR.name: HIBP_DESCRIPTOR,
}


def get_plugin_descriptor(name: str) -> PluginDescriptor | None:
    return PLUGIN_DESCRIPTORS.get(name)
