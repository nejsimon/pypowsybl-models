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
