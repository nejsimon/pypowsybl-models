"""Shared declarative base and the snapshot-scoping convention.

See 02-schema-design.md for the reasoning: every data table's primary key is
`snapshot_id` plus the pandas index column(s) of the pypowsybl method it
mirrors, and every relation between two data tables is additionally scoped by
`snapshot_id` so that a row from one snapshot can never satisfy a foreign key
from another snapshot's row.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class SnapshotScoped:
    """Adds the `snapshot_id` (primary key component) and denormalized
    `scenario_time` columns that every data table carries."""

    snapshot_id: Mapped[int] = mapped_column(ForeignKey("network_snapshot.id"), primary_key=True)
    scenario_time: Mapped[datetime] = mapped_column(index=True)


def snapshot_scoped_fk(
    local_columns: str | Sequence[str],
    target_table: str,
    target_columns: str | Sequence[str] = "id",
) -> ForeignKeyConstraint:
    """A `ForeignKeyConstraint` from this table's `(snapshot_id, *local_columns)`
    to `target_table`'s `(snapshot_id, *target_columns)`.

    `target_columns` defaults to the natural-key column name of every entity
    table in this schema (`id`), so most calls only need `local_columns` and
    `target_table` (e.g. `snapshot_scoped_fk("voltage_level_id", "voltage_level")`).
    """
    locals_ = [local_columns] if isinstance(local_columns, str) else list(local_columns)
    remotes = [target_columns] if isinstance(target_columns, str) else list(target_columns)
    return ForeignKeyConstraint(
        ["snapshot_id", *locals_],
        [f"{target_table}.snapshot_id", *(f"{target_table}.{column}" for column in remotes)],
    )
