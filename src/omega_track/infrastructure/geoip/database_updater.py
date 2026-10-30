# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation concrete de DatabaseUpdater (Phase 5) : telecharge la
derniere base d'un fournisseur, verifie son integrite, puis remplace
l'ancienne atomiquement en gardant une sauvegarde courte (plan de dev §5
"Regles d'update") - jamais d'ecriture destructive avant validation.

URLs et formats d'archive verifies a l'ecriture de ce module (2026-09) -
comme docs/DATA_SOURCES.md le rappelle pour toute source tierce, ces
details (schema de distribution DB-IP/MaxMind) peuvent changer et doivent
etre revalides avant la v1.0."""
from __future__ import annotations

import gzip
import os
import shutil
import tarfile
from collections.abc import Callable
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Literal

import httpx

from omega_track.application.exceptions import GeoIpDownloadError, MaxMindCredentialsMissingError
from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus
from omega_track.infrastructure.geoip.database_integrity import compute_checksum, validate_mmdb
from omega_track.ports.services.secret_store import SecretStore
from omega_track.shared.i18n import _

_MAXMIND_LICENSE_KEY_NAME = "maxmind_license_key"

ArchiveFormat = Literal["gzip", "tar_gz"]

_EDITIONS: dict[str, str] = {
    "dbip": "City Lite",
    "maxmind": "GeoLite2-City",
}


class HttpDatabaseUpdater:
    """Implemente ports/services/database_updater.py::DatabaseUpdater."""

    def __init__(
        self,
        *,
        http_client: httpx.Client,
        secret_store: SecretStore,
        now: Callable[[], datetime],
        validate: Callable[[Path], bool] = validate_mmdb,
    ) -> None:
        self._http_client = http_client
        self._secret_store = secret_store
        self._now = now
        self._validate = validate

    def download_latest(self, provider: str, destination: Path) -> GeoIpDatabaseStatus:
        url, archive_format = self._build_request(provider)
        try:
            response = self._http_client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise GeoIpDownloadError(_("échec de téléchargement pour {provider!r}").format(provider=provider)) from exc

        try:
            raw_mmdb = _extract_mmdb_bytes(response.content, archive_format)
        except (OSError, tarfile.TarError) as exc:
            raise GeoIpDownloadError(_("archive invalide pour {provider!r}").format(provider=provider)) from exc

        destination.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = destination.with_suffix(destination.suffix + ".tmp")
        tmp_path.write_bytes(raw_mmdb)

        if not self._validate(tmp_path):
            tmp_path.unlink(missing_ok=True)
            raise GeoIpDownloadError(_("base téléchargée invalide pour {provider!r}").format(provider=provider))

        checksum = compute_checksum(tmp_path)
        if destination.exists():
            backup_path = destination.with_suffix(destination.suffix + ".bak")
            shutil.copy2(destination, backup_path)
        os.replace(tmp_path, destination)

        return GeoIpDatabaseStatus(
            provider=provider,
            edition=_EDITIONS.get(provider, provider),
            local_path=str(destination),
            checksum=checksum,
            downloaded_at=self._now(),
            published_at=None,
            status="ok",
        )

    def _build_request(self, provider: str) -> tuple[str, ArchiveFormat]:
        if provider == "dbip":
            month = self._now().strftime("%Y-%m")
            return f"https://download.db-ip.com/free/dbip-city-lite-{month}.mmdb.gz", "gzip"
        if provider == "maxmind":
            license_key = self._secret_store.get_secret(_MAXMIND_LICENSE_KEY_NAME)
            if not license_key:
                raise MaxMindCredentialsMissingError()
            url = (
                "https://download.maxmind.com/app/geoip_download"
                f"?edition_id=GeoLite2-City&license_key={license_key}&suffix=tar.gz"
            )
            return url, "tar_gz"
        raise GeoIpDownloadError(_("fournisseur GeoIP inconnu : {provider!r}").format(provider=provider))


def _extract_mmdb_bytes(raw: bytes, archive_format: ArchiveFormat) -> bytes:
    if archive_format == "gzip":
        return gzip.decompress(raw)
    with tarfile.open(fileobj=BytesIO(raw), mode="r:gz") as archive:
        member = next((m for m in archive.getmembers() if m.name.endswith(".mmdb")), None)
        if member is None:
            raise GeoIpDownloadError(_("aucun fichier .mmdb trouvé dans l'archive"))
        extracted = archive.extractfile(member)
        if extracted is None:
            raise GeoIpDownloadError(_("membre .mmdb illisible dans l'archive"))
        return extracted.read()
