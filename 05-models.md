# 05 — Model definitions

The concrete, table-by-table plan to implement, applying the conventions from `02-schema-design.md`. Column *semantics* (units, meaning) are documented in pypowsybl's own docstrings (see `01-api-analysis.md`) and are not repeated here — this is the structural translation into SQLAlchemy columns: name, type, key role.

## Blanket rules (apply to every table below, not repeated per column)

- Every table has `snapshot_id` (FK → `network_snapshot.id`) and `scenario_time` (datetime, denormalized, indexed) in addition to the columns listed.
- Primary key = `snapshot_id` + the columns marked **PK** below.
- Foreign keys are always scoped by `snapshot_id` in addition to the natural column(s) shown (composite FK), per `02-schema-design.md`.
- **Nullability:** only PK columns and the boolean status flags explicitly marked **not null** below are non-nullable. Every other column is nullable — this covers both pypowsybl's `all_attributes`-only columns (absent unless requested) and default columns that are legitimately `NaN` pre-loadflow (`p`, `q`, `i`, `solved_tap_position`, `solved_section_count`, etc.). Modeling everything else as nullable avoids 100+ redundant annotations for what's already documented per-column in pypowsybl's own docstrings.
- Capture the *full* attribute set (i.e. what `all_attributes=True` returns), not just pypowsybl's default subset — a persisted snapshot should be replayable without having to know which optional columns a future query will need.
- Enum-like string columns from pypowsybl (`energy_source`, `reactive_limits_kind`, `regulation_mode`, `type`, `kind`, `model_type`, `topology_kind`, `element_type`, limit `type`) are stored as plain `String`, not a DB-level enum — pypowsybl can add new values across versions (`01-api-analysis.md`), and a DB enum would need a migration each time.

## `network_snapshot`

- `id` — Integer, surrogate PK, autoincrement
- `scenario_time` — DateTime, not null, indexed

## `substation`

- `id` — String, **PK**
- `name`, `TSO`, `geo_tags`, `country` — String
- `fictitious` — Boolean

## `voltage_level`

- `id` — String, **PK**
- `substation_id` — String, FK → `substation.id`
- `nominal_v`, `high_voltage_limit`, `low_voltage_limit` — Float
- `fictitious` — Boolean
- `topology_kind` — String

## `bus`

- `id` — String, **PK** (bus-view ID)
- `voltage_level_id` — String, FK → `voltage_level.id`
- `v_mag`, `v_angle`, `fictitious_p0`, `fictitious_q0` — Float
- `connected_component`, `synchronous_component` — Integer

## `busbar_section`

- `id` — String, **PK**
- `voltage_level_id` — String, FK → `voltage_level.id`
- `bus_id` — String, FK → `bus.id`
- `bus_breaker_bus_id`, `node` — String
- `v`, `angle` — Float
- `connected`, `fictitious` — Boolean

## `generator`

- `id` — String, **PK**
- `voltage_level_id` — String, FK → `voltage_level.id`
- `bus_id`, `regulated_bus_id` — String, FK → `bus.id`
- `bus_breaker_bus_id`, `regulated_bus_breaker_bus_id`, `node` — String
- `regulated_element_id` — String, **no FK** (open-ended polymorphic reference — `02-schema-design.md`)
- `energy_source`, `reactive_limits_kind` — String
- `target_p`, `max_p`, `min_p`, `max_q`, `min_q`, `max_q_at_target_p`, `min_q_at_target_p`, `max_q_at_p`, `min_q_at_p`, `rated_s`, `target_v`, `equivalent_local_target_v`, `target_q`, `p`, `q`, `i` — Float
- `voltage_regulator_on`, `connected`, `condenser`, `fictitious` — Boolean

## `load`

- `id` — String, **PK**
- `voltage_level_id` — String, FK → `voltage_level.id`
- `bus_id` — String, FK → `bus.id`
- `bus_breaker_bus_id`, `node` — String
- `type` — String
- `p0`, `q0`, `p`, `q`, `i` — Float
- `connected`, `fictitious` — Boolean

## `line`

- `id` — String, **PK**
- `voltage_level1_id`, `voltage_level2_id` — String, FK → `voltage_level.id`
- `bus1_id`, `bus2_id` — String, FK → `bus.id`
- `bus_breaker_bus1_id`, `bus_breaker_bus2_id`, `node1`, `node2`, `selected_limits_group_1`, `selected_limits_group_2` — String
- `r`, `x`, `g1`, `b1`, `g2`, `b2`, `p1`, `q1`, `i1`, `p2`, `q2`, `i2` — Float
- `connected1`, `connected2`, `fictitious` — Boolean

## `two_windings_transformer`

- `id` — String, **PK**
- `voltage_level1_id`, `voltage_level2_id` — String, FK → `voltage_level.id`
- `bus1_id`, `bus2_id` — String, FK → `bus.id`
- `bus_breaker_bus1_id`, `bus_breaker_bus2_id`, `node1`, `node2`, `selected_limits_group_1`, `selected_limits_group_2` — String
- `r`, `x`, `b`, `g`, `rated_u1`, `rated_u2`, `rated_s`, `p1`, `q1`, `i1`, `p2`, `q2`, `i2`, `rho`, `alpha`, `r_at_current_tap`, `x_at_current_tap`, `g_at_current_tap`, `b_at_current_tap` — Float
- `connected1`, `connected2`, `fictitious` — Boolean
- `id` also functions as an informal reference to `ratio_tap_changer.id`/`phase_tap_changer.id` (no DB FK — `02-schema-design.md`)

## `three_windings_transformer`

- `id` — String, **PK**
- `rated_u0` — Float
- `fictitious` — Boolean
- For each leg `n` in `{1, 2, 3}`:
  - `voltage_leveln_id` — String, FK → `voltage_level.id`
  - `busn_id` — String, FK → `bus.id`
  - `bus_breaker_busn_id`, `noden`, `selected_limits_group_n` — String
  - `rn`, `xn`, `bn`, `gn`, `rated_un`, `rated_sn`, `pn`, `qn`, `in`, `rhon`, `alphan`, `rn_at_current_tap`, `xn_at_current_tap`, `gn_at_current_tap`, `bn_at_current_tap` — Float
  - `ratio_tap_positionn`, `phase_tap_positionn` — Integer
  - `connectedn` — Boolean
- `id` also functions as an informal reference to `ratio_tap_changer.id`/`phase_tap_changer.id` (no DB FK — `02-schema-design.md`)

## `switch`

- `id` — String, **PK**
- `voltage_level_id` — String, FK → `voltage_level.id`
- `bus_breaker_bus1_id`, `bus_breaker_bus2_id`, `node1`, `node2` — String
- `kind` — String
- `open`, `retained`, `fictitious` — Boolean

## `shunt_compensator`

- `id` — String, **PK**
- `voltage_level_id` — String, FK → `voltage_level.id`
- `bus_id` — String, FK → `bus.id`
- `bus_breaker_bus_id`, `node` — String
- `model_type` — String
- `max_section_count`, `section_count` — Integer
- `solved_section_count` — Float (nullable — NaN pre-loadflow, per `01-api-analysis.md`)
- `p`, `q`, `i` — Float
- `connected`, `fictitious` — Boolean

## `linear_shunt_compensator_section`

- `id` — String, **PK** (shunt compensator id — FK → `shunt_compensator.id`)
- `g_per_section`, `b_per_section` — Float
- `max_section_count` — Integer

## `non_linear_shunt_compensator_section`

- `id` — String, **PK** (part 1 — FK → `shunt_compensator.id`)
- `section` — Integer, **PK** (part 2, the section number)
- `g`, `b` — Float

## `boundary_line`

- `id` — String, **PK**
- `voltage_level_id` — String, FK → `voltage_level.id`
- `bus_id` — String, FK → `bus.id`
- `bus_breaker_bus_id`, `node`, `pairing_key`, `ucte_xnode_code` — String
- `tie_line_id` — String, **no FK** (tie lines are not one of the 20 target tables)
- `r`, `x`, `g`, `b`, `p0`, `q0`, `p`, `q`, `i`, `boundary_p`, `boundary_q`, `boundary_i`, `boundary_v_mag`, `boundary_v_angle` — Float
- `connected`, `fictitious`, `paired` — Boolean

## `static_var_compensator`

- `id` — String, **PK**
- `voltage_level_id` — String, FK → `voltage_level.id`
- `bus_id`, `regulated_bus_id` — String, FK → `bus.id`
- `bus_breaker_bus_id`, `regulated_bus_breaker_bus_id`, `node` — String
- `regulated_element_id` — String, **no FK** (open-ended polymorphic reference)
- `regulation_mode` — String
- `b_min`, `b_max`, `target_v`, `target_q`, `p`, `q`, `i` — Float
- `connected`, `fictitious` — Boolean

## `ratio_tap_changer`

- `id` — String, **PK** (transformer id — see `01-api-analysis.md` caveat, no single FK)
- `side` — String, **PK**, not null (empty string `''` for 2-windings transformers)
- `regulating_bus_id` — String, FK → `bus.id`
- `regulation_mode` — String
- `tap`, `low_tap`, `high_tap`, `step_count` — Integer
- `solved_tap_position` — Float (nullable — NaN pre-loadflow)
- `target_v`, `target_deadband`, `regulation_value` — Float
- `regulated_side` — String
- `oltc`, `regulating` — Boolean

## `phase_tap_changer`

- `id` — String, **PK** (transformer id — see `01-api-analysis.md` caveat, no single FK)
- `side` — String, **PK**, not null (empty string `''` for 2-windings transformers)
- `regulating_bus_id` — String, FK → `bus.id`
- `regulation_mode` — String
- `tap`, `low_tap`, `high_tap`, `step_count` — Integer
- `solved_tap_position` — Float (nullable — NaN pre-loadflow)
- `regulation_value`, `target_deadband` — Float
- `regulated_side` — String
- `oltc`, `regulating` — Boolean

## `ratio_tap_changer_step`

- `id` — String, **PK** (transformer id) — FK → `ratio_tap_changer.(id, side)` together with `side`
- `side` — String, **PK**, not null (empty string for 2-windings transformers — carried over from the parent row since it isn't part of pypowsybl's own index; see `01-api-analysis.md`)
- `position` — Integer, **PK**
- `rho`, `r`, `x`, `g`, `b` — Float

## `phase_tap_changer_step`

- `id` — String, **PK** (transformer id) — FK → `phase_tap_changer.(id, side)` together with `side`
- `side` — String, **PK**, not null
- `position` — Integer, **PK**
- `rho`, `alpha`, `r`, `x`, `g`, `b` — Float

## `loading_limit`

- `element_id` — String, **PK**, **no FK** (closed 4-way polymorphism — `02-schema-design.md`)
- `element_type` — String, not null (`LINE` / `TWO_WINDINGS_TRANSFORMER` / `THREE_WINDINGS_TRANSFORMER` / `BOUNDARY_LINE`)
- `side` — String, **PK**
- `type` — String, **PK**, not null (`CURRENT` / `ACTIVE_POWER` / `APPARENT_POWER`)
- `acceptable_duration` — Integer, **PK**, not null (`-1` = infinite duration, per pypowsybl convention — not NULL)
- `group_name` — String, **PK**
- `name` — String
- `value` — Float
- `fictitious`, `selected` — Boolean

## Open decisions to confirm before implementation

Collected from `01-api-analysis.md` and `02-schema-design.md` — implementation should not proceed past these without a decision:

1. Composite PK for `network_snapshot` + pandas index (vs. a literal reading of "pandas index = primary key") — `02-schema-design.md`.
2. `side` added to the PK of the four tap-changer tables, normalized to `''` rather than NULL — needs validation against a real multi-leg-tap-changer network (`03-testing-strategy.md`).
3. No DB-level FK for tap-changer-to-transformer, `loading_limit.element_id`, or `regulated_element_id` — `02-schema-design.md`.
4. `transformer_end` normalization (2WT sides / 3WT legs into a shared table) — considered and not recommended, but flagged as a real alternative.
