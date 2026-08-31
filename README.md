# pypowsybl-models

SQLAlchemy models for [pypowsybl](https://github.com/powsybl/pypowsybl) `Network` snapshots. Each of pypowsybl's `Network.get_*()` accessor methods (buses, lines, generators, transformers, tap changers, loading limits, ...) has a matching table here, keyed so that the same network can be persisted repeatedly over time as a series of independent snapshots. See `01-api-analysis.md` through `05-models.md` for the design rationale, and `CLAUDE.md` for a map of the codebase.

## Requirements

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/)

## Using this package in another project

Build a wheel and point your other project's dependency manager at it:

```
uv build                              # produces dist/pypowsybl_models-<version>-py3-none-any.whl
```

Then, from the consuming project:

```
uv add /path/to/pypowsybl-models/dist/pypowsybl_models-<version>-py3-none-any.whl
# or, with plain pip:
pip install /path/to/pypowsybl-models/dist/pypowsybl_models-<version>-py3-none-any.whl
```

Once this repository has a remote, the same wheel can be installed directly from it without a local build step (`uv add git+<repository-url>` / `pip install git+<repository-url>`).

```python
from datetime import UTC, datetime

import pypowsybl.network as pn
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from pypowsybl_models import Base, Generator, NetworkSnapshot, load_dataframe

engine = create_engine("sqlite:///network.db")
Base.metadata.create_all(engine)

network = pn.create_eurostag_tutorial_example1_network()

with Session(engine) as session:
    snapshot = NetworkSnapshot(scenario_time=datetime.now(UTC))
    session.add(snapshot)
    session.flush()  # need snapshot.id before loading rows

    load_dataframe(session, Generator, snapshot.id, snapshot.scenario_time, network.get_generators(all_attributes=True))
    session.commit()
```

Loading several tables for the same snapshot requires a `session.flush()` between each, parents before children (substation → voltage_level → bus → everything else) — see the docstring in `src/pypowsybl_models/load.py` for why.

## Development

Clone with the submodule (a reference copy of pypowsybl's source, used only to check this schema against the real `Network` API — see `04-project-setup.md`; it is not a runtime dependency):

```
git clone --recurse-submodules <repository-url>
# or, if already cloned:
git submodule update --init
```

Install the environment:

```
uv sync
```

Run the test suite (against in-memory SQLite, using pypowsybl's own built-in fixture networks — no external CGMES file needed, see `03-testing-strategy.md`):

```
uv run pytest
uv run pytest tests/test_round_trip.py -k get_lines   # a single test
```

Lint, format, and type-check:

```
uv run ruff check --fix src/ tests/
uv run ruff format src/ tests/
uv run ty check src/ tests/
```

Install the git hook so all of the above run automatically on commit:

```
uv run pre-commit install
uv run pre-commit run --all-files   # run it on demand, e.g. after installing
```

Build a wheel/sdist:

```
uv build
```

## Scope and known gaps

### Undocumented columns found by testing

pypowsybl's own docstrings aren't a complete account of what a DataFrame actually contains. Running the round-trip tests against real fixture data (`03-testing-strategy.md`) turned up columns none of the target methods' docstrings mention:

- `name` is present on almost every table but undocumented in pypowsybl's own docstrings.
- `bus.fictitious` and a 3-windings-transformer star-point `v`/`angle` — likewise undocumented, only found by testing.
- CGMES-sourced networks emit dynamic `CGMES.*` extension properties outside the fixed schema; the loader now drops unknown columns instead of crashing (see `src/pypowsybl_models/load.py`).

### `Network` methods not modeled

This schema covers the 20 methods listed in `spec.md`. A full survey of every `get_*` method on `Network` that returns a DataFrame turned up more that aren't modeled here (beyond `get_dangling_lines`/`get_operational_limits`, which are just deprecated aliases of `get_boundary_lines`/`get_loading_limits`, already covered — see `01-api-analysis.md`):

**Equipment types, same category as what's already modeled:**
- `get_batteries` — battery storage, sibling to generators/loads
- `get_grounds` — grounding connections
- `get_hvdc_lines` — HVDC lines (parallel to AC `get_lines`)
- `get_lcc_converter_stations` / `get_vsc_converter_stations` — HVDC converter stations, referenced by `get_hvdc_lines`
- `get_tie_lines` — pairs of boundary lines merged into one; already referenced indirectly via `boundary_line.tie_line_id` but not modeled itself
- `get_boundary_lines_generation` (+ deprecated `get_dangling_lines_generation`) — the equivalent-generator part of a boundary line, split out like tap-changer/shunt sections are

**Directly fills a gap in what's already modeled:**
- `get_reactive_capability_curve_points` — the `generator` model's `max_q`/`min_q` only apply "if `reactive_limits_kind` is MIN_MAX"; when it's `CURVE` instead, the actual reactive limits live in this table. Same applies to `static_var_compensator`'s reactive limits.

**Limits, same category as `get_loading_limits`:**
- `get_voltage_angle_limits` — angle-difference limits between two elements

**A newer, separate DC grid model** (distinct from the HVDC-line model above — possibly overlapping/superseding it, worth checking pypowsybl's docs/version history before deciding which one to model):
- `get_dc_lines`, `get_dc_nodes`, `get_dc_buses`, `get_dc_switches`, `get_dc_grounds`, `get_voltage_source_converters`

**Grouping/control-area concept, no current equivalent:**
- `get_areas`, `get_areas_voltage_levels`, `get_areas_boundaries`

**Computed/enrichment data:**
- `get_switch_flows` — switches currently have no `p`/`q`/`i` columns (unlike every other element); this is where that data lives
- `get_elements_properties`, `get_aliases` — generic key/value metadata and alternate IDs per element

**Generic/derived views** — probably not worth their own table, just unions of tables already modeled:
- `get_identifiables`, `get_injections`, `get_branches`, `get_terminals`, `get_extensions`/`get_extension`
