# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import gzip
import tarfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import httpx
import pytest

from omega_track.application.exceptions import GeoIpDownloadError, MaxMindCredentialsMissingError
from omega_track.infrastructure.geoip.database_updater import HttpDatabaseUpdater

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeSecretStore:
    def __init__(self, license_key: str | None = None) -> None:
        self._key = license_key

    def get_secret(self, key: str) -> str | None:
        return self._key if key == "maxmind_license_key" else None

    def set_secret(self, key: str, value: str) -> None:  # pragma: no cover - non exerce ici
        raise NotImplementedError

    def delete_secret(self, key: str) -> None:  # pragma: no cover - non exerce ici
        raise NotImplementedError


def _tar_gz_archive(member_name: str, content: bytes) -> bytes:
    buffer = BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        info = tarfile.TarInfo(name=member_name)
        info.size = len(content)
        archive.addfile(info, BytesIO(content))
    return buffer.getvalue()


def test_dbip_download_extracts_gzip_and_replaces_destination_atomically(tmp_path: Path) -> None:
    destination = tmp_path / "dbip-city.mmdb"
    destination.write_bytes(b"ancienne-version")
    payload = gzip.compress(b"nouvelle-version-mmdb")

    def handler(request: httpx.Request) -> httpx.Response:
        assert "dbip-city-lite-2026-09.mmdb.gz" in str(request.url)
        return httpx.Response(200, content=payload)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    updater = HttpDatabaseUpdater(
        http_client=client, secret_store=_FakeSecretStore(), now=lambda: _NOW, validate=lambda _path: True
    )

    status = updater.download_latest("dbip", destination)

    assert status.status == "ok"
    assert status.provider == "dbip"
    assert status.edition == "City Lite"
    assert destination.read_bytes() == b"nouvelle-version-mmdb"
    assert destination.with_suffix(destination.suffix + ".bak").read_bytes() == b"ancienne-version"
    assert not destination.with_suffix(destination.suffix + ".tmp").exists()


def test_maxmind_download_extracts_tar_gz(tmp_path: Path) -> None:
    destination = tmp_path / "maxmind-city.mmdb"
    payload = _tar_gz_archive("GeoLite2-City_20260901/GeoLite2-City.mmdb", b"contenu-maxmind")

    def handler(request: httpx.Request) -> httpx.Response:
        assert "license_key=secret-key" in str(request.url)
        return httpx.Response(200, content=payload)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    updater = HttpDatabaseUpdater(
        http_client=client,
        secret_store=_FakeSecretStore("secret-key"),
        now=lambda: _NOW,
        validate=lambda _path: True,
    )

    status = updater.download_latest("maxmind", destination)

    assert status.status == "ok"
    assert destination.read_bytes() == b"contenu-maxmind"


def test_maxmind_download_without_key_raises_credentials_error(tmp_path: Path) -> None:
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200)))
    updater = HttpDatabaseUpdater(http_client=client, secret_store=_FakeSecretStore(None), now=lambda: _NOW)

    with pytest.raises(MaxMindCredentialsMissingError):
        updater.download_latest("maxmind", tmp_path / "x.mmdb")


def test_http_failure_raises_geoip_download_error_without_touching_destination(tmp_path: Path) -> None:
    destination = tmp_path / "dbip-city.mmdb"
    destination.write_bytes(b"intact")

    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(503)))
    updater = HttpDatabaseUpdater(http_client=client, secret_store=_FakeSecretStore(), now=lambda: _NOW)

    with pytest.raises(GeoIpDownloadError):
        updater.download_latest("dbip", destination)

    assert destination.read_bytes() == b"intact"


def test_invalid_downloaded_file_raises_and_leaves_destination_untouched(tmp_path: Path) -> None:
    destination = tmp_path / "dbip-city.mmdb"
    destination.write_bytes(b"intact")
    payload = gzip.compress(b"contenu-invalide")

    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, content=payload)))
    updater = HttpDatabaseUpdater(
        http_client=client, secret_store=_FakeSecretStore(), now=lambda: _NOW, validate=lambda _path: False
    )

    with pytest.raises(GeoIpDownloadError):
        updater.download_latest("dbip", destination)

    assert destination.read_bytes() == b"intact"
    assert not destination.with_suffix(destination.suffix + ".tmp").exists()
