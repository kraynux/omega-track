# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de HtmlExporter (Phase 8, etendue Phase 12) -
fichier HTML autonome (aucun serveur requis, "HTML genere sans serveur"
- critere de sortie), sections repliables (`<details>`), graphe de
relations Mermaid embarque INLINE (D-009 - jamais seulement un fichier
`.mmd` a part, reutilise `mermaid_graph_builder.py::build_mermaid_graph`
telle quelle). Theme d'export (5 palettes, `options.export_theme`) porte
depuis omega-check (D-007/D-008, retour utilisateur Phase 12) - template
Jinja2 desormais un vrai fichier `templates/report.html.j2` (charge via
FileSystemLoader), plus une chaine Python inline.

Le rendu Mermaid lui-meme est fait cote navigateur via mermaid.js charge
depuis un CDN (jsdelivr) : le fichier fonctionne sans serveur local, mais
le rendu du graphe suppose un navigateur avec acces reseau au CDN -
limite assumee, pas d'alternative sans vendoring du JS.

Chaque chemin NeoTrace embarque desormais aussi son propre graphe Mermaid
(flowchart des sauts, `build_network_path_mermaid`) en plus du tableau
IP/hote/RTT/ASN/pays deja present - retour utilisateur Phase 12 : "neotrace
l'export est sense faire un graphe, il n'apparait pas". Reste un flowchart
texte/Mermaid, pas une carte Leaflet/OpenStreetMap interactive - une
vraie integration Leaflet est une piece separee substantielle, hors du
critere de sortie strict "HTML genere sans serveur" (Phase 8)."""
from __future__ import annotations

from pathlib import Path

import jinja2

from omega_track.application.orchestrators.mermaid_graph_builder import (
    build_mermaid_graph,
    build_network_path_mermaid,
)
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.value_objects.export_options import ExportOptions
from omega_track.infrastructure.exporters._report_view import build_header, path_to_dict
from omega_track.infrastructure.exporters.html_theme_resolver import resolve_export_palette
from omega_track.shared.i18n import TRANSLATOR, _

_TEMPLATES_DIR = Path(__file__).parent / "templates"

_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(_TEMPLATES_DIR),
    # `autoescape=True` explicite, jamais `select_autoescape(["html"])` :
    # ce dernier decide selon l'EXTENSION du nom de fichier, or
    # "report.html.j2" se termine par ".j2" (pas ".html") et
    # `select_autoescape` retourne alors False - verifie empiriquement,
    # ce qui aurait desactive completement l'echappement HTML (vraie
    # regression XSS trouvee par le test de securite existant en migrant
    # vers un fichier .j2 separe, Phase 12).
    autoescape=True,
)
# Lot N (langue des exports) : texte des gabarits traduit par `_` dans la langue active
# (celle des exports sous translating_as) ; lang= et dir= du document suivent.
_environment.globals.update(_=_, html_lang=TRANSLATOR.html_lang, html_dir=TRANSLATOR.html_dir)
# R1 : texte enregistre en francais (titre, impact...) retraduit dans la langue de l'export.
_environment.filters["tr"] = lambda value: _(value) if isinstance(value, str) and value else value


class Jinja2HtmlExporter:
    """Implemente ports/exporters/html_exporter.py::HtmlExporter."""

    def __init__(self) -> None:
        self._template = _environment.get_template("report.html.j2")

    def export(self, report: IdentityReport, options: ExportOptions) -> bytes:
        findings_by_family: dict[str, list[Finding]] = {}
        for finding in report.findings:
            family = finding.finding_type.split(".", 1)[0]
            findings_by_family.setdefault(family, []).append(finding)

        paths = []
        for path in report.paths:
            path_view = path_to_dict(path)
            path_view["mermaid_graph"] = build_network_path_mermaid(path)
            paths.append(path_view)

        html = self._template.render(
            header=build_header(report, options),
            summary=report.summarize(),
            findings_by_family=dict(sorted(findings_by_family.items())),
            relations=report.relations,
            mermaid_graph=build_mermaid_graph(report) if options.include_relations_graph else "",
            paths=paths,
            palette=resolve_export_palette(options.export_theme),
        )
        return html.encode("utf-8")
