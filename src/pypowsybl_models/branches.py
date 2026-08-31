from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from pypowsybl_models.base import Base, SnapshotScoped, snapshot_scoped_fk


class Line(SnapshotScoped, Base):
    __tablename__ = "line"
    __table_args__ = (
        snapshot_scoped_fk("voltage_level1_id", "voltage_level"),
        snapshot_scoped_fk("voltage_level2_id", "voltage_level"),
        snapshot_scoped_fk("bus1_id", "bus"),
        snapshot_scoped_fk("bus2_id", "bus"),
    )

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    voltage_level1_id: Mapped[str | None]
    voltage_level2_id: Mapped[str | None]
    bus1_id: Mapped[str | None]
    bus2_id: Mapped[str | None]
    bus_breaker_bus1_id: Mapped[str | None]
    bus_breaker_bus2_id: Mapped[str | None]
    node1: Mapped[str | None]
    node2: Mapped[str | None]
    selected_limits_group_1: Mapped[str | None]
    selected_limits_group_2: Mapped[str | None]
    r: Mapped[float | None]
    x: Mapped[float | None]
    g1: Mapped[float | None]
    b1: Mapped[float | None]
    g2: Mapped[float | None]
    b2: Mapped[float | None]
    p1: Mapped[float | None]
    q1: Mapped[float | None]
    i1: Mapped[float | None]
    p2: Mapped[float | None]
    q2: Mapped[float | None]
    i2: Mapped[float | None]
    connected1: Mapped[bool | None]
    connected2: Mapped[bool | None]
    fictitious: Mapped[bool | None]


class TwoWindingsTransformer(SnapshotScoped, Base):
    __tablename__ = "two_windings_transformer"
    __table_args__ = (
        snapshot_scoped_fk("voltage_level1_id", "voltage_level"),
        snapshot_scoped_fk("voltage_level2_id", "voltage_level"),
        snapshot_scoped_fk("bus1_id", "bus"),
        snapshot_scoped_fk("bus2_id", "bus"),
    )

    # Also functions as an informal reference to ratio_tap_changer.id /
    # phase_tap_changer.id - no DB FK, see 02-schema-design.md.
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    voltage_level1_id: Mapped[str | None]
    voltage_level2_id: Mapped[str | None]
    bus1_id: Mapped[str | None]
    bus2_id: Mapped[str | None]
    bus_breaker_bus1_id: Mapped[str | None]
    bus_breaker_bus2_id: Mapped[str | None]
    node1: Mapped[str | None]
    node2: Mapped[str | None]
    selected_limits_group_1: Mapped[str | None]
    selected_limits_group_2: Mapped[str | None]
    r: Mapped[float | None]
    x: Mapped[float | None]
    b: Mapped[float | None]
    g: Mapped[float | None]
    rated_u1: Mapped[float | None]
    rated_u2: Mapped[float | None]
    rated_s: Mapped[float | None]
    p1: Mapped[float | None]
    q1: Mapped[float | None]
    i1: Mapped[float | None]
    p2: Mapped[float | None]
    q2: Mapped[float | None]
    i2: Mapped[float | None]
    rho: Mapped[float | None]
    alpha: Mapped[float | None]
    r_at_current_tap: Mapped[float | None]
    x_at_current_tap: Mapped[float | None]
    g_at_current_tap: Mapped[float | None]
    b_at_current_tap: Mapped[float | None]
    connected1: Mapped[bool | None]
    connected2: Mapped[bool | None]
    fictitious: Mapped[bool | None]


class ThreeWindingsTransformer(SnapshotScoped, Base):
    __tablename__ = "three_windings_transformer"
    __table_args__ = (
        snapshot_scoped_fk("voltage_level1_id", "voltage_level"),
        snapshot_scoped_fk("voltage_level2_id", "voltage_level"),
        snapshot_scoped_fk("voltage_level3_id", "voltage_level"),
        snapshot_scoped_fk("bus1_id", "bus"),
        snapshot_scoped_fk("bus2_id", "bus"),
        snapshot_scoped_fk("bus3_id", "bus"),
    )

    # Also functions as an informal reference to ratio_tap_changer.id /
    # phase_tap_changer.id - no DB FK, see 02-schema-design.md.
    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    rated_u0: Mapped[float | None]
    fictitious: Mapped[bool | None]
    # Star-point voltage magnitude/angle - undocumented in pypowsybl's own
    # docstring, only surfaced by round-trip testing, see 05-models.md.
    v: Mapped[float | None]
    angle: Mapped[float | None]

    voltage_level1_id: Mapped[str | None]
    bus1_id: Mapped[str | None]
    bus_breaker_bus1_id: Mapped[str | None]
    node1: Mapped[str | None]
    selected_limits_group_1: Mapped[str | None]
    r1: Mapped[float | None]
    x1: Mapped[float | None]
    b1: Mapped[float | None]
    g1: Mapped[float | None]
    rated_u1: Mapped[float | None]
    rated_s1: Mapped[float | None]
    ratio_tap_position1: Mapped[int | None]
    phase_tap_position1: Mapped[int | None]
    p1: Mapped[float | None]
    q1: Mapped[float | None]
    i1: Mapped[float | None]
    rho1: Mapped[float | None]
    alpha1: Mapped[float | None]
    r1_at_current_tap: Mapped[float | None]
    x1_at_current_tap: Mapped[float | None]
    g1_at_current_tap: Mapped[float | None]
    b1_at_current_tap: Mapped[float | None]
    connected1: Mapped[bool | None]

    voltage_level2_id: Mapped[str | None]
    bus2_id: Mapped[str | None]
    bus_breaker_bus2_id: Mapped[str | None]
    node2: Mapped[str | None]
    selected_limits_group_2: Mapped[str | None]
    r2: Mapped[float | None]
    x2: Mapped[float | None]
    b2: Mapped[float | None]
    g2: Mapped[float | None]
    rated_u2: Mapped[float | None]
    rated_s2: Mapped[float | None]
    ratio_tap_position2: Mapped[int | None]
    phase_tap_position2: Mapped[int | None]
    p2: Mapped[float | None]
    q2: Mapped[float | None]
    i2: Mapped[float | None]
    rho2: Mapped[float | None]
    alpha2: Mapped[float | None]
    r2_at_current_tap: Mapped[float | None]
    x2_at_current_tap: Mapped[float | None]
    g2_at_current_tap: Mapped[float | None]
    b2_at_current_tap: Mapped[float | None]
    connected2: Mapped[bool | None]

    voltage_level3_id: Mapped[str | None]
    bus3_id: Mapped[str | None]
    bus_breaker_bus3_id: Mapped[str | None]
    node3: Mapped[str | None]
    selected_limits_group_3: Mapped[str | None]
    r3: Mapped[float | None]
    x3: Mapped[float | None]
    b3: Mapped[float | None]
    g3: Mapped[float | None]
    rated_u3: Mapped[float | None]
    rated_s3: Mapped[float | None]
    ratio_tap_position3: Mapped[int | None]
    phase_tap_position3: Mapped[int | None]
    p3: Mapped[float | None]
    q3: Mapped[float | None]
    i3: Mapped[float | None]
    rho3: Mapped[float | None]
    alpha3: Mapped[float | None]
    r3_at_current_tap: Mapped[float | None]
    x3_at_current_tap: Mapped[float | None]
    g3_at_current_tap: Mapped[float | None]
    b3_at_current_tap: Mapped[float | None]
    connected3: Mapped[bool | None]
