# Copyright (c) 2026 kraynux - Licence MIT
"""Construction du graphe Mermaid des relations d'un IdentityReport (Phase
8) - vit dans application/ (tier 3) plutot que dans
infrastructure/exporters/mermaid_file_exporter.py (tier 2) parce que la
TUI (interfaces/, egalement tier 2, Phase 11, onglet Relations de
screens/results.py) doit produire EXACTEMENT le meme graphe que l'export
`.mmd` sans dupliquer l'algorithme : deux membres du meme palier (tier 2)
ne peuvent pas s'importer l'un l'autre (contrat import-linter
"independence" verifie a chaque phase depuis la Phase 5) - la seule
option legale est de descendre la logique partagee d'un palier, meme
correctif que GeoIpDownloadError (Phase 5) et LogCorrelation (Phase 7)."""
from __future__ import annotations

import html

from omega_track.domain.entities.findings.path import NetworkPath
from omega_track.domain.entities.identity_report import IdentityReport


def _escape(text: str) -> str:
    """Echappement HTML complet (`&`/`<`/`>`/guillemets) - pas seulement
    les guillemets Mermaid : ce graphe est embarque tel quel (`| safe`,
    voir templates/report.html.j2) dans la page HTML exportee, jamais
    re-echappe par Jinja2 (les `<br/>` volontaires du texte doivent
    rester interpretes par mermaid.js) - toute donnee VARIABLE (ref
    d'entite, hostname...) doit donc etre nettoyee ici en amont, sinon un
    hostname malveillant contenant `<script>` s'injecterait tel quel
    dans la page (XSS reel, pas seulement une syntaxe Mermaid cassee)."""
    return html.escape(text, quote=True)


def build_mermaid_graph(report: IdentityReport) -> str:
    entity_refs = sorted(
        {relation.source_entity_ref for relation in report.relations}
        | {relation.target_entity_ref for relation in report.relations}
    )
    node_ids = {ref: f"n{index}" for index, ref in enumerate(entity_refs)}

    lines = ["graph TD"]
    for ref, node_id in node_ids.items():
        lines.append(f'  {node_id}["{_escape(ref)}"]')
    for relation in report.relations:
        source_id = node_ids[relation.source_entity_ref]
        target_id = node_ids[relation.target_entity_ref]
        # Le label d'une ARETE (entre "|...|") doit etre entoure de
        # guillemets des qu'il contient un caractere de forme Mermaid
        # (parentheses, crochets...) - "resolves_to (verified)" sans
        # guillemets cassait le parseur (bug reel signale par
        # l'utilisateur : "Syntax error in text mermaid version 10.9.8"
        # sur tout export HTML contenant au moins une relation).
        label = _escape(f"{relation.relation_type.value} ({relation.confidence.value})")
        lines.append(f'  {source_id} -->|"{label}"| {target_id}')
    return "\n".join(lines)


def build_network_path_mermaid(path: NetworkPath) -> str:
    """Flowchart des sauts d'un chemin NeoTrace (retour utilisateur : le
    rapport HTML doit vraiment montrer un graphe pour NeoTrace, pas
    seulement le tableau IP/hote/RTT deja present) - un noeud par hop,
    relies dans l'ordre de sequence, jamais un hop non-repondant tu
    silencieusement (`*` explicite, meme discipline que le domaine,
    voir domain/entities/findings/path.py::NetworkHop.is_responding)."""
    if not path.hops:
        return "graph LR\n  vide[\"aucun saut collecte\"]"

    lines = ["graph LR"]
    for hop in path.hops:
        node_id = f"h{hop.sequence}"
        if hop.ip is None:
            label = f"#{hop.sequence}<br/>*"
        else:
            rtt = f"{hop.rtt_ms:.1f} ms" if hop.rtt_ms is not None else "?"
            host = f"<br/>{_escape(hop.hostname)}" if hop.hostname else ""
            label = f"#{hop.sequence}<br/>{_escape(str(hop.ip))}{host}<br/>{rtt}"
        lines.append(f'  {node_id}["{label}"]')
    for previous, current in zip(path.hops, path.hops[1:], strict=False):
        lines.append(f"  h{previous.sequence} --> h{current.sequence}")
    return "\n".join(lines)
