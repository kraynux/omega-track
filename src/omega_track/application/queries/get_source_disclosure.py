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
            "Cle API gratuite disponible avec un compte VirusTotal (Google). "
            "Quota de l'ordre de quelques requetes/minute et quelques centaines/jour "
            "pour une cle gratuite - a revalider contre la documentation officielle, "
            "VirusTotal ajuste regulierement ces seuils."
        ),
        data_sent_notice=(
            "Le domaine ou l'IP observe par ce TrackRun est transmis a VirusTotal (Google). "
            "Selon le type de requete, cette donnee peut etre partagee avec l'ecosysteme "
            "VirusTotal (autres utilisateurs/partenaires du service)."
        ),
        privacy_notice="Voir docs/PRIVACY.md - la cle est stockee hors de la base de resultats.",
    ),
    "hibp": SourceDisclosure(
        source_name="hibp",
        is_paid=True,
        quota_notice=(
            "Source PAYANTE depuis le changement de politique HIBP de 2022 - "
            "plus d'offre d'API gratuite pour les recherches par domaine/breach. "
            "Verifier le plan tarifaire actuel avant de configurer une cle."
        ),
        data_sent_notice="Le domaine observe par ce TrackRun est transmis a Have I Been Pwned.",
        privacy_notice="Voir docs/PRIVACY.md - la cle est stockee hors de la base de resultats.",
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
