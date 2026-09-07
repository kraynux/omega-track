# Copyright (c) 2026 kraynux - Licence MIT
"""Definition DDL des tables SQLite (plan de dev, Phase 4).

Colonnes choisies pour tenir des maintenant les principes de fusion
Suite (D-006, ~/DEV/SUITE/DECISIONS_ARCHITECTURE.md) : `id` en UUID TEXT
(jamais autoincrement, `omega_lib.shared.ids`), `tool` present des la v1
solo (`'track'` par defaut, meme colonne que `scans.tool` chez CHECK),
`created_at`/`started_at`/etc. en ISO8601 UTC.

Schema additif (`CREATE TABLE IF NOT EXISTS` uniquement) - pas de moteur
de migration `ALTER TABLE` en MVP (D-018, angle mort 9) : un vrai systeme
de migration reste un objectif de v1.0 stabilisation (Phase 14), pas
anticipe ici.

Ecart assume par rapport a l'esquisse initiale du plan (§Phase 4) :
- `findings`/`relations` portent `evidences_json` (une VRAIE liste de
  preuves, pas un simple `source_reference` singulier) - le domaine
  (Phase 2, `Finding.evidences: list[Evidence]`) l'exige deja, la
  dedup/corroboration (D-011) ne fonctionnerait pas avec une seule
  reference.
- `geoip_databases.provider` est la cle primaire naturelle, pas un `id`
  UUID separe - `GeoIpDatabaseStatus` (domaine, Phase 3) ne porte pas de
  champ `id` propre, un seul statut existe par fournisseur (get_status(provider)).
- Pas de table `settings` (contredirait la decision Phase 4 elle-meme :
  `settings.json`, une seule source de verite pour les reglages)."""
from __future__ import annotations

SCHEMA_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS targets (
        id TEXT PRIMARY KEY,
        tool TEXT NOT NULL DEFAULT 'track',
        normalized_value TEXT NOT NULL,
        target_kind TEXT NOT NULL,
        alias TEXT,
        tags_json TEXT NOT NULL,
        pinned INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        last_track_at TEXT,
        last_status TEXT
    )
    """,
    """
    CREATE UNIQUE INDEX IF NOT EXISTS idx_targets_value
    ON targets (normalized_value, target_kind)
    """,
    """
    CREATE TABLE IF NOT EXISTS track_profiles (
        id TEXT PRIMARY KEY,
        tool TEXT NOT NULL DEFAULT 'track',
        name TEXT NOT NULL,
        is_default INTEGER NOT NULL,
        modules_json TEXT NOT NULL,
        options_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS track_runs (
        id TEXT PRIMARY KEY,
        tool TEXT NOT NULL DEFAULT 'track',
        target_id TEXT NOT NULL REFERENCES targets (id),
        profile_snapshot_json TEXT NOT NULL,
        status TEXT NOT NULL,
        progress REAL NOT NULL,
        created_at TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT,
        error_summary TEXT,
        tags_json TEXT NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_track_runs_target_id ON track_runs (target_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS module_runs (
        id TEXT PRIMARY KEY,
        track_run_id TEXT NOT NULL REFERENCES track_runs (id),
        module_name TEXT NOT NULL,
        status TEXT NOT NULL,
        collection_mode TEXT NOT NULL,
        started_at TEXT,
        completed_at TEXT,
        source_name TEXT,
        error_code TEXT,
        error_detail TEXT
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_module_runs_track_run_id ON module_runs (track_run_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS findings (
        id TEXT PRIMARY KEY,
        track_run_id TEXT NOT NULL REFERENCES track_runs (id),
        module_run_id TEXT NOT NULL REFERENCES module_runs (id),
        finding_type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        confidence TEXT NOT NULL,
        collection_mode TEXT NOT NULL,
        source_name TEXT NOT NULL,
        observed_at TEXT NOT NULL,
        collected_at TEXT NOT NULL,
        evidences_json TEXT NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_findings_track_run_id ON findings (track_run_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS relations (
        id TEXT PRIMARY KEY,
        track_run_id TEXT NOT NULL REFERENCES track_runs (id),
        source_entity_ref TEXT NOT NULL,
        target_entity_ref TEXT NOT NULL,
        relation_type TEXT NOT NULL,
        confidence TEXT NOT NULL,
        evidences_json TEXT NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_relations_track_run_id ON relations (track_run_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS exports (
        id TEXT PRIMARY KEY,
        track_run_id TEXT NOT NULL REFERENCES track_runs (id),
        format TEXT NOT NULL,
        output_path TEXT NOT NULL,
        checksum TEXT NOT NULL,
        redaction_policy TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_exports_track_run_id ON exports (track_run_id)
    """,
    """
    CREATE TABLE IF NOT EXISTS geoip_databases (
        provider TEXT PRIMARY KEY,
        edition TEXT NOT NULL,
        local_path TEXT NOT NULL,
        checksum TEXT NOT NULL,
        downloaded_at TEXT NOT NULL,
        published_at TEXT,
        status TEXT NOT NULL
    )
    """,
)
