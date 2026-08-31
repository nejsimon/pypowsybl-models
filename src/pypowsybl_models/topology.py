from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from pypowsybl_models.base import Base, SnapshotScoped, snapshot_scoped_fk


class Substation(SnapshotScoped, Base):
    __tablename__ = "substation"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    tso: Mapped[str | None] = mapped_column("TSO")
    geo_tags: Mapped[str | None]
    country: Mapped[str | None]
    fictitious: Mapped[bool | None]


class VoltageLevel(SnapshotScoped, Base):
    __tablename__ = "voltage_level"
    __table_args__ = (snapshot_scoped_fk("substation_id", "substation"),)

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    substation_id: Mapped[str | None]
    nominal_v: Mapped[float | None]
    high_voltage_limit: Mapped[float | None]
    low_voltage_limit: Mapped[float | None]
    fictitious: Mapped[bool | None]
    topology_kind: Mapped[str | None]


class Bus(SnapshotScoped, Base):
    __tablename__ = "bus"
    __table_args__ = (snapshot_scoped_fk("voltage_level_id", "voltage_level"),)

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    voltage_level_id: Mapped[str | None]
    v_mag: Mapped[float | None]
    v_angle: Mapped[float | None]
    connected_component: Mapped[int | None]
    synchronous_component: Mapped[int | None]
    fictitious_p0: Mapped[float | None]
    fictitious_q0: Mapped[float | None]
    # Undocumented in pypowsybl's own docstring (unlike every other element
    # table's `fictitious`) - only surfaced by round-trip testing against
    # real data, see 05-models.md.
    fictitious: Mapped[bool | None]


class Switch(SnapshotScoped, Base):
    __tablename__ = "switch"
    __table_args__ = (snapshot_scoped_fk("voltage_level_id", "voltage_level"),)

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str | None]
    voltage_level_id: Mapped[str | None]
    bus_breaker_bus1_id: Mapped[str | None]
    bus_breaker_bus2_id: Mapped[str | None]
    node1: Mapped[str | None]
    node2: Mapped[str | None]
    kind: Mapped[str | None]
    open: Mapped[bool | None]
    retained: Mapped[bool | None]
    fictitious: Mapped[bool | None]


class BusbarSection(SnapshotScoped, Base):
    __tablename__ = "busbar_section"
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
    v: Mapped[float | None]
    angle: Mapped[float | None]
    connected: Mapped[bool | None]
    fictitious: Mapped[bool | None]
