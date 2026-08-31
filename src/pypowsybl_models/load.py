"""Load a pandas DataFrame, as returned by a `Network.get_*()` method, into ORM rows.

See 02-schema-design.md for the convention this implements: every table's
primary key is `snapshot_id` plus the DataFrame's own index column(s), so
loading a DataFrame means resetting its index to columns and attaching the
snapshot identity to every row.

When loading several tables for the same snapshot, call `session.flush()`
between tables, parents before children (substation -> voltage_level ->
bus -> everything else). None of these models declare ORM `relationship()`s,
so SQLAlchemy's automatic dependency sort cannot reorder inserts across
tables within a single flush - it does not reliably order composite
multi-column foreign keys without one, and will raise an IntegrityError.
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import Any

import pandas as pd
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from pypowsybl_models.base import Base


def _clean(value: Any) -> Any:
    """NaN (pypowsybl's "no value"/"not yet computed" marker) becomes NULL."""
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def load_dataframe[ModelT: Base](
    session: Session,
    model: type[ModelT],
    snapshot_id: int,
    scenario_time: datetime,
    df: pd.DataFrame,
) -> list[ModelT]:
    """Insert one `model` row per `df` row, scoped to `snapshot_id`/`scenario_time`.

    Column names are lowercased to match model attribute names - pypowsybl's
    `TSO` column (on `get_substations`) is the only non-lowercase one, mapped
    to the `tso` attribute (see `Substation` in topology.py).

    Columns pypowsybl returns that aren't part of `model` are silently
    dropped - notably CGMES's dynamic per-element `CGMES.*` properties
    (region, sub-region, original class, ...), which are an open-ended
    extension mechanism, not part of this schema's fixed 20 tables (see
    01-api-analysis.md/05-models.md).
    """
    known_attributes = {attr.key for attr in inspect(model).column_attrs}
    rows = []
    for record in df.reset_index().to_dict(orient="records"):
        kwargs = {
            str(key).lower(): _clean(value) for key, value in record.items() if str(key).lower() in known_attributes
        }
        row = model(snapshot_id=snapshot_id, scenario_time=scenario_time, **kwargs)
        session.add(row)
        rows.append(row)
    return rows
