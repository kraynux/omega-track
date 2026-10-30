# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Aide : reference statique des raccourcis et fonctions de
l'application. Adapte du patron screens/help_screen.py d'omega-check
(D-007/D-008) - pas de table de profils systeme (TRACK n'a pas de
concept de profil de ports nomme comme CHECK), remplacee par la liste
des modules de collecte connus (domain/entities/track_profile.py::
KNOWN_MODULES)."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Footer, Header, Static

from omega_track.domain.entities.track_profile import KNOWN_MODULES
from omega_track.interfaces.tui.screens._base import OmegaScreen
from omega_track.shared.i18n import _

_SHORTCUTS = (
    (_("Haut / Bas"), _("Naviguer entre les éléments d'un écran")),
    (_("Tab / Maj+Tab"), _("Naviguer entre les champs d'un formulaire")),
    (_("Échap"), _("Retour à l'écran précédent (confirmation de sortie sur l'accueil)")),
    ("t", _("Thème suivant (appliqué immédiatement, sans confirmation)")),
    ("r", _("Rafraîchir la détection du terminal")),
    ("a", _("Cette aide")),
    ("q", _("Quitter (avec confirmation)")),
)

_SECTIONS = (
    (
        _("Cibles"),
        (
            _("Enregistrer une IP ou un domaine, avec alias et tags. Épingler une cible "
              "l'autorise durablement (plus besoin de confirmation explicite sur ses futures "
              "observations).")
        ),
    ),
    (
        _("Tracker"),
        (
            _("Choisir une cible enregistrée, les modules de collecte à activer et lancer une "
              "observation (TrackRun). Une observation contre une cible non épinglée exige une "
              "confirmation explicite.")
        ),
    ),
    (
        _("Résultats"),
        (
            _("Rapport d'identité complet d'une observation terminée : DNS/RDAP, chemin réseau "
              "(NeoTrace), certificats (Certificate Transparency), archives, ASN/BGP, "
              "relations corrélées entre entités.")
        ),
    ),
    (
        _("Statuts d'un module (onglet Résultats)"),
        (
            _("Terminé : la source a répondu, données exploitables présentes.\nPartiel : au "
              "moins une réponse obtenue, mais pas toutes (ex. certains sauts NeoTrace sans "
              "réponse).\nNon activé : ce module n'était pas coché au lancement de "
              "l'observation.\nNon exécuté : désactivé par une condition (ex. cible IP pour un "
              "module qui n'a de sens que pour un domaine, clé API absente, quota en "
              "attente).\nEn échec : la source a été interrogée mais n'a donné AUCUNE réponse "
              "exploitable (timeout, erreur du serveur distant, réseau injoignable) - ne "
              "signifie jamais que l'application est bloquée ou reste à charger : "
              "l'observation dans son ensemble s'est déjà terminée normalement, seul ce module "
              "précis n'a rien pu produire. Fréquent et normal pour RDAP sur certains "
              "registres/TLD (pas de réponse, service temporairement indisponible, cible sans "
              "enregistrement connu).")
        ),
    ),
    (
        _("Historique"),
        (
            _("Liste toutes les observations passées : filtrage par cible/statut/tag, rejeu "
              "contre la résolution actuelle, export du rapport.")
        ),
    ),
    (
        _("GeoIP - comment l'obtenir"),
        (
            _("DB-IP (fournisseur par défaut) : gratuit, sans inscription - 'Mettre à jour la "
              "base' dans l'écran GeoIP suffit, rien à configurer.\nMaxMind (alternatif, "
              "optionnel) : créer un compte gratuit sur maxmind.com, puis dans 'Mon compte' -> "
              "'Gérer les clés de licence' -> 'Générer une nouvelle clé de licence'. Coller "
              "cette clé dans l'écran GeoIP, choisir 'maxmind' comme fournisseur, puis 'Mettre "
              "à jour la base'.")
        ),
    ),
    (
        _("Sources à clé - comment les obtenir"),
        (
            _("VirusTotal (gratuit avec compte) : créer un compte sur virustotal.com, puis "
              "dans son profil -> 'API key', copier la clé affichée. La coller dans l'écran "
              "'Sources à clé' (choisir 'virustotal', champ Clé API). Quota limité pour une "
              "clé gratuite (quelques requêtes/minute).\nHIBP - Have I Been Pwned (PAYANT "
              "depuis 2022, plus d'offre gratuite) : nécessite un abonnement sur "
              "haveibeenpwned.com/API/Key avant de pouvoir obtenir une clé - jamais présenté "
              "comme gratuite dans cette application.\nDans les deux cas : l'écran affiche "
              "toujours le détail (quota, données envoyées au fournisseur, confidentialité) "
              "avant d'enregistrer une clé. Sans clé configurée, le module correspondant est "
              "simplement ignoré (jamais une erreur bloquante pour le reste de l'observation).")
        ),
    ),
)

_SCOPE_NOTICE = (
    _("Omega-track observe des cibles explicitement enregistrées et autorisées (épinglées ou "
      "confirmation explicite) : aucune découverte ni dérive automatique vers d'autres cibles. "
      "Le score de confiance n'est jamais un verdict de sécurité.")
)


class HelpScreen(OmegaScreen):
    """Reference statique, accessible depuis n'importe quel ecran (touche `a`)."""

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static(_("AIDE"), classes="omega-title")
            yield Static(_("Raccourcis clavier"), classes="omega-subtitle")
            for key, description in _SHORTCUTS:
                yield Static(_("{key:<14} {description}").format(key=key, description=description))
            yield Static("")
            yield Static(_("Fonctions"), classes="omega-subtitle")
            for title, description in _SECTIONS:
                yield Static(f"[b]{title}[/b]\n{description}\n")
            yield Static("")
            yield Static(_("Modules de collecte connus"), classes="omega-subtitle")
            yield Static(", ".join(sorted(KNOWN_MODULES)))
            yield Static("")
            yield Static(_SCOPE_NOTICE, classes="omega-subtitle")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Retour"), id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
