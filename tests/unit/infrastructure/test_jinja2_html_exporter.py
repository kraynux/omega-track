# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.path import NetworkHop, NetworkPath
from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.entities.relation import Relation, RelationType
from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.export_options import ExportOptions
from omega_track.domain.value_objects.identifiers import (
    FindingId,
    ModuleRunId,
    RelationId,
    TargetId,
    TrackProfileId,
    TrackRunId,
)
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.infrastructure.exporters.jinja2_html_exporter import Jinja2HtmlExporter

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


def _profile() -> TrackProfile:
    return TrackProfile(
        id=TrackProfileId("profile-1"), name="default", modules={"dns"}, created_at=_NOW, updated_at=_NOW
    )


def _finding() -> Finding:
    return Finding(
        id=FindingId("f1"), track_run_id=TrackRunId("run-1"), module_run_id=ModuleRunId("mr-1"),
        finding_type="dns.a_record", payload={"address": "1.1.1.1"}, confidence=ConfidenceLevel.VERIFIED,
        collection_mode=CollectionMode.ACTIVE_LIGHT, source_name="dns", observed_at=_NOW, collected_at=_NOW,
    )


def _relation() -> Relation:
    return Relation(
        id=RelationId("rel-1"), track_run_id=TrackRunId("run-1"), source_entity_ref="example.com",
        target_entity_ref="1.1.1.1", relation_type=RelationType.RESOLVES_TO, confidence=ConfidenceLevel.VERIFIED,
    )


def test_html_is_a_standalone_document_with_mermaid_embedded_inline() -> None:
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
        findings=[_finding()], relations=[_relation()],
    )
    html = Jinja2HtmlExporter().export(report, ExportOptions()).decode("utf-8")

    assert html.startswith("<!doctype html>")
    assert "example.com" in html
    assert "dns.a_record" in html
    assert '<pre class="mermaid">' in html
    assert "resolves_to" in html
    assert "mermaid" in html.lower()


def test_html_escapes_untrusted_payload_content() -> None:
    malicious = Finding(
        id=FindingId("f1"), track_run_id=TrackRunId("run-1"), module_run_id=ModuleRunId("mr-1"),
        finding_type="dns.txt_record", payload={"text": "<script>alert(1)</script>"},
        confidence=ConfidenceLevel.VERIFIED, collection_mode=CollectionMode.ACTIVE_LIGHT,
        source_name="dns", observed_at=_NOW, collected_at=_NOW,
    )
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
        findings=[malicious],
    )
    html = Jinja2HtmlExporter().export(report, ExportOptions()).decode("utf-8")
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_html_omits_mermaid_graph_when_disabled_in_options() -> None:
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
        relations=[_relation()],
    )
    html = Jinja2HtmlExporter().export(report, ExportOptions(include_relations_graph=False)).decode("utf-8")
    mermaid_block = html.split('<pre class="mermaid">')[1].split("</pre>")[0]
    assert mermaid_block.strip() == ""
    # la table des relations reste affichee, seul le graphe est desactive
    assert "resolves_to" in html


def test_html_includes_network_path_table() -> None:
    ip = IPAddress.parse("1.1.1.1")
    path = NetworkPath(target_ip=ip, protocol="icmp", hops=[NetworkHop(sequence=1, ip=ip, rtt_ms=1.5)])
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
        paths=[path],
    )
    html = Jinja2HtmlExporter().export(report, ExportOptions()).decode("utf-8")
    assert "1.1.1.1" in html
    assert "atteinte" in html


def test_html_includes_a_mermaid_flowchart_for_each_network_path() -> None:
    """Regression Phase 12 : "neotrace l'export est sense faire un
    graphe, il n'apparait pas" - chaque chemin NeoTrace doit embarquer son
    propre flowchart Mermaid, pas seulement le tableau IP/hote/RTT."""
    ip = IPAddress.parse("1.1.1.1")
    path = NetworkPath(
        target_ip=ip, protocol="icmp",
        hops=[NetworkHop(sequence=1, ip=IPAddress.parse("192.168.1.1"), hostname="gateway"), NetworkHop(sequence=2, ip=ip, rtt_ms=1.5)],
    )
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
        paths=[path],
    )
    html = Jinja2HtmlExporter().export(report, ExportOptions()).decode("utf-8")
    mermaid_blocks = html.count('<pre class="mermaid">')
    assert mermaid_blocks == 1  # aucune relation dans ce rapport, seul le chemin en a un
    assert "graph LR" in html
    assert "h1 --> h2" in html


def test_html_escapes_untrusted_content_even_inside_the_mermaid_block() -> None:
    """Le graphe Mermaid est embarque via `| safe` (les balises `<br/>`
    volontaires ne doivent pas etre re-echappees par Jinja2) - une donnee
    variable malveillante (ici un hostname retourne par un reverse DNS
    hostile) ne doit donc jamais atteindre le document HTML final non
    echappee : l'echappement doit avoir lieu en amont, dans
    mermaid_graph_builder.py, pas compter sur l'autoescape du template."""
    ip = IPAddress.parse("1.1.1.1")
    path = NetworkPath(
        target_ip=ip, protocol="icmp",
        hops=[NetworkHop(sequence=1, ip=ip, hostname="<script>alert(1)</script>")],
    )
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
        paths=[path],
    )
    html = Jinja2HtmlExporter().export(report, ExportOptions()).decode("utf-8")
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_html_configures_mermaid_theme_variables_from_the_palette() -> None:
    """Regression Phase 12 : "les dessins... police claire donc on voit
    pas" - mermaid.js utilise ses propres couleurs par defaut sans
    rapport avec le theme de la page ; il faut forcer des themeVariables
    derivees de la meme palette pour rester lisible."""
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
    )
    html = Jinja2HtmlExporter().export(report, ExportOptions()).decode("utf-8")
    assert "themeVariables" in html
    assert 'theme: "base"' in html
    assert "primaryTextColor" in html
    assert "edgeLabelBackground" in html


def test_html_uses_the_terminal_window_layout_ported_from_omega_fire() -> None:
    """Regression Phase 12 : "les themes d'export sont pas complets...
    base toi sur omega-fire, type terminal" - bandeau a 3 points colores
    (rouge/jaune/vert via error/warning/success) au-dessus du contenu."""
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
    )
    html = Jinja2HtmlExporter().export(report, ExportOptions()).decode("utf-8")
    assert "terminal-header" in html
    assert "dot-close" in html and "dot-min" in html and "dot-max" in html
    assert "omega-track -- example.com" in html


def test_html_colors_findings_and_relations_by_confidence_level() -> None:
    """Les 9 jetons de la palette doivent tous etre reellement exploites
    (le premier jet n'utilisait ni success/warning/error) - un badge de
    confiance par finding/relation, colore selon le niveau."""
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
        findings=[_finding()], relations=[_relation()],
    )
    html = Jinja2HtmlExporter().export(report, ExportOptions()).decode("utf-8")
    assert 'class="badge confidence-verified"' in html


def test_html_footer_states_the_export_theme_used() -> None:
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
    )
    html = Jinja2HtmlExporter().export(report, ExportOptions(export_theme="omega-burn")).decode("utf-8")
    assert "omega-burn" in html


def test_html_applies_the_chosen_export_theme_palette() -> None:
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
    )
    default_html = Jinja2HtmlExporter().export(report, ExportOptions()).decode("utf-8")
    neon_html = Jinja2HtmlExporter().export(report, ExportOptions(export_theme="omega-neon")).decode("utf-8")
    assert default_html != neon_html
