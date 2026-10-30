# Copyright (c) 2026 kraynux - Licence MIT
"""Use case GetSourceDisclosure (plan de dev §12 "affichage préalable
obligatoire... avant toute activation") - texte statique par source,
extrait de docs/DATA_SOURCES.md (a revalider contre la documentation
officielle a jour avant toute promesse chiffree faite a l'utilisateur,
meme prudence que le document source). Interfaces (CLI `source info`/
TUI ecran Sources) affichent ce texte AVANT d'accepter une cle -
`configure_source_key.py` ne fait aucune verification de "l'a-t-on deja
affiche" (statelessement impossible a verifier de facon fiable) : c'est
la responsabilite de l'interface d'afficher ce texte a chaque appel de
configuration, jamais seulement a la premiere fois."""
from __future__ import annotations

from dataclasses import dataclass

from omega_track.application.exceptions import UnknownReputationSourceError
from omega_track.shared.i18n import _


@dataclass(frozen=True, slots=True)
class SourceDisclosure:
    source_name: str
    is_paid: bool
    """True : ne jamais presenter comme "une simple cle gratuite a
    demander" (HIBP, depuis le changement de politique 2022)."""
    quota_notice: str
    data_sent_notice: str
    privacy_notice: str


_DISCLOSURES: dict[str, SourceDisclosure] = {
    "virustotal": SourceDisclosure(
        source_name="virustotal",
        is_paid=False,
        quota_notice=(
            _("Clé API gratuite disponible avec un compte VirusTotal (Google). Quota de "
              "l'ordre de quelques requêtes/minute et quelques centaines/jour pour une clé "
              "gratuite - à revalider contre la documentation officielle, VirusTotal ajuste "
              "régulièrement ces seuils.")
        ),
        data_sent_notice=(
            _("Le domaine ou l'IP observé par ce TrackRun est transmis à VirusTotal (Google). "
              "Selon le type de requête, cette donnée peut être partagée avec l'écosystème "
              "VirusTotal (autres utilisateurs/partenaires du service).")
        ),
        privacy_notice=_("Voir docs/PRIVACY.md - la clé est stockée hors de la base de résultats."),
    ),
    "hibp": SourceDisclosure(
        source_name="hibp",
        is_paid=True,
        quota_notice=(
            _("Source PAYANTE depuis le changement de politique HIBP de 2022 - plus d'offre "
              "d'API gratuite pour les recherches par domaine/breach. Vérifier le plan "
              "tarifaire actuel avant de configurer une clé.")
        ),
        data_sent_notice=_("Le domaine observé par ce TrackRun est transmis à Have I Been Pwned."),
        privacy_notice=_("Voir docs/PRIVACY.md - la clé est stockée hors de la base de résultats."),
    ),
}


def get_source_disclosure(source_name: str) -> SourceDisclosure:
    disclosure = _DISCLOSURES.get(source_name)
    if disclosure is None:
        raise UnknownReputationSourceError(source_name)
    return disclosure


def list_known_reputation_sources() -> list[str]:
    return sorted(_DISCLOSURES)


def secret_name_for(source_name: str) -> str:
    """Convention de nommage de la cle secrete d'une source (partagee par
    application/orchestrators/phases/reputation_phase.py,
    get_source_status.py, configure_source_key.py, clear_source_key.py -
    un seul point de verite pour ne jamais desynchroniser la clef utilisee
    a l'ecriture de celle utilisee a la lecture)."""
    return f"{source_name}_api_key"
