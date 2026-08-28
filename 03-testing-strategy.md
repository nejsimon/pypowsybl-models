# 03 — Testing strategy

Addresses the "Note" in `spec.md` about CGMES fixtures being hard to come by. Per `01-api-analysis.md`, this turns out not to be a problem: pypowsybl ships everything needed as part of the submodule.

## Fixtures — no external CGMES file needs to be sourced

Use pypowsybl's own network factory functions (`pypowsybl.network.impl.network_creation_util`), which build a fully-loaded `Network` in memory, no file I/O required:

- `create_eurostag_tutorial_example1_network()` — small, simple bus-breaker network. Good default fixture for most tables.
- `create_four_substations_node_breaker_network()` — node-breaker topology. Needed to exercise `node`, `bus_breaker_bus_id`-style columns that are absent/empty in bus-breaker networks.
- `create_micro_grid_be_network()` / `create_micro_grid_nl_network()` — loaded from the bundled CGMES fixtures under `pypowsybl/data/` (`MicroGridTestConfiguration_T4_BE_BB_Complete_v2.zip`, `Boundary.zip`). These are the ones that exercise `boundary_line`/tie lines and are closest to real CGMES data.

None of these require network access or a locally-supplied CGMES file — they're all resolved from within the `pypowsybl` submodule already added to this repo.

## What needs a network with tap changers on more than one leg

`01-api-analysis.md` flags that the composite primary key for the four tap-changer tables must include `side`, because a 3-windings transformer can carry tap changers on multiple legs sharing the same `id`. Before trusting that design: run `get_ratio_tap_changers()` / `get_phase_tap_changers()` against the built-in networks and confirm whether any of them actually produces >1 row per `id`. If none do, this needs a network built by hand (or `create_micro_grid_*`, if it happens to have one) specifically to validate the composite-key assumption rather than trusting the docstring's wording alone.

## Test approach

1. **Schema tests, no pypowsybl needed:** create all tables against an in-memory SQLite DB (`sqlite:///:memory:` or a temp file) and assert constraints (PKs, FKs, not-null) hold using hand-built rows. Fast, no dependency on pypowsybl actually being importable.
2. **Round-trip tests, one per target method:** load a fixture network, call the corresponding `Network.get_*()` method, insert the resulting DataFrame into a fresh `network_snapshot` + its table via the ORM (`DataFrame.to_sql`-style or explicit row construction — decide in `05-models.md`/implementation), then query it back and assert the values match the DataFrame. This is the primary correctness check per table.
3. **Cross-table relation tests:** for a couple of representative FKs (e.g. `bus.voltage_level_id` → `voltage_level.id`, `line.bus1_id` → `bus.id`), assert that every referenced ID inserted from a fixture network's DataFrame actually exists in the target table — catches ordering bugs (inserting children before parents) and confirms the relations in `02-schema-design.md` hold on real data, not just in theory.
4. **Multi-snapshot test:** insert the same fixture network twice under two different `network_snapshot` rows (different `scenario_time`) and confirm no primary-key collisions occur and that both snapshots' data can be queried independently — this is the main thing the `snapshot_id`-in-PK design (`02-schema-design.md`) needs to prove.

## Runner

SQLite is sufficient for all of the above per `spec.md`'s own note — no external database server needed for tests. `pypowsybl` itself must be installed (it's a compiled Python package, not pure source — see `04-project-setup.md` for how it's wired in via `uv`).
