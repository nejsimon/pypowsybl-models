"""Multiple snapshots of the same network must not collide, per 03-testing-strategy.md step 4.

This is the main thing the snapshot_id-in-primary-key design (02-schema-design.md)
needs to prove: the same network, loaded twice under two different
network_snapshot rows, must not raise a primary-key violation, and each
snapshot's data must be independently queryable.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pypowsybl.network as pn
from sqlalchemy.orm import Session

from pypowsybl_models import Generator, NetworkSnapshot, load_dataframe


def test_same_network_loaded_twice_under_different_snapshots(session: Session, eurostag_network: pn.Network) -> None:
    df = eurostag_network.get_generators(all_attributes=True)

    snapshot_1 = NetworkSnapshot(scenario_time=datetime(2026, 1, 1, tzinfo=UTC))
    snapshot_2 = NetworkSnapshot(scenario_time=datetime(2026, 1, 2, tzinfo=UTC))
    session.add_all([snapshot_1, snapshot_2])
    session.flush()

    load_dataframe(session, Generator, snapshot_1.id, snapshot_1.scenario_time, df)
    load_dataframe(session, Generator, snapshot_2.id, snapshot_2.scenario_time, df)
    session.commit()

    assert session.query(Generator).filter_by(snapshot_id=snapshot_1.id).count() == len(df)
    assert session.query(Generator).filter_by(snapshot_id=snapshot_2.id).count() == len(df)
    assert session.query(Generator).count() == 2 * len(df)

    # Same generator id, two different snapshots - independently queryable, not merged.
    generator_id = df.index[0]
    rows = session.query(Generator).filter_by(id=generator_id).order_by(Generator.snapshot_id).all()
    assert [row.snapshot_id for row in rows] == [snapshot_1.id, snapshot_2.id]
