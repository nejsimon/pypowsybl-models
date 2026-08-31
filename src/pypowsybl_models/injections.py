from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from pypowsybl_models.base import Base, SnapshotScoped, snapshot_scoped_fk


class Generator(SnapshotScoped, Base):
    __tablename__ = "generator"
    __table_args__ = (
        snapshot_scoped_fk("voltage_level_id", "voltage_level"),
        snapshot_scoped_fk("bus_id", "bus"),
        snapshot_scoped_fk("regulated_bus_id", "bus"),
    )

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    voltage_level_id: Mapped[str | None]
    bus_id: Mapped[str | None]
    bus_breaker_bus_id: Mapped[str | None]
    node: Mapped[str | None]
    regulated_bus_id: Mapped[str | None]
    regulated_bus_breaker_bus_id: Mapped[str | None]
    # Open-ended polymorphic reference to any network element - no FK, see 02-schema-design.md.
    regulated_element_id: Mapped[str | None]
    energy_source: Mapped[str | None]
    reactive_limits_kind: Mapped[str | None]
    target_p: Mapped[float | None]
    max_p: Mapped[float | None]
    min_p: Mapped[float | None]
    max_q: Mapped[float | None]
    min_q: Mapped[float | None]
    max_q_at_target_p: Mapped[float | None]
    min_q_at_target_p: Mapped[float | None]
    max_q_at_p: Mapped[float | None]
    min_q_at_p: Mapped[float | None]
    rated_s: Mapped[float | None]
    target_v: Mapped[float | None]
    equivalent_local_target_v: Mapped[float | None]
    target_q: Mapped[float | None]
    p: Mapped[float | None]
    q: Mapped[float | None]
    i: Mapped[float | None]
    voltage_regulator_on: Mapped[bool | None]
    connected: Mapped[bool | None]
    condenser: Mapped[bool | None]
    fictitious: Mapped[bool | None]


class Load(SnapshotScoped, Base):
    __tablename__ = "load"
    __table_args__ = (
        snapshot_scoped_fk("voltage_level_id", "voltage_level"),
        snapshot_scoped_fk("bus_id", "bus"),
    )

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    voltage_level_id: Mapped[str | None]
    bus_id: Mapped[str | None]
    bus_breaker_bus_id: Mapped[str | None]
    node: Mapped[str | None]
    type: Mapped[str | None]
    p0: Mapped[float | None]
    q0: Mapped[float | None]
    p: Mapped[float | None]
    q: Mapped[float | None]
    i: Mapped[float | None]
    connected: Mapped[bool | None]
    fictitious: Mapped[bool | None]


class ShuntCompensator(SnapshotScoped, Base):
    __tablename__ = "shunt_compensator"
    __table_args__ = (
        snapshot_scoped_fk("voltage_level_id", "voltage_level"),
        snapshot_scoped_fk("bus_id", "bus"),
    )

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    voltage_level_id: Mapped[str | None]
    bus_id: Mapped[str | None]
    bus_breaker_bus_id: Mapped[str | None]
    node: Mapped[str | None]
    model_type: Mapped[str | None]
    max_section_count: Mapped[int | None]
    section_count: Mapped[int | None]
    solved_section_count: Mapped[float | None]
    p: Mapped[float | None]
    q: Mapped[float | None]
    i: Mapped[float | None]
    connected: Mapped[bool | None]
    fictitious: Mapped[bool | None]


class LinearShuntCompensatorSection(SnapshotScoped, Base):
    __tablename__ = "linear_shunt_compensator_section"
    __table_args__ = (snapshot_scoped_fk("id", "shunt_compensator"),)

    id: Mapped[str] = mapped_column(primary_key=True)
    g_per_section: Mapped[float | None]
    b_per_section: Mapped[float | None]
    max_section_count: Mapped[int | None]


class NonLinearShuntCompensatorSection(SnapshotScoped, Base):
    __tablename__ = "non_linear_shunt_compensator_section"
    __table_args__ = (snapshot_scoped_fk("id", "shunt_compensator"),)

    id: Mapped[str] = mapped_column(primary_key=True)
    section: Mapped[int] = mapped_column(primary_key=True)
    g: Mapped[float | None]
    b: Mapped[float | None]


class BoundaryLine(SnapshotScoped, Base):
    __tablename__ = "boundary_line"
    __table_args__ = (
        snapshot_scoped_fk("voltage_level_id", "voltage_level"),
        snapshot_scoped_fk("bus_id", "bus"),
    )

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    voltage_level_id: Mapped[str | None]
    bus_id: Mapped[str | None]
    bus_breaker_bus_id: Mapped[str | None]
    node: Mapped[str | None]
    pairing_key: Mapped[str | None]
    ucte_xnode_code: Mapped[str | None]
    # Not one of the 20 target tables, so no FK - see 05-models.md.
    tie_line_id: Mapped[str | None]
    r: Mapped[float | None]
    x: Mapped[float | None]
    g: Mapped[float | None]
    b: Mapped[float | None]
    p0: Mapped[float | None]
    q0: Mapped[float | None]
    p: Mapped[float | None]
    q: Mapped[float | None]
    i: Mapped[float | None]
    boundary_p: Mapped[float | None]
    boundary_q: Mapped[float | None]
    boundary_i: Mapped[float | None]
    boundary_v_mag: Mapped[float | None]
    boundary_v_angle: Mapped[float | None]
    connected: Mapped[bool | None]
    fictitious: Mapped[bool | None]
    paired: Mapped[bool | None]


class StaticVarCompensator(SnapshotScoped, Base):
    __tablename__ = "static_var_compensator"
    __table_args__ = (
        snapshot_scoped_fk("voltage_level_id", "voltage_level"),
        snapshot_scoped_fk("bus_id", "bus"),
        snapshot_scoped_fk("regulated_bus_id", "bus"),
    )

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    voltage_level_id: Mapped[str | None]
    bus_id: Mapped[str | None]
    bus_breaker_bus_id: Mapped[str | None]
    node: Mapped[str | None]
    regulated_bus_id: Mapped[str | None]
    regulated_bus_breaker_bus_id: Mapped[str | None]
    # Open-ended polymorphic reference to any network element - no FK, see 02-schema-design.md.
    regulated_element_id: Mapped[str | None]
    regulation_mode: Mapped[str | None]
    b_min: Mapped[float | None]
    b_max: Mapped[float | None]
    target_v: Mapped[float | None]
    target_q: Mapped[float | None]
    p: Mapped[float | None]
    q: Mapped[float | None]
    i: Mapped[float | None]
    connected: Mapped[bool | None]
    fictitious: Mapped[bool | None]
