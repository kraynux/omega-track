# Copyright (c) 2026 kraynux - Licence MIT
"""Lecture MMDB partagee entre DB-IP et MaxMind (Phase 5) : les deux
fournisseurs distribuent ce meme format binaire, seul le fichier/URL
differe (voir dbip_resolver.py/maxmind_resolver.py). `MmdbReader` prend un
`opener` injectable pour permettre des tests sans fichier .mmdb reel,
meme convention que clock/id_factory (app/container.py)."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any, Protocol

import maxminddb

from omega_track.domain.value_objects.asn import Asn
from omega_track.domain.value_objects.geo_location import GeoLocation
from omega_track.domain.value_objects.ip_address import IPAddress


class MmdbDatabase(Protocol):
    def get(self, ip: str) -> Any | None: ...

    def close(self) -> None: ...


class MmdbReader:
    """Enveloppe paresseuse (ouverture au premier lookup, pas au
    constructeur) autour d'une base MMDB. Base absente/invalide -> aucune
    geolocalisation plutot qu'une erreur (docs/DATA_SOURCES.md : "le
    tracker continue sans geolocalisation si la base est absente/perimee"
    - jamais implemente jusqu'ici, bug reel signale par l'utilisateur :
    un TrackRun plantait avec `FileNotFoundError` des qu'aucune base
    GeoIP n'avait encore ete telechargee)."""

    def __init__(
        self,
        path: Path,
        *,
        opener: Callable[[Path], MmdbDatabase] = maxminddb.open_database,
    ) -> None:
        self._path = path
        self._opener = opener
        self._db: MmdbDatabase | None = None
        self._unavailable = False

    def lookup(self, ip: str) -> dict[str, Any] | None:
        if self._unavailable:
            return None
        if self._db is None:
            try:
                self._db = self._opener(self._path)
            except (OSError, ValueError, maxminddb.InvalidDatabaseError):
                self._unavailable = True
                return None
        record = self._db.get(ip)
        return dict(record) if record is not None else None

    def close(self) -> None:
        if self._db is not None:
            self._db.close()
            self._db = None


def parse_geo_record(raw: dict[str, Any], *, source: str) -> GeoLocation:
    """Schema commun DB-IP/MaxMind (DB-IP est volontairement compatible
    avec le schema MaxMind pour permettre un remplacement direct)."""
    country = raw.get("country") or {}
    city = raw.get("city") or {}
    location = raw.get("location") or {}
    subdivisions = raw.get("subdivisions") or []
    region = (subdivisions[0].get("names") or {}).get("en") if subdivisions else None
    city_name = (city.get("names") or {}).get("en")
    country_code = country.get("iso_code")

    precision: str | None
    if city_name:
        precision = "city"
    elif region:
        precision = "region"
    elif country_code:
        precision = "country"
    else:
        precision = None

    return GeoLocation(
        country=country_code,
        region=region,
        city=city_name,
        latitude=location.get("latitude"),
        longitude=location.get("longitude"),
        timezone=location.get("time_zone"),
        precision=precision,
        source=source,
    )


def parse_asn_record(raw: dict[str, Any] | None) -> Asn | None:
    """Renvoie None si le fichier charge ne porte pas les champs ASN -
    les bases gratuites City-only n'en fournissent pas toujours, ce n'est
    jamais une erreur (voir MmdbGeoIpResolver)."""
    if raw is None:
        return None
    number = raw.get("autonomous_system_number")
    if number is None:
        return None
    return Asn(number=int(number), organization=raw.get("autonomous_system_organization"))


class MmdbGeoIpResolver:
    """Implemente ports/services/geoip_resolver.py::GeoIpResolver au
    dessus d'un seul MmdbReader par fournisseur - une base Lite gratuite
    (DB-IP ou MaxMind) ne separe pas toujours geo et ASN dans un fichier
    distinct (plan de dev §5) ; lookup_asn renvoie simplement None quand
    le champ est absent, jamais une erreur (memes garanties de tolerance
    aux champs manquants que D-015 pour RDAP)."""

    def __init__(self, reader: MmdbReader, *, source: str) -> None:
        self._reader = reader
        self._source = source

    @property
    def source(self) -> str:
        return self._source

    def locate(self, ip: IPAddress) -> GeoLocation | None:
        if not ip.is_public:
            return None
        raw = self._reader.lookup(str(ip))
        if raw is None:
            return None
        return parse_geo_record(raw, source=self._source)

    def lookup_asn(self, ip: IPAddress) -> Asn | None:
        if not ip.is_public:
            return None
        raw = self._reader.lookup(str(ip))
        return parse_asn_record(raw)
