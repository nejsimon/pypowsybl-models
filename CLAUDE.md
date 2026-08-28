# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Pre-implementation. The repository currently contains only `spec.md` — no code, no dependency manifest, no numbered spec files. Do not start writing models until numbered spec files (`01-*.md`, `02-*.md`, ...) have been generated from `spec.md` and confirmed with the user, per the global workflow rules.

## What this project is

SQLAlchemy models representing the output of pypowsybl's `Network` accessor methods (e.g. `get_buses()`, `get_lines()`, `get_generators()`), so that pandas DataFrames returned by pypowsybl can be persisted to a relational database.

## Target Network methods to model

One table (plus any supporting/deduplicated tables) per method:

- `get_buses`, `get_busbar_sections`, `get_lines`, `get_generators`, `get_loads`
- `get_2_windings_transformers`, `get_3_windings_transformers`
- `get_switches`, `get_substations`, `get_static_voltage_levels`
- `get_loading_limits`, `get_boundary_lines`
- `get_shunt_compensators`, `get_linear_shunt_compensator_sections`, `get_non_linear_shunt_compensator_sections`
- `get_phase_tap_changers`, `get_ratio_tap_changers`, `get_phase_tap_changers_steps`, `get_ratio_tap_changers_steps`
- `get_static_var_compensators`

## Data modeling requirements

- The pandas DataFrame index of each method's output is the table's primary key.
- `scenario_time` must be part of an index (it is not unique on its own) since queries will filter/sort on it frequently.
- Every table has a `snapshot_id` foreign key into a shared `network_snapshot` table.
- Before finalizing a table's columns, check the target method's stability in pypowsybl's history (git log/tags) — additions are fine, but historical signature changes or removals need to be called out explicitly.
- Look for id-based relations between the target methods' outputs (e.g. substation ↔ voltage level ↔ bus) and model them as foreign keys rather than duplicating identifying data.
- Where multiple tables share repeated data, break it out into its own table to deduplicate.

## Reference implementation

The modeling work should be checked against pypowsybl itself:

- Source: https://github.com/powsybl/pypowsybl (intended to be added as a git submodule per `spec.md`'s suggested workflow).
- The methods to model are defined on the `Network` class in `pypowsybl/network/impl/network.py`.

## Testing

- End-to-end testing needs a CGMES file loaded into pypowsybl; check upstream for usable mock/test data before assuming none exists.
- Model-level testing (schema, relations, constraints) can likely be done against SQLite without needing real pypowsybl data.
