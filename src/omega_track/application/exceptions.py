# Copyright (c) 2026 kraynux - Licence MIT
"""Racine des erreurs de la couche application (use cases, orchestration)
- meme convention que CHECK (application/exceptions.py::ApplicationError),
premier module de ce genre chez TRACK (Phase 5)."""
from __future__ import annotations

from omega_track.core.errors import OmegaTrackError
from omega_track.domain.value_objects.identifiers import TargetId, TrackRunId


class ApplicationError(OmegaTrackError):
    """Racine des echecs attendus de la couche application - jamais levee
    directement."""


class UnknownGeoIpProviderError(ApplicationError):
    """Fournisseur GeoIP demande hors du catalogue connu ('dbip'/'maxmind')."""

    def __init__(self, provider: str) -> None:
        super().__init__(f"fournisseur GeoIP inconnu : {provider!r}")
        self.provider = provider


class MaxMindCredentialsMissingError(ApplicationError):
    """Cle de licence MaxMind absente ou vide - precondition de
    configuration distincte d'un echec de telechargement (voir
    GeoIpDownloadError ci-dessous)."""

    def __init__(self) -> None:
        super().__init__("cle de licence MaxMind absente ou vide")


class GeoIpDownloadError(ApplicationError):
    """Echec de telechargement/extraction/validation d'une base GeoIP
    (Phase 5) - jamais destructif : leve avant tout remplacement de
    l'ancien fichier (voir infrastructure/geoip/database_updater.py).

    Definie ici plutot que dans infrastructure/exceptions.py : c'est le
    type technique qu'application/commands/geoip/_download.py doit
    connaitre par son nom pour persister un statut 'download_failed' sans
    toucher au fichier existant, et la Dependency Rule interdit a
    application/ d'importer infrastructure/ (meme raisonnement que
    TargetResolutionError chez CHECK). infrastructure/geoip/
    database_updater.py importe ce type depuis ICI (sens autorise :
    infrastructure -> application) et le leve."""


class UnknownThemeError(ApplicationError):
    """Nom de theme demande absent du catalogue
    omega_lib.theme.policies.TUI_THEMES (Phase 11, meme convention que
    CHECK/DEEP/FOLD - D-008)."""

    def __init__(self, theme_name: str) -> None:
        super().__init__(f"theme inconnu : {theme_name!r}")
        self.theme_name = theme_name


class UnknownExportFormatError(ApplicationError):
    """Format d'export demande hors du catalogue connu ('json'/'markdown'/
    'html'/'csv'/'dot'/'mermaid', Phase 8)."""

    def __init__(self, export_format: str) -> None:
        super().__init__(f"format d'export inconnu : {export_format!r}")
        self.export_format = export_format


class TargetNotFoundError(ApplicationError):
    """Cible introuvable pour l'identifiant fourni (Phase 9)."""

    def __init__(self, target_id: TargetId) -> None:
        super().__init__(f"cible introuvable : {target_id!r}")
        self.target_id = target_id


class TrackRunNotFoundError(ApplicationError):
    """TrackRun ou Target associee introuvable (Phase 8, reutilisable par
    tout use case futur ayant besoin de charger un TrackRun existant -
    ex. Phase 9 `track show`)."""

    def __init__(self, track_run_id: TrackRunId) -> None:
        super().__init__(f"TrackRun introuvable : {track_run_id!r}")
        self.track_run_id = track_run_id


class CollectorUnavailableError(ApplicationError):
    """Source totalement indisponible (reseau, resolveur, binaire absent)
    (Phase 6, D-015) - distinct d'un champ/enregistrement individuel
    absent, qui n'est jamais une erreur. Un collecteur
    (infrastructure/collectors/) leve ceci uniquement quand la source
    entiere ne peut repondre, jamais pour une donnee simplement manquante
    dans une reponse par ailleurs valide. Meme raisonnement de placement
    que GeoIpDownloadError ci-dessus (infrastructure -> application)."""

    def __init__(self, source: str, reason: str | None = None) -> None:
        message = f"source indisponible : {source}"
        if reason:
            message = f"{message} ({reason})"
        super().__init__(message)
        self.source = source
        self.reason = reason


class UnknownReputationSourceError(ApplicationError):
    """Nom de source de reputation demande hors du catalogue connu
    ('virustotal'/'hibp', Phase 12)."""

    def __init__(self, source_name: str) -> None:
        super().__init__(f"source de reputation inconnue : {source_name!r}")
        self.source_name = source_name


class ApiKeyMissingError(ApplicationError):
    """Cle API absente ou vide fournie a une commande de configuration de
    source (Phase 12) - precondition de configuration, distincte d'une
    source non executee faute de cle DANS un TrackRun (celle-ci ne leve
    jamais rien, voir application/orchestrators/phases/
    reputation_phase.py)."""

    def __init__(self, source_name: str) -> None:
        super().__init__(f"cle API absente ou vide pour {source_name!r}")
        self.source_name = source_name


class QuotaExceededError(ApplicationError):
    """Quota d'une source a cle depasse (Phase 12, HTTP 429 typiquement) -
    distinct de CollectorUnavailableError : la source elle-meme fonctionne,
    c'est la limite d'usage qui est atteinte. Capturee par
    application/orchestrators/phases/reputation_phase.py pour enregistrer
    un backoff persistant (application/policies/quota_backoff.py) evitant
    de retenter inutilement au prochain TrackRun."""

    def __init__(self, source: str) -> None:
        super().__init__(f"quota depasse : {source}")
        self.source = source
