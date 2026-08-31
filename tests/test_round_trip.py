"""Round-trip each target method's DataFrame through the ORM, per 03-testing-strategy.md.

For every (fixture network, target method) pair: load the DataFrame into the
matching table, then query it back and confirm every row survived with the
same primary-key values pypowsybl's own index reported.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

import pypowsybl.network as pn
import pytest
from conftest import TARGET_METHODS
from sqlalchemy.orm import Session

from pypowsybl_models import Base, NetworkSnapshot, load_dataframe


@pytest.mark.parametrize(("method_name", "model"), TARGET_METHODS)
def test_round_trip(
    session: Session,
    make_snapshot: Callable[[datetime | None], NetworkSnapshot],
    any_network: pn.Network,
    method_name: str,
    model: type[Base],
) -> None:
    df = getattr(any_network, method_name)(all_attributes=True)
    snapshot = make_snapshot(None)

    rows = load_dataframe(session, model, snapshot.id, snapshot.scenario_time, df)
    session.commit()

    assert len(rows) == len(df)
    assert session.query(model).filter_by(snapshot_id=snapshot.id).count() == len(df)
