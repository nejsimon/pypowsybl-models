# 04 — Project setup

Standard Python project conventions per the user's global instructions, applied to this repo.

## Dependency on pypowsybl: submodule is reference-only

The `pypowsybl/` submodule (added in this repo's git history) contains C++ (`cpp/`) and Java (`java/`) sources and needs `cmake`/`pybind11`/a JDK to build from source (per its own `requirements.txt`/`setup.cfg`). It is **not** meant to be installed as the runtime dependency — it exists so this repo's models can be checked against the actual `Network` API and its history (`01-api-analysis.md`).

The actual runtime dependency is the published `pypowsybl` package from PyPI (requires Python >=3.10, matching the submodule's `setup.cfg`). Test fixtures (`03-testing-strategy.md`) use the *installed* package's factory functions — the submodule is only consulted for source-reading, not imported.

## Tooling

- Virtual environment: `.venv/`, managed with `uv` (`uv sync`, `uv run`).
- Dependencies: `pypowsybl`, `sqlalchemy`, `pandas` as runtime deps; `pytest` as a dev dependency for `03-testing-strategy.md`.
- Linting: `ruff`, enforced via a pre-commit hook.
- Type checking: full annotations, enforced via a pre-commit hook using `ty` (per the user's global Python conventions — `pypowsybl` itself uses `mypy` for its own CI, but that's their choice for their codebase, not ours).
- Testing: `pytest`, against SQLite (`03-testing-strategy.md`) — no external DB server dependency.

## Repository layout (proposed)

```
pyproject.toml
src/
  pypowsybl_models/
    __init__.py
    base.py          # SQLAlchemy declarative base, shared conventions (snapshot_id/scenario_time columns)
    snapshot.py       # network_snapshot model
    <one module per entity group, e.g. topology.py (substation/voltage_level/bus/busbar_section),
     injections.py (generator/load/shunt_compensator/*_section/static_var_compensator/boundary_line),
     branches.py (line/two_windings_transformer/three_windings_transformer),
     tap_changers.py (ratio/phase tap changer + step tables),
     limits.py (loading_limit)>
tests/
  conftest.py         # shared fixtures: in-memory sqlite engine, fixture networks from pypowsybl
  test_<entity>.py    # one file per entity group, per 03-testing-strategy.md
```

Grouping into a handful of modules by domain area (rather than 20 one-model files, or one giant file) keeps related FKs colocated without becoming unwieldy — adjust the grouping above if a different split reads better once the models are actually being written.
