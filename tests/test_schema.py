"""Schema-level checks that don't need pypowsybl data - per 03-testing-strategy.md step 1."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from conftest import TARGET_METHODS
from sqlalchemy import Engine, inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from pypowsybl_models import Base, Bus, NetworkSnapshot, Substation, VoltageLevel


def test_all_21_tables_exist() -> None:
    tables = set(Base.metadata.tables.keys())
    expected = {"network_snapshot"} | {model.__tablename__ for _, model in TARGET_METHODS}  # type: ignore[attr-defined]
    assert tables == expected
    assert len(tables) == 21


def test_composite_primary_keys(strict_engine: Engine) -> None:
    inspector = inspect(strict_engine)
    pk = inspector.get_pk_constraint("loading_limit")["constrained_columns"]
    assert set(pk) == {"snapshot_id", "element_id", "side", "type", "acceptable_duration", "group_name"}

    pk = inspector.get_pk_constraint("ratio_tap_changer_step")["constrained_columns"]
    assert set(pk) == {"snapshot_id", "id", "side", "position"}


def test_snapshot_scoped_fk_rejects_cross_snapshot_reference(strict_session: Session) -> None:
    """A bus row must not be able to reference a voltage level from a different snapshot."""
    snapshot_a = NetworkSnapshot(scenario_time=datetime(2026, 1, 1, tzinfo=UTC))
    snapshot_b = NetworkSnapshot(scenario_time=datetime(2026, 1, 2, tzinfo=UTC))
    strict_session.add_all([snapshot_a, snapshot_b])
    strict_session.flush()

    strict_session.add(Substation(snapshot_id=snapshot_a.id, scenario_time=snapshot_a.scenario_time, id="S1"))
    strict_session.add(
        VoltageLevel(
            snapshot_id=snapshot_a.id,
            scenario_time=snapshot_a.scenario_time,
            id="VL1",
            substation_id="S1",
        )
    )
    strict_session.flush()

    # VL1 exists in snapshot A, not in snapshot B - a bus in B pointing at it must fail.
    strict_session.add(
        Bus(
            snapshot_id=snapshot_b.id,
            scenario_time=snapshot_b.scenario_time,
            id="BUS1",
            voltage_level_id="VL1",
        )
    )
    with pytest.raises(IntegrityError):
        strict_session.flush()
