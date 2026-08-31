"""Ratio/phase tap changers and their steps.

`side` is added to the primary key of all four tables here, even though it is
not part of pypowsybl's own pandas index - a 3-windings transformer can carry
a tap changer on more than one leg, sharing the same `id` and distinguished
only by `side`. Normalized to an empty string (never NULL) for the
2-windings-transformer case, so it stays usable as a key component. See the
caveat in 01-api-analysis.md and the validation step in 03-testing-strategy.md.

`id` is the owning transformer's id, but that transformer may live in either
`two_windings_transformer` or `three_windings_transformer` - no DB-level FK
is possible without checking both tables, so it is stored as a plain column.
See 02-schema-design.md.
"""

from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from pypowsybl_models.base import Base, SnapshotScoped, snapshot_scoped_fk


class RatioTapChanger(SnapshotScoped, Base):
    __tablename__ = "ratio_tap_changer"
    __table_args__ = (snapshot_scoped_fk("regulating_bus_id", "bus"),)

    id: Mapped[str] = mapped_column(primary_key=True)
    side: Mapped[str] = mapped_column(primary_key=True)
    regulating_bus_id: Mapped[str | None]
    regulation_mode: Mapped[str | None]
    tap: Mapped[int | None]
    low_tap: Mapped[int | None]
    high_tap: Mapped[int | None]
    step_count: Mapped[int | None]
    solved_tap_position: Mapped[float | None]
    target_v: Mapped[float | None]
    target_deadband: Mapped[float | None]
    regulation_value: Mapped[float | None]
    regulated_side: Mapped[str | None]
    oltc: Mapped[bool | None]
    regulating: Mapped[bool | None]


class PhaseTapChanger(SnapshotScoped, Base):
    __tablename__ = "phase_tap_changer"
    __table_args__ = (snapshot_scoped_fk("regulating_bus_id", "bus"),)

    id: Mapped[str] = mapped_column(primary_key=True)
    side: Mapped[str] = mapped_column(primary_key=True)
    regulating_bus_id: Mapped[str | None]
    regulation_mode: Mapped[str | None]
    tap: Mapped[int | None]
    low_tap: Mapped[int | None]
    high_tap: Mapped[int | None]
    step_count: Mapped[int | None]
    solved_tap_position: Mapped[float | None]
    regulation_value: Mapped[float | None]
    target_deadband: Mapped[float | None]
    regulated_side: Mapped[str | None]
    oltc: Mapped[bool | None]
    regulating: Mapped[bool | None]


class RatioTapChangerStep(SnapshotScoped, Base):
    __tablename__ = "ratio_tap_changer_step"
    __table_args__ = (snapshot_scoped_fk(["id", "side"], "ratio_tap_changer", ["id", "side"]),)

    id: Mapped[str] = mapped_column(primary_key=True)
    side: Mapped[str] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(primary_key=True)
    rho: Mapped[float | None]
    r: Mapped[float | None]
    x: Mapped[float | None]
    g: Mapped[float | None]
    b: Mapped[float | None]


class PhaseTapChangerStep(SnapshotScoped, Base):
    __tablename__ = "phase_tap_changer_step"
    __table_args__ = (snapshot_scoped_fk(["id", "side"], "phase_tap_changer", ["id", "side"]),)

    id: Mapped[str] = mapped_column(primary_key=True)
    side: Mapped[str] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(primary_key=True)
    rho: Mapped[float | None]
    alpha: Mapped[float | None]
    r: Mapped[float | None]
    x: Mapped[float | None]
    g: Mapped[float | None]
    b: Mapped[float | None]
