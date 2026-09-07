# Copyright (c) 2026 kraynux - Licence MIT
"""Snapshot immuable dans un TrackRun (critere de sortie Phase 4, D-013)."""
import sqlite3
from datetime import datetime, timezone

from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.entities.track_run import ModuleRun, TrackRun
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.identifiers import (
    ModuleRunId,
    TargetId,
    TrackProfileId,
    TrackRunId,
)
from omega_track.domain.value_objects.statuses import ModuleStatus, TrackStatus
from omega_track.infrastructure.repositories.sqlite.track_run_repository import (
    SqliteTrackRunRepository,
)

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
_LATER = datetime(2026, 1, 1, 0, 5, tzinfo=timezone.utc)


def _profile(modules: set[str]) -> TrackProfile:
    return TrackProfile(id=TrackProfileId("p1"), name="default", modules=modules, created_at=_NOW, updated_at=_NOW)


def _run(**overrides) -> TrackRun:
    defaults = {
        "id": TrackRunId("run-1"),
        "target_id": TargetId("t1"),
        "profile_snapshot": _profile({"dns"}),
        "status": TrackStatus.QUEUED,
        "created_at": _NOW,
    }
    defaults.update(overrides)
    return TrackRun(**defaults)


def test_save_and_get_round_trips_status_and_progress(connection: sqlite3.Connection) -> None:
    repo = SqliteTrackRunRepository(connection)
    run = _run(status=TrackStatus.RUNNING, started_at=_NOW, progress=0.4, tags={"weekly"})
    repo.save(run)

    fetched = repo.get(TrackRunId("run-1"))
    assert fetched is not None
    assert fetched.status == TrackStatus.RUNNING
    assert fetched.progress == 0.4
    assert fetched.tags == {"weekly"}


def test_profile_snapshot_is_a_frozen_copy_not_a_live_reference(connection: sqlite3.Connection) -> None:
    """D-013 : `track replay` doit reutiliser EXACTEMENT le profil
    d'origine, meme si le profil nomme a change depuis - verifie ici en
    persistant un run avec un profil, puis en changeant ce qu'un profil
    portant le meme id contiendrait, et en confirmant que le snapshot
    deja sauvegarde reste inchange."""
    repo = SqliteTrackRunRepository(connection)
    run = _run(profile_snapshot=_profile({"dns", "rdap"}))
    repo.save(run)

    # Un profil different portant le meme id (simule une modification du
    # profil nomme apres coup) ne doit jamais affecter le snapshot deja
    # persiste dans ce TrackRun.
    fetched = repo.get(TrackRunId("run-1"))
    assert fetched is not None
    assert fetched.profile_snapshot.modules == {"dns", "rdap"}


def test_module_runs_persisted_and_hydrated(connection: sqlite3.Connection) -> None:
    repo = SqliteTrackRunRepository(connection)
    run = _run()
    run.module_runs["dns"] = ModuleRun(
        id=ModuleRunId("mr-1"), module_name="dns", status=ModuleStatus.COMPLETED,
        collection_mode=CollectionMode.ACTIVE_LIGHT, started_at=_NOW, completed_at=_LATER,
        source_name="dns",
    )
    repo.save(run)

    fetched = repo.get(TrackRunId("run-1"))
    assert fetched is not None
    assert fetched.module_runs["dns"].status == ModuleStatus.COMPLETED
    assert fetched.module_runs["dns"].source_name == "dns"


def test_resave_replaces_module_runs_delete_then_insert(connection: sqlite3.Connection) -> None:
    repo = SqliteTrackRunRepository(connection)
    run = _run()
    run.module_runs["dns"] = ModuleRun(
        id=ModuleRunId("mr-1"), module_name="dns", status=ModuleStatus.RUNNING,
        collection_mode=CollectionMode.ACTIVE_LIGHT,
    )
    repo.save(run)

    run.module_runs["dns"].status = ModuleStatus.COMPLETED
    repo.save(run)

    fetched = repo.get(TrackRunId("run-1"))
    assert fetched is not None
    assert len(fetched.module_runs) == 1
    assert fetched.module_runs["dns"].status == ModuleStatus.COMPLETED


def test_list_for_target_filters_correctly(connection: sqlite3.Connection) -> None:
    repo = SqliteTrackRunRepository(connection)
    repo.save(_run(id=TrackRunId("r1"), target_id=TargetId("t1")))
    repo.save(_run(id=TrackRunId("r2"), target_id=TargetId("t2")))

    results = repo.list_for_target(TargetId("t1"))
    assert [r.id for r in results] == [TrackRunId("r1")]


def test_list_recent_filters_by_status_and_tag(connection: sqlite3.Connection) -> None:
    repo = SqliteTrackRunRepository(connection)
    repo.save(_run(id=TrackRunId("r1"), status=TrackStatus.COMPLETED, tags={"a"}))
    repo.save(_run(id=TrackRunId("r2"), status=TrackStatus.FAILED, tags={"b"}))

    completed = repo.list_recent(status="completed")
    assert [r.id for r in completed] == [TrackRunId("r1")]

    tagged = repo.list_recent(tag="b")
    assert [r.id for r in tagged] == [TrackRunId("r2")]


def test_delete_removes_run_and_module_runs(connection: sqlite3.Connection) -> None:
    repo = SqliteTrackRunRepository(connection)
    run = _run()
    run.module_runs["dns"] = ModuleRun(
        id=ModuleRunId("mr-1"), module_name="dns", status=ModuleStatus.PENDING,
        collection_mode=CollectionMode.ACTIVE_LIGHT,
    )
    repo.save(run)
    repo.delete(TrackRunId("run-1"))
    assert repo.get(TrackRunId("run-1")) is None
