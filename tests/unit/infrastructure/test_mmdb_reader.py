# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from pathlib import Path
from typing import Any

from omega_track.domain.value_objects.asn import Asn
from omega_track.domain.value_objects.geo_location import GeoLocation
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.infrastructure.geoip.mmdb_reader import (
    MmdbGeoIpResolver,
    MmdbReader,
    parse_asn_record,
    parse_geo_record,
)

_PUBLIC_IP = IPAddress.parse("1.1.1.1")
_PRIVATE_IP = IPAddress.parse("192.168.1.1")


class _FakeMmdbDatabase:
    def __init__(self, records: dict[str, dict[str, Any]]) -> None:
        self._records = records
        self.closed = False

    def get(self, ip: str) -> dict[str, Any] | None:
        return self._records.get(ip)

    def close(self) -> None:
        self.closed = True


def _reader(records: dict[str, dict[str, Any]]) -> MmdbReader:
    db = _FakeMmdbDatabase(records)
    return MmdbReader(Path("/unused.mmdb"), opener=lambda _path: db)


def test_reader_returns_none_for_unknown_ip() -> None:
    reader = _reader({})
    assert reader.lookup("1.1.1.1") is None


def test_reader_opens_lazily_and_reuses_the_same_database() -> None:
    opened: list[Path] = []

    def opener(path: Path) -> _FakeMmdbDatabase:
        opened.append(path)
        return _FakeMmdbDatabase({"1.1.1.1": {"country": {"iso_code": "AU"}}})

    reader = MmdbReader(Path("/some.mmdb"), opener=opener)
    reader.lookup("1.1.1.1")
    reader.lookup("1.1.1.1")
    assert opened == [Path("/some.mmdb")]


def test_parse_geo_record_prefers_city_precision() -> None:
    raw = {
        "country": {"iso_code": "FR"},
        "city": {"names": {"en": "Paris"}},
        "subdivisions": [{"names": {"en": "Ile-de-France"}}],
        "location": {"latitude": 48.85, "longitude": 2.35, "time_zone": "Europe/Paris"},
    }
    geo = parse_geo_record(raw, source="dbip")
    assert geo == GeoLocation(
        country="FR",
        region="Ile-de-France",
        city="Paris",
        latitude=48.85,
        longitude=2.35,
        timezone="Europe/Paris",
        precision="city",
        source="dbip",
    )


def test_parse_geo_record_falls_back_to_country_precision() -> None:
    geo = parse_geo_record({"country": {"iso_code": "FR"}}, source="dbip")
    assert geo.precision == "country"
    assert geo.city is None


def test_parse_asn_record_returns_none_when_absent() -> None:
    assert parse_asn_record(None) is None
    assert parse_asn_record({}) is None


def test_parse_asn_record_builds_asn() -> None:
    asn = parse_asn_record({"autonomous_system_number": 13335, "autonomous_system_organization": "Cloudflare"})
    assert asn == Asn(number=13335, organization="Cloudflare")


def test_resolver_never_looks_up_private_ips() -> None:
    reader = _reader({"192.168.1.1": {"country": {"iso_code": "FR"}}})
    resolver = MmdbGeoIpResolver(reader, source="dbip")
    assert resolver.locate(_PRIVATE_IP) is None
    assert resolver.lookup_asn(_PRIVATE_IP) is None


def test_resolver_locates_public_ip() -> None:
    reader = _reader({"1.1.1.1": {"country": {"iso_code": "AU"}}})
    resolver = MmdbGeoIpResolver(reader, source="dbip")
    location = resolver.locate(_PUBLIC_IP)
    assert location is not None
    assert location.country == "AU"
    assert location.source == "dbip"


def test_resolver_lookup_asn_returns_none_when_file_has_no_asn_fields() -> None:
    reader = _reader({"1.1.1.1": {"country": {"iso_code": "AU"}}})
    resolver = MmdbGeoIpResolver(reader, source="dbip")
    assert resolver.lookup_asn(_PUBLIC_IP) is None


def test_resolver_lookup_asn_returns_asn_when_present() -> None:
    reader = _reader({"1.1.1.1": {"autonomous_system_number": 13335, "autonomous_system_organization": "Cloudflare"}})
    resolver = MmdbGeoIpResolver(reader, source="maxmind")
    asn = resolver.lookup_asn(_PUBLIC_IP)
    assert asn == Asn(number=13335, organization="Cloudflare")
