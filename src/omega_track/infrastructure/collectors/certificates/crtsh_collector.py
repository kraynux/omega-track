# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de CertificateTransparencyCollector (Phase 10)
via l'API JSON publique de crt.sh (`?q=<domaine>&output=json`). Traite
comme une source a cle du point de vue de la robustesse malgre l'absence
de cle (docs/DATA_SOURCES.md : "aucun quota formellement publie... service
communautaire sans SLA") - seule une indisponibilite totale (reseau,
JSON invalide) leve CollectorUnavailableError, jamais un champ individuel
absent (meme discipline D-015 que RDAP).

`distinct_log_count` : l'API JSON de crt.sh ne donne pas explicitement un
identifiant de log CT par entree, mais stocke une ligne PAR (certificat,
log) observe - regrouper les entrees du certificat le plus recent
(meme `serial_number`) et compter les `id` distincts approxime donc
raisonnablement "combien de logs CT distincts ont observe ce
certificat". Heuristique documentee, a revalider avant la v1.0 si le
format de reponse de crt.sh change (meme prudence que docs/DATA_SOURCES.md
pour toute source tierce)."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

import httpx

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.certificate import CertificateFindingType
from omega_track.domain.entities.findings.dns import DnsFindingType
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.shared.i18n import _

SOURCE_NAME = "crt.sh"


class CrtShCollector:
    """Implemente ports/collectors/certificate_transparency_collector.py::
    CertificateTransparencyCollector."""

    def __init__(self, *, http_client: httpx.Client, now: Callable[[], datetime]) -> None:
        self._http_client = http_client
        self._now = now

    def collect_certificates(self, domain: DomainName) -> list[CollectedRecord]:
        entries = self._fetch(domain)
        if not entries:
            return []

        now = self._now()
        records: list[CollectedRecord] = []
        seen_serials: set[str] = set()
        seen_sans: set[str] = set()
        domain_text = str(domain)

        for entry in entries:
            serial = entry.get("serial_number")
            if serial and serial not in seen_serials:
                seen_serials.add(serial)
                records.append(
                    CollectedRecord(
                        finding_type=CertificateFindingType.CERTIFICATE_OBSERVED.value,
                        payload={
                            "serial_number": serial,
                            "issuer_name": entry.get("issuer_name"),
                            "not_before": entry.get("not_before"),
                            "not_after": entry.get("not_after"),
                        },
                        confidence=ConfidenceLevel.DECLARED,
                        source_name=SOURCE_NAME,
                        observed_at=now,
                    )
                )

            for name in _split_names(entry.get("name_value")):
                if name in seen_sans:
                    continue
                seen_sans.add(name)
                records.append(
                    CollectedRecord(
                        finding_type=CertificateFindingType.SUBJECT_ALTERNATIVE_NAME.value,
                        payload={"name": name, "certificate_serial": serial},
                        confidence=ConfidenceLevel.DECLARED,
                        source_name=SOURCE_NAME,
                        observed_at=now,
                    )
                )
                if name != domain_text and name.endswith(f".{domain_text}"):
                    records.append(
                        CollectedRecord(
                            finding_type=DnsFindingType.PASSIVE_SUBDOMAIN.value,
                            payload={"name": name},
                            confidence=ConfidenceLevel.DECLARED,
                            source_name=SOURCE_NAME,
                            observed_at=now,
                        )
                    )

        return records

    def distinct_log_count(self, domain: DomainName) -> int:
        entries = self._fetch(domain)
        if not entries:
            return 0
        latest = max(entries, key=lambda e: e.get("entry_timestamp") or "")
        serial = latest.get("serial_number")
        return len({e.get("id") for e in entries if e.get("serial_number") == serial})

    def _fetch(self, domain: DomainName) -> list[dict[str, Any]]:
        try:
            response = self._http_client.get("https://crt.sh/", params={"q": str(domain), "output": "json"})
        except httpx.HTTPError as exc:
            raise CollectorUnavailableError(SOURCE_NAME, str(exc)) from exc

        if response.status_code == 404:
            return []
        if response.status_code >= 400:
            raise CollectorUnavailableError(SOURCE_NAME, _("erreur HTTP ({status_code})").format(status_code=response.status_code))

        try:
            payload = response.json()
        except ValueError as exc:
            raise CollectorUnavailableError(SOURCE_NAME, _("réponse JSON invalide")) from exc

        if not isinstance(payload, list):
            raise CollectorUnavailableError(SOURCE_NAME, _("forme de réponse inattendue"))
        return payload


def _split_names(raw: str | None) -> list[str]:
    if not raw:
        return []
    return sorted({line.strip().lower() for line in raw.splitlines() if line.strip()})
