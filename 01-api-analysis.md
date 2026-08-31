# 01 — pypowsybl `Network` API analysis

Analysis of the `Network` class in `vendor/pypowsybl/pypowsybl/network/impl/network.py` (submodule, full history available), covering the 20 target methods from `spec.md`.

## Corrections to the method list in spec.md

Three method names in `spec.md` did not match the actual pypowsybl API and have been corrected there:

| spec.md said | Actual method | Note |
|---|---|---|
| `get_static_voltage_levels` | `get_voltage_levels` | `get_static_voltage_levels` never existed anywhere in pypowsybl's git history. |
| `get_phase_tap_changers_steps` | `get_phase_tap_changer_steps` | Singular "changer", not "changers". Confirmed via `git log -S` across full history — never existed as plural. |
| `get_ratio_tap_changers_steps` | `get_ratio_tap_changer_steps` | Same as above. |

## API stability findings (per suggested workflow step 3)

Additions across versions are not itemized here (expected and harmless). Two breaking renames are notable and directly affect naming choices in this schema:

- **`get_boundary_lines` is a rename of `get_dangling_lines`.** The old name (`get_dangling_lines`) existed from the earliest refactor (`6b0ad13e`, "Network elements access refactoring #128") through most of the project's life, and was renamed to `get_boundary_lines` in commit `8c7e511b` ("Complete integration of dependencies 2026.0.0 #1183), dated 2026-04-03 — a few months before this analysis. `get_dangling_lines` no longer exists as a callable method (only an unrelated deprecated `with_dangling_lines` boolean kwarg survives on other methods, aliasing to `with_boundary_lines`). **Decision: model this table as `boundary_line`, matching the current name**, since it is what's live in the API today.
- **`get_loading_limits` supersedes `get_operational_limits`.** `get_operational_limits` still exists in the current source but raises `DeprecationWarning` ("use get_loading_limits instead") — introduced by commit `481205e4`. `get_loading_limits` is the one named in `spec.md` and is the correct, forward-looking choice.

No other target method has been renamed or removed historically; all have existed with their current names since the `ee97de90` "refactor api (#641)" restructuring or earlier.

## Column and index inventory

For each target method: the pandas index (→ candidate primary key components) and the columns returned (default + optional/`all_attributes`-only, per the docstrings). Columns already documented in pypowsybl's own docstrings are not repeated verbatim here in full prose — see `vendor/pypowsybl/pypowsybl/network/impl/network.py` for exact wording; below is the structural summary needed for schema design.

| Method | pandas index | Notable non-scalar/relational columns |
|---|---|---|
| `get_substations` | `id` | — (top of hierarchy) |
| `get_voltage_levels` | `id` | `substation_id` |
| `get_buses` | `id` (bus view) | `voltage_level_id` |
| `get_busbar_sections` | `id` | `voltage_level_id`, `bus_id`, `bus_breaker_bus_id`, `node` |
| `get_generators` | `id` | `voltage_level_id`, `bus_id`, `bus_breaker_bus_id`, `regulated_element_id` (polymorphic), `regulated_bus_id`, `regulated_bus_breaker_bus_id` |
| `get_loads` | `id` | `voltage_level_id`, `bus_id`, `bus_breaker_bus_id` |
| `get_lines` | `id` | `voltage_level1_id`, `voltage_level2_id`, `bus1_id`, `bus2_id` |
| `get_2_windings_transformers` | `id` | `voltage_level1_id`, `voltage_level2_id`, `bus1_id`, `bus2_id` |
| `get_3_windings_transformers` | `id` | `voltage_level{1,2,3}_id`, `bus{1,2,3}_id` |
| `get_switches` | `id` | `voltage_level_id` |
| `get_shunt_compensators` | `id` | `voltage_level_id`, `bus_id` |
| `get_linear_shunt_compensator_sections` | `id` (shunt id) | — |
| `get_non_linear_shunt_compensator_sections` | **multi:** `(id, section number)` | — |
| `get_boundary_lines` | `id` | `voltage_level_id`, `bus_id`, `tie_line_id` |
| `get_static_var_compensators` | `id` | `voltage_level_id`, `bus_id`, `regulated_element_id` (polymorphic), `regulated_bus_id` |
| `get_ratio_tap_changers` | `id` (transformer id) — **see caveat below** | `regulating_bus_id` |
| `get_phase_tap_changers` | `id` (transformer id) — **see caveat below** | `regulating_bus_id` |
| `get_ratio_tap_changer_steps` | **multi:** `(id, position)` | — |
| `get_phase_tap_changer_steps` | **multi:** `(id, position)` | — |
| `get_loading_limits` | **multi:** `(element_id, side, type, acceptable_duration, group_name)` | `element_id` + `element_type` (polymorphic, closed set — see below) |

### Caveat: `side` is not part of the documented pandas index, but must be part of the DB key

For `get_ratio_tap_changers`, `get_phase_tap_changers`, `get_ratio_tap_changer_steps`, and `get_phase_tap_changer_steps`, pypowsybl's own pandas index is just `id` (or `(id, position)`) — but a 3-windings transformer can carry a tap changer on more than one leg, producing multiple rows that share the same `id`, distinguished only by the `side` column (`ONE`/`TWO`/`THREE`, empty for 2-windings transformers). Treating pandas' documented index as the literal, sufficient primary key would allow silent collisions for 3-windings transformers.

**Decision carried into `02-schema-design.md`: `side` is added to the primary key of these four tables**, normalized to an empty string (not NULL) for the 2-windings-transformer case, so the composite key stays usable. This should be explicitly validated in `03-testing-strategy.md` against a network with multi-leg tap changers.

### `get_loading_limits`'s polymorphism is a closed set

`element_type` is constrained to exactly `LINE`, `TWO_WINDINGS_TRANSFORMER`, `THREE_WINDINGS_TRANSFORMER`, `BOUNDARY_LINE` (per docstring). `element_id` + `element_type` together identify a row in one of those four tables — see the "polymorphic references" decision in `02-schema-design.md` for how this is (and isn't) enforced with foreign keys.

`regulated_element_id` on `get_generators` and `get_static_var_compensators` is a similar but *open-ended* polymorphic reference (per pypowsybl, it can point at any network element acting as a regulating terminal, not just a fixed set of 4 types) — treated differently, see `02-schema-design.md`.

## Built-in test fixtures (feeds into `03-testing-strategy.md`)

No CGMES file needs to be sourced externally. The `pypowsybl` submodule ships:
- In-memory network factories requiring no file I/O: `create_eurostag_tutorial_example1_network()`, `create_four_substations_node_breaker_network()` (node-breaker topology, useful for `node`/`bus_breaker_bus_id` columns), `create_micro_grid_be_network()` / `create_micro_grid_nl_network()` (loaded from bundled CGMES data, exercises boundary lines / tie lines).
- Bundled CGMES fixtures under `vendor/pypowsybl/data/`: `CGMES_Full.zip`, `CGMES_Partial.zip`, `MicroGridTestConfiguration_T4_BE_BB_Complete_v2.zip`, `Boundary.zip`.
