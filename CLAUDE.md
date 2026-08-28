# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Pre-implementation. The full plan has been written up as numbered spec files (`01-api-analysis.md` through `05-models.md`) — read those before touching code, they are the source of truth for table/column decisions, not this file. Several open decisions are flagged at the end of `05-models.md` and need confirming before implementation starts, per the global workflow rules. No code or dependency manifest exists yet.

- `01-api-analysis.md` — corrections to spec.md's method names, API stability findings (notably: `get_boundary_lines` is a 2026 rename of `get_dangling_lines`), column/index inventory.
- `02-schema-design.md` — the `network_snapshot` + composite-PK convention, table list, relations, polymorphic-reference decisions, dedup assessment.
- `03-testing-strategy.md` — uses pypowsybl's built-in network factories, no external CGMES file needed.
- `04-project-setup.md` — `uv`/`ruff`/`mypy` setup, repo layout, submodule-is-reference-only note.
- `05-models.md` — the column-by-column table definitions to implement.

## What this project is

SQLAlchemy models representing the output of pypowsybl's `Network` accessor methods (e.g. `get_buses()`, `get_lines()`, `get_generators()`), so that pandas DataFrames returned by pypowsybl can be persisted to a relational database.

## Target Network methods to model

One table (plus any supporting/deduplicated tables) per method:

- `get_buses`, `get_busbar_sections`, `get_lines`, `get_generators`, `get_loads`
- `get_2_windings_transformers`, `get_3_windings_transformers`
- `get_switches`, `get_substations`, `get_voltage_levels`
- `get_loading_limits`, `get_boundary_lines`
- `get_shunt_compensators`, `get_linear_shunt_compensator_sections`, `get_non_linear_shunt_compensator_sections`
- `get_phase_tap_changers`, `get_ratio_tap_changers`, `get_phase_tap_changer_steps`, `get_ratio_tap_changer_steps`
- `get_static_var_compensators`

## Data modeling requirements

- The pandas DataFrame index of each method's output is the table's primary key.
- `scenario_time` must be part of an index (it is not unique on its own) since queries will filter/sort on it frequently.
- Every table has a `snapshot_id` foreign key into a shared `network_snapshot` table.
- Before finalizing a table's columns, check the target method's stability in pypowsybl's history (git log/tags) — additions are fine, but historical signature changes or removals need to be called out explicitly.
- Look for id-based relations between the target methods' outputs (e.g. substation ↔ voltage level ↔ bus) and model them as foreign keys rather than duplicating identifying data.
- Where multiple tables share repeated data, break it out into its own table to deduplicate.

## Reference implementation

`pypowsybl` is checked out as a git submodule at `pypowsybl/` (full history, not shallow) — used purely as a reference for reading the actual `Network` API and its git history; it is not the runtime dependency (see `04-project-setup.md`). The methods to model are defined on the `Network` class in `pypowsybl/pypowsybl/network/impl/network.py`.

## Testing

No CGMES file needs to be sourced — `03-testing-strategy.md` covers pypowsybl's own bundled fixtures and in-memory network factories, and SQLite is sufficient for all schema/relation testing.
