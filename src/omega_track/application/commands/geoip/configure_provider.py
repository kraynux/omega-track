# Copyright (c) 2026 kraynux - Licence MIT
"""Use cases SelectGeoIpProvider/ConfigureMaxMindCredentials/
ValidateGeoIpConfiguration (plan de dev §5) - regroupes dans un seul
fichier (ARBORESCENCE.md ne prevoit qu'un configure_provider.py pour ces
3 cas d'usage, tous de tres petite taille et etroitement lies : choisir
le fournisseur, y attacher une cle, puis verifier que la configuration
resultante est utilisable)."""
from __future__ import annotations

from dataclasses import dataclass

from omega_track.application.exceptions import (
    MaxMindCredentialsMissingError,
    UnknownGeoIpProviderError,
)
from omega_track.application.policies.provider_selection import (
    VALID_GEOIP_PROVIDERS,
    resolve_active_geoip_provider,
)
from omega_track.ports.repositories.geoip_database_repository import GeoipDatabaseRepository
from omega_track.ports.repositories.settings_repository import SettingsRepository
from omega_track.ports.services.secret_store import SecretStore

_PROVIDER_SETTING_KEY = "geoip_provider"
_MAXMIND_LICENSE_KEY_NAME = "maxmind_license_key"


def select_geoip_provider(*, settings_repository: SettingsRepository, provider: str) -> None:
    if provider not in VALID_GEOIP_PROVIDERS:
        raise UnknownGeoIpProviderError(provider)
    settings_repository.set(_PROVIDER_SETTING_KEY, provider)


def configure_maxmind_credentials(*, secret_store: SecretStore, license_key: str) -> None:
    cleaned = license_key.strip()
    if not cleaned:
        raise MaxMindCredentialsMissingError()
    secret_store.set_secret(_MAXMIND_LICENSE_KEY_NAME, cleaned)


@dataclass(frozen=True, slots=True)
class GeoIpConfigurationValidation:
    provider: str
    ready: bool
    reason: str | None
    """'cle_maxmind_absente'|'base_absente_ou_invalide', None si ready."""


def validate_geoip_configuration(
    *,
    settings_repository: SettingsRepository,
    secret_store: SecretStore,
    geoip_database_repository: GeoipDatabaseRepository,
) -> GeoIpConfigurationValidation:
    provider = resolve_active_geoip_provider(settings_repository.get(_PROVIDER_SETTING_KEY))

    if provider == "maxmind" and not secret_store.get_secret(_MAXMIND_LICENSE_KEY_NAME):
        return GeoIpConfigurationValidation(provider=provider, ready=False, reason="cle_maxmind_absente")

    status = geoip_database_repository.get_status(provider)
    if status is None or status.status != "ok":
        return GeoIpConfigurationValidation(provider=provider, ready=False, reason="base_absente_ou_invalide")

    return GeoIpConfigurationValidation(provider=provider, ready=True, reason=None)
