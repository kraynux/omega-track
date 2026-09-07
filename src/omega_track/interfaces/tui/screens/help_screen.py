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

_SHORTCUTS = (
    ("Haut / Bas", "Naviguer entre les elements d'un ecran"),
    ("Tab / Maj+Tab", "Naviguer entre les champs d'un formulaire"),
    ("Echap", "Retour a l'ecran precedent (confirmation de sortie sur l'accueil)"),
    ("t", "Theme suivant (applique immediatement, sans confirmation)"),
    ("r", "Rafraichir la detection du terminal"),
    ("a", "Cette aide"),
    ("q", "Quitter (avec confirmation)"),
)

_SECTIONS = (
    (
        "Cibles",
        (
            "Enregistrer une IP ou un domaine, avec alias et tags. Epingler une "
            "cible l'autorise durablement (plus besoin de confirmation explicite "
            "sur ses futures observations)."
        ),
    ),
    (
        "Tracker",
        (
            "Choisir une cible enregistree, les modules de collecte a activer et "
            "lancer une observation (TrackRun). Une observation contre une cible "
            "non epinglee exige une confirmation explicite."
        ),
    ),
    (
        "Resultats",
        (
            "Rapport d'identite complet d'une observation terminee : DNS/RDAP, "
            "chemin reseau (NeoTrace), certificats (Certificate Transparency), "
            "archives, ASN/BGP, relations correlees entre entites."
        ),
    ),
    (
        "Statuts d'un module (onglet Resultats)",
        (
            "Termine : la source a repondu, donnees exploitables presentes.\n"
            "Partiel : au moins une reponse obtenue, mais pas toutes (ex. certains "
            "sauts NeoTrace sans reponse).\n"
            "Non active : ce module n'etait pas coche au lancement de l'observation.\n"
            "Non execute : desactive par une condition (ex. cible IP pour un module "
            "qui n'a de sens que pour un domaine, cle API absente, quota en attente).\n"
            "En echec : la source a ete interrogee mais n'a donne AUCUNE reponse "
            "exploitable (timeout, erreur du serveur distant, reseau injoignable) - "
            "ne signifie jamais que l'application est bloquee ou reste a charger : "
            "l'observation dans son ensemble s'est deja terminee normalement, seul "
            "ce module precis n'a rien pu produire. Frequent et normal pour RDAP sur "
            "certains registres/TLD (pas de reponse, service temporairement "
            "indisponible, cible sans enregistrement connu)."
        ),
    ),
    (
        "Historique",
        (
            "Liste toutes les observations passees : filtrage par cible/statut/"
            "tag, rejeu contre la resolution actuelle, export du rapport."
        ),
    ),
    (
        "GeoIP - comment l'obtenir",
        (
            "DB-IP (fournisseur par defaut) : gratuit, sans inscription - "
            "'Mettre a jour la base' dans l'ecran GeoIP suffit, rien a configurer.\n"
            "MaxMind (alternatif, optionnel) : creer un compte gratuit sur "
            "maxmind.com, puis dans 'Mon compte' -> 'Gerer les cles de licence' -> "
            "'Generer une nouvelle cle de licence'. Coller cette cle dans l'ecran "
            "GeoIP, choisir 'maxmind' comme fournisseur, puis 'Mettre a jour la base'."
        ),
    ),
    (
        "Sources a cle - comment les obtenir",
        (
            "VirusTotal (gratuit avec compte) : creer un compte sur virustotal.com, "
            "puis dans son profil -> 'API key', copier la cle affichee. La coller "
            "dans l'ecran 'Sources a cle' (choisir 'virustotal', champ Cle API). "
            "Quota limite pour une cle gratuite (quelques requetes/minute).\n"
            "HIBP - Have I Been Pwned (PAYANT depuis 2022, plus d'offre gratuite) : "
            "necessite un abonnement sur haveibeenpwned.com/API/Key avant de pouvoir "
            "obtenir une cle - jamais presente comme gratuite dans cette application.\n"
            "Dans les deux cas : l'ecran affiche toujours le detail (quota, donnees "
            "envoyees au fournisseur, confidentialite) avant d'enregistrer une cle. "
            "Sans cle configuree, le module correspondant est simplement ignore "
            "(jamais une erreur bloquante pour le reste de l'observation)."
        ),
    ),
)

_SCOPE_NOTICE = (
    "Omega-track observe des cibles explicitement enregistrees et autorisees "
    "(epinglees ou confirmation explicite) : aucune decouverte ni derive "
    "automatique vers d'autres cibles. Le score de confiance n'est jamais un "
    "verdict de securite."
)


class HelpScreen(OmegaScreen):
    """Reference statique, accessible depuis n'importe quel ecran (touche `a`)."""

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static("AIDE", classes="omega-title")
            yield Static("Raccourcis clavier", classes="omega-subtitle")
            for key, description in _SHORTCUTS:
                yield Static(f"{key:<14} {description}")
            yield Static("")
            yield Static("Fonctions", classes="omega-subtitle")
            for title, description in _SECTIONS:
                yield Static(f"[b]{title}[/b]\n{description}\n")
            yield Static("")
            yield Static("Modules de collecte connus", classes="omega-subtitle")
            yield Static(", ".join(sorted(KNOWN_MODULES)))
            yield Static("")
            yield Static(_SCOPE_NOTICE, classes="omega-subtitle")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
