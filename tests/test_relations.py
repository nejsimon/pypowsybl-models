"""Cross-table relation integrity, per 03-testing-strategy.md step 3.

Loads a real fixture network's substation/voltage-level/bus/line data and
confirms every foreign key referenced by a child row actually resolves to a
row that was inserted for its parent - catching insertion-order bugs and
validating the relations from 02-schema-design.md against real data.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pypowsybl.network as pn
from sqlalchemy.orm import Session

from pypowsybl_models import Bus, Line, NetworkSnapshot, Substation, VoltageLevel, load_dataframe


def test_bus_and_line_references_resolve(strict_session: Session, micro_grid_be_network: pn.Network) -> None:
    snapshot = NetworkSnapshot(scenario_time=datetime(2026, 1, 1, tzinfo=UTC))
    strict_session.add(snapshot)
    strict_session.flush()

    network = micro_grid_be_network
    sid, stime = snapshot.id, snapshot.scenario_time
    # Insertion order matters: parents before children, matching the
    # substation -> voltage_level -> bus -> line hierarchy in 02-schema-design.md.
    # Flushing after each table is required - without declared relationship()s,
    # SQLAlchemy's automatic dependency sort doesn't reliably order composite
    # multi-column foreign keys across a single flush.
    load_dataframe(strict_session, Substation, sid, stime, network.get_substations(all_attributes=True))
    strict_session.flush()
    load_dataframe(strict_session, VoltageLevel, sid, stime, network.get_voltage_levels(all_attributes=True))
    strict_session.flush()
    load_dataframe(strict_session, Bus, sid, stime, network.get_buses(all_attributes=True))
    strict_session.flush()
    load_dataframe(strict_session, Line, sid, stime, network.get_lines(all_attributes=True))
    strict_session.commit()

    voltage_level_ids = {vl.id for vl in strict_session.query(VoltageLevel).filter_by(snapshot_id=snapshot.id)}
    substation_ids = {s.id for s in strict_session.query(Substation).filter_by(snapshot_id=snapshot.id)}
    bus_ids = {b.id for b in strict_session.query(Bus).filter_by(snapshot_id=snapshot.id)}

    for vl in strict_session.query(VoltageLevel).filter_by(snapshot_id=snapshot.id):
        assert vl.substation_id in substation_ids

    for bus in strict_session.query(Bus).filter_by(snapshot_id=snapshot.id):
        assert bus.voltage_level_id in voltage_level_ids

    for line in strict_session.query(Line).filter_by(snapshot_id=snapshot.id):
        assert line.voltage_level1_id in voltage_level_ids
        assert line.voltage_level2_id in voltage_level_ids
        if line.bus1_id is not None:
            assert line.bus1_id in bus_ids
        if line.bus2_id is not None:
            assert line.bus2_id in bus_ids
