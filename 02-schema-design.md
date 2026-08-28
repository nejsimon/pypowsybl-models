# 02 — Schema design

Builds on `01-api-analysis.md`. Covers the snapshot/versioning convention, table list, relations, and the polymorphic-reference decisions. `05-models.md` has the full column-by-column definitions.

## Reconciling the three stated requirements

`spec.md` states three requirements that, taken individually, are in tension:

1. "The pandas dataframe index should be the primary key."
2. "The scenario_time must be included in an index" (and is "not unique in itself").
3. "There must be a `network_snapshot` table and each table must have a `snapshot_id` referring to this table."

Taken literally, (1) alone would make e.g. `id` (a generator ID) the sole primary key of the `generator` table — but that collides across snapshots, since the same generator ID reappears in every snapshot. Requirements (2) and (3) only make sense if a table is expected to hold rows from *many* snapshots at once.

**Decision:** the primary key of every data table is **`snapshot_id` + the pandas index column(s)**, not the pandas index alone. This satisfies (1) (the pandas index is still fully part of, and drives, the primary key — it's just not the *whole* key) while making (3) meaningful. For (2), `scenario_time` is denormalized from `network_snapshot` onto every data table as a plain (non-unique) column, with a secondary index on it — so time-range queries don't require a join to `network_snapshot` first. This is called out explicitly because it's a deviation from the literal wording of requirement (1); flag if a stricter reading was intended.

## `network_snapshot`

| Column | Type | Notes |
|---|---|---|
| `id` | surrogate PK (integer, autoincrement) | Referenced by every other table's `snapshot_id`. |
| `scenario_time` | datetime, indexed | The instant the snapshot represents. Not unique alone (multiple snapshots can share a `scenario_time`, e.g. re-runs) — matches spec.md's note. |

Kept minimal on purpose. Any richer metadata (source file name, network ID/name, load timestamp) is speculative until a concrete need shows up — add later rather than guessing now.

## Primary key & indexing convention (applies to every data table)

- `snapshot_id` — FK to `network_snapshot.id`, part of the composite PK.
- `scenario_time` — denormalized copy of the owning snapshot's `scenario_time`, plain column, indexed (`ix_<table>_scenario_time` or combined with the natural id, e.g. `(scenario_time, id)`, depending on the dominant query pattern — finalize in `05-models.md` per table if it differs from the default).
- the pandas index column(s) from `01-api-analysis.md`, renamed `id` where pypowsybl calls it `id`, otherwise kept as named (`element_id`, `position`, etc.).
- PRIMARY KEY = `(snapshot_id, <pandas index column(s)>)`.

## Table list (20 tables, one per target method, mirroring `01-api-analysis.md`)

`network_snapshot`, `substation`, `voltage_level`, `bus`, `busbar_section`, `generator`, `load`, `line`, `two_windings_transformer`, `three_windings_transformer`, `switch`, `shunt_compensator`, `linear_shunt_compensator_section`, `non_linear_shunt_compensator_section`, `boundary_line`, `static_var_compensator`, `ratio_tap_changer`, `phase_tap_changer`, `ratio_tap_changer_step`, `phase_tap_changer_step`, `loading_limit`.

## Relations (foreign keys)

Straightforward one-target relations get real foreign keys, all additionally scoped by `snapshot_id` (a bus in snapshot A must not satisfy a FK from a generator row in snapshot B):

- `voltage_level.substation_id` → `substation.id`
- `bus.voltage_level_id` → `voltage_level.id`
- `busbar_section.voltage_level_id` → `voltage_level.id`; `busbar_section.bus_id` → `bus.id`
- `generator.voltage_level_id` → `voltage_level.id`; `generator.bus_id` → `bus.id`; `generator.regulated_bus_id` → `bus.id`
- `load.voltage_level_id` → `voltage_level.id`; `load.bus_id` → `bus.id`
- `line.voltage_level1_id`/`voltage_level2_id` → `voltage_level.id`; `line.bus1_id`/`bus2_id` → `bus.id`
- `two_windings_transformer.voltage_level{1,2}_id` → `voltage_level.id`; `.bus{1,2}_id` → `bus.id`
- `three_windings_transformer.voltage_level{1,2,3}_id` → `voltage_level.id`; `.bus{1,2,3}_id` → `bus.id`
- `switch.voltage_level_id` → `voltage_level.id`
- `shunt_compensator.voltage_level_id` → `voltage_level.id`; `.bus_id` → `bus.id`
- `linear_shunt_compensator_section.id` / `non_linear_shunt_compensator_section.id` → `shunt_compensator.id` (both scoped by `snapshot_id`)
- `boundary_line.voltage_level_id` → `voltage_level.id`; `.bus_id` → `bus.id`
- `static_var_compensator.voltage_level_id` → `voltage_level.id`; `.bus_id` → `bus.id`; `.regulated_bus_id` → `bus.id`
- `ratio_tap_changer_step.(id, side)` → `ratio_tap_changer.(id, side)`; same pattern for `phase_tap_changer_step` → `phase_tap_changer`

Composite FKs throughout implicitly include `snapshot_id` on both sides (standard practice for snapshot-scoped schemas — every FK is really `(snapshot_id, <natural columns>)` → `(snapshot_id, <natural columns>)`).

## Polymorphic references — two different patterns, two different decisions

### `ratio_tap_changer.id` / `phase_tap_changer.id` can belong to either a 2- or 3-windings transformer

A tap changer's `id` is the *owning transformer's* ID, but that transformer might be in `two_windings_transformer` or `three_windings_transformer` — there's no column telling you which. Enforcing a single DB-level FK isn't possible without checking both tables.

**Decision: no DB-level FK from tap-changer tables to either transformer table.** Store `id` as a plain indexed column. Document the ambiguity in the model docstring/comment. Adding two nullable FK columns with a "exactly one is set" check constraint was considered and rejected as unnecessary complexity for a relationship that's easy to resolve at query time (`id` exists in exactly one of the two transformer tables for a given snapshot) — consistent with "keep it simple."

### `loading_limit.element_id` (closed 4-way polymorphism) vs. `generator.regulated_element_id` / `static_var_compensator.regulated_element_id` (open-ended)

`loading_limit.element_type` is a closed enum (`LINE`, `TWO_WINDINGS_TRANSFORMER`, `THREE_WINDINGS_TRANSFORMER`, `BOUNDARY_LINE` — see `01-api-analysis.md`), so it *could* be modeled with 4 nullable FK columns guarded by a check constraint matching `element_type`. `regulated_element_id`, by contrast, can reference essentially any network element (not just a fixed set of 4), so the same trick doesn't scale there.

**Decision: treat both the same way, as plain unconstrained columns, for consistency and simplicity** — `loading_limit.element_id`/`element_type` and `regulated_element_id` are stored as-is with no FK. This is the one place where "keep it simple" is weighed above "relate tables by id with foreign keys" from `spec.md`'s step 4; flag if closed-set enforcement for `loading_limit` specifically is wanted instead.

## Deduplication assessment (spec.md step 5)

pypowsybl's own dataframes are already fairly normalized for our purposes — most "shared data" is already factored out upstream (e.g. bus electrical state lives once in `get_buses`, and every other element references it by `bus_id` rather than repeating `v_mag`/`v_angle`). The natural dedup opportunities that exist are the ones pypowsybl itself already splits into their own methods, and this schema mirrors that 1:1 rather than inventing new shared tables:

- Tap changer steps are already separate from their parent tap changer (`*_tap_changer` vs `*_tap_changer_step`).
- Shunt compensator sections are already separate from `shunt_compensator`.

One dedup opportunity was considered and **rejected**: factoring `two_windings_transformer`'s two sides and `three_windings_transformer`'s three legs into a shared `transformer_end` table (they share most column names — `r`, `x`, `b`, `g`, `rated_u`, `p`, `q`, `i`, `voltage_level_id`, `bus_id`, `connected`, tap-position/`rho`/`alpha`/`*_at_current_tap`). This would reduce column repetition but breaks the "one table per method" structure `spec.md` asks for and adds join complexity for what's normally read as one wide row per transformer. Flag if this normalization is actually wanted — it's a bigger structural change than anything else in this design.
