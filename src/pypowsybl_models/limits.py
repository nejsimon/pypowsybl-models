"""Loading limits.

`element_id`/`element_type` is a closed 4-way polymorphic reference (LINE,
TWO_WINDINGS_TRANSFORMER, THREE_WINDINGS_TRANSFORMER, BOUNDARY_LINE) - stored
as plain columns with no DB-level FK, for consistency with the open-ended
polymorphic references elsewhere in this schema. See 02-schema-design.md.

`side` and `group_name` are part of the primary key (per pypowsybl's own
index, see 01-api-analysis.md) and therefore can never be NULL at the DB
level; normalize them to an empty string where pypowsybl would otherwise
return an empty/absent value, the same convention used for tap-changer `side`
in tap_changers.py.
"""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from pypowsybl_models.base import Base, SnapshotScoped


class LoadingLimit(SnapshotScoped, Base):
    __tablename__ = "loading_limit"

    element_id: Mapped[str] = mapped_column(primary_key=True)
    element_type: Mapped[str]
    side: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(primary_key=True)
    acceptable_duration: Mapped[int] = mapped_column(primary_key=True)
    group_name: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    value: Mapped[float | None]
    fictitious: Mapped[bool | None]
    selected: Mapped[bool | None]
