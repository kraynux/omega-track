# Copyright (c) 2026 kraynux - Licence MIT
"""Identification de clusters (composantes connexes du graphe de
relations) - pur, recalcule a la lecture a partir des Relation d'un
TrackRun, jamais persiste independamment (meme discipline que D-011 de
FOLD : ne pas stocker un cache derive d'une donnee deja reconstructible)."""
from __future__ import annotations

from collections import defaultdict

from omega_track.domain.entities.relation import Cluster, Relation


def identify_clusters(relations: list[Relation]) -> list[Cluster]:
    """Union-find simple - suffisant pour la taille d'un graphe TRACK
    (quelques dizaines d'entites au plus par TrackRun, pas besoin d'une
    dependance de graphe lourde)."""
    parent: dict[str, str] = {}

    def find(ref: str) -> str:
        parent.setdefault(ref, ref)
        while parent[ref] != ref:
            parent[ref] = parent[parent[ref]]
            ref = parent[ref]
        return ref

    def union(a: str, b: str) -> None:
        root_a, root_b = find(a), find(b)
        if root_a != root_b:
            parent[root_a] = root_b

    for relation in relations:
        union(relation.source_entity_ref, relation.target_entity_ref)

    groups: dict[str, set[str]] = defaultdict(set)
    for ref in parent:
        groups[find(ref)].add(ref)

    return [
        Cluster(id=f"cluster-{index}", member_refs=members)
        for index, members in enumerate(groups.values())
        if len(members) > 1
    ]
