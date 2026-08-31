from __future__ import annotations

import sqlite3
from collections.abc import Callable, Iterator
from datetime import UTC, datetime

import pypowsybl.network as pn
import pytest
from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session

from pypowsybl_models import (
    Base,
    BoundaryLine,
    Bus,
    BusbarSection,
    Generator,
    Line,
    LinearShuntCompensatorSection,
    Load,
    LoadingLimit,
    NetworkSnapshot,
    NonLinearShuntCompensatorSection,
    PhaseTapChanger,
    PhaseTapChangerStep,
    RatioTapChanger,
    RatioTapChangerStep,
    ShuntCompensator,
    StaticVarCompensator,
    Substation,
    Switch,
    ThreeWindingsTransformer,
    TwoWindingsTransformer,
    VoltageLevel,
)

# One entry per target method from spec.md, mapping the Network accessor to
# the model it should round-trip through - see 01-api-analysis.md/05-models.md.
TARGET_METHODS: list[tuple[str, type[Base]]] = [
    ("get_substations", Substation),
    ("get_voltage_levels", VoltageLevel),
    ("get_buses", Bus),
    ("get_switches", Switch),
    ("get_busbar_sections", BusbarSection),
    ("get_generators", Generator),
    ("get_loads", Load),
    ("get_shunt_compensators", ShuntCompensator),
    ("get_linear_shunt_compensator_sections", LinearShuntCompensatorSection),
    ("get_non_linear_shunt_compensator_sections", NonLinearShuntCompensatorSection),
    ("get_boundary_lines", BoundaryLine),
    ("get_static_var_compensators", StaticVarCompensator),
    ("get_lines", Line),
    ("get_2_windings_transformers", TwoWindingsTransformer),
    ("get_3_windings_transformers", ThreeWindingsTransformer),
    ("get_ratio_tap_changers", RatioTapChanger),
    ("get_phase_tap_changers", PhaseTapChanger),
    ("get_ratio_tap_changer_steps", RatioTapChangerStep),
    ("get_phase_tap_changer_steps", PhaseTapChangerStep),
    ("get_loading_limits", LoadingLimit),
]


@pytest.fixture
def engine() -> Iterator[Engine]:
    """Plain SQLite engine - foreign keys unenforced, SQLite's own default.

    Used by tests that load a single table in isolation (round-trip, multi-
    snapshot) without populating the tables it references.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def strict_engine() -> Iterator[Engine]:
    """SQLite engine with foreign-key enforcement turned on.

    Used by tests that load a full parent/child chain and want the database
    itself to prove the relations from 02-schema-design.md hold.
    """
    engine = create_engine("sqlite:///:memory:")

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection: sqlite3.Connection, _connection_record: object) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine: Engine) -> Iterator[Session]:
    with Session(engine) as session:
        yield session


@pytest.fixture
def strict_session(strict_engine: Engine) -> Iterator[Session]:
    with Session(strict_engine) as session:
        yield session


@pytest.fixture
def make_snapshot(session: Session) -> Callable[[datetime | None], NetworkSnapshot]:
    def _make(scenario_time: datetime | None = None) -> NetworkSnapshot:
        snapshot = NetworkSnapshot(scenario_time=scenario_time or datetime(2026, 1, 1, tzinfo=UTC))
        session.add(snapshot)
        session.flush()
        return snapshot

    return _make


@pytest.fixture(scope="session")
def eurostag_network() -> pn.Network:
    return pn.create_eurostag_tutorial_example1_network()


@pytest.fixture(scope="session")
def four_substations_network() -> pn.Network:
    return pn.create_four_substations_node_breaker_network()


@pytest.fixture(scope="session")
def micro_grid_be_network() -> pn.Network:
    return pn.create_micro_grid_be_network()


FIXTURE_NETWORK_FIXTURES = ["eurostag_network", "four_substations_network", "micro_grid_be_network"]


@pytest.fixture(params=FIXTURE_NETWORK_FIXTURES)
def any_network(request: pytest.FixtureRequest) -> pn.Network:
    return request.getfixturevalue(request.param)
