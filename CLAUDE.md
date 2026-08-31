# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

SQLAlchemy models representing the output of pypowsybl's `Network` accessor methods (e.g. `get_buses()`, `get_lines()`, `get_generators()`), so that pandas DataFrames returned by pypowsybl can be persisted to a relational database as versioned snapshots.

## Project status

Implemented: 21 tables (`network_snapshot` plus one per target method), a generic DataFrame-to-ORM loader, and a passing test suite. The numbered spec files are still the source of truth for *why* the schema looks the way it does — read them before changing a table's columns or relations, don't just infer intent from the code:

- `spec.md` — the original brief.
- `01-api-analysis.md` — corrections to spec.md's method names, API stability findings (notably: `get_boundary_lines` is a 2026 rename of `get_dangling_lines`; `get_loading_limits` supersedes deprecated `get_operational_limits`), column/index inventory from pypowsybl's docstrings.
- `02-schema-design.md` — the `network_snapshot` + composite-PK convention, table list, relations, polymorphic-reference decisions, dedup assessment.
- `03-testing-strategy.md` — the fixture/test strategy actually implemented in `tests/`.
- `04-project-setup.md` — tooling conventions (`uv`/`ruff`/`ty`), repo layout, why the submodule isn't the runtime dependency.
- `05-models.md` — the column-by-column table definitions, including a handful of columns (`name` on most tables, `bus.fictitious`, `three_windings_transformer.v`/`angle`) that pypowsybl's own docstrings don't mention and were only found by running the round-trip tests against real fixture data.

## Commands

```
uv sync                              # install/update the environment
uv run pytest                        # run the test suite
uv run pytest tests/test_round_trip.py -k get_lines   # a single test
uv run ruff check --fix src/ tests/  # lint
uv run ruff format src/ tests/       # format
uv run ty check src/ tests/          # type-check
uv run pre-commit run --all-files    # everything pre-commit enforces
```

`ruff`/`ty` are scoped to `src/`/`tests/` explicitly (and excluded from `vendor/` in `pyproject.toml`) — the vendored `pypowsybl` submodule has its own tooling and its own (unrelated) test failures if you try to import extras it doesn't have installed.

## Architecture

- `src/pypowsybl_models/base.py` — the declarative `Base`, the `SnapshotScoped` mixin (`snapshot_id` + `scenario_time` columns every table gets), and `snapshot_scoped_fk()`, a helper that builds a `ForeignKeyConstraint` scoped by `snapshot_id` in addition to the natural column(s) — this is how every relation in `02-schema-design.md` is actually implemented.
- `src/pypowsybl_models/snapshot.py`, `topology.py`, `injections.py`, `branches.py`, `tap_changers.py`, `limits.py` — the 21 table models, grouped by domain area per `04-project-setup.md`'s layout.
- `src/pypowsybl_models/load.py` — `load_dataframe(session, model, snapshot_id, scenario_time, df)`, the generic loader every table uses to turn a `Network.get_*()` DataFrame into ORM rows. It lowercases column names to match attribute names, converts NaN to NULL, and **silently drops any DataFrame column that isn't one of the model's own attributes** — this is intentional, not a bug: CGMES-sourced networks add dynamic `CGMES.*` per-element extension properties that aren't part of this schema's fixed tables (see `01-api-analysis.md`).
- None of these models declare ORM `relationship()`s — only table-level `ForeignKeyConstraint`s. This means loading a full network graph requires `session.flush()` between tables, parents before children (substation → voltage_level → bus → everything else); SQLAlchemy will not reliably reorder composite-FK inserts across tables within a single flush on its own. See the docstring in `load.py` and `tests/test_relations.py` for the pattern.
- `tests/conftest.py` — `TARGET_METHODS` (the method-to-model mapping used by the parametrized round-trip test), the `engine`/`session` fixtures (foreign keys off, SQLite's default — for tests that load one table in isolation) vs. `strict_engine`/`strict_session` (foreign keys on — for tests that load a full parent/child chain and want the database to prove the relations hold), and the fixture networks (`eurostag_network`, `four_substations_network`, `micro_grid_be_network`) built from pypowsybl's own factory functions — no external CGMES file is needed.

## Reference implementation

`pypowsybl` is checked out as a git submodule at `vendor/pypowsybl/` (full history, not shallow) — used purely as a reference for reading the actual `Network` API and its git history; it is not the runtime dependency (see `04-project-setup.md`). The methods to model are defined on the `Network` class in `vendor/pypowsybl/pypowsybl/network/impl/network.py`. It was deliberately placed under `vendor/` rather than at the repo root: a top-level `pypowsybl/` directory shadows the installed `pypowsybl` package on `sys.path` whenever the repo root ends up on the path (e.g. `python -c`, some pytest invocations), causing confusing `ImportError`s.
