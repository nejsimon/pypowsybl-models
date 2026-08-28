# SQLAhcmey models for power system blocks (pypowsybl)

This repository contains SQLAchemy models for pypowsybl redy to be used in a database.

## Target methods:
* Network.get_buses()
* Network.get_busbar_sections()
* Network.get_lines()
* Network.get_generators()
* Network.get_loads()
* Network.get_2_windings_transformers()
* Network.get_3_windings_transformers()
* Network.get_switches()
* Network.get_substations()
* Network.get_loading_limits()
* Network.get_boundary_lines()
* Network.get_shunt_compensators()
* Network.get_linear_shunt_compensator_sections()
* Network.get_non_linear_shunt_compensator_sections()
* Network.get_phase_tap_changers()
* Network.get_ratio_tap_changers()
* Network.get_phase_tap_changer_steps()
* Network.get_ratio_tap_changer_steps()
* Network.get_static_var_compensators()
* Network.get_voltage_levels()

## Suggested workflow
1. Check our pypowsybl from https://github.com/powsybl/pypowsybl as a submodule
2. Check the Network object defined in the file pypowsybl/network/impl/network.py
3. Assess the API stability of the methods mentioned. Additions are fine, historical changes and removals should be noted. Check the git history, release tags or just the history.
4. Assess relations, i.e. tables relating to each other by id. These should be related using foreign keys in the models.
5. Assess if common data could be broken out to table(s) to deduplicate data.
6. Create one table / database model per mentioned method and possibly any other needed table as stated previously.

## Requirements
* The pandas dataframe index should be the primary key.
* The scenario_time must be included in an index as this will be queried often but it's not unique in itself.
* In addition there must be a network_snapshot table and each table must have a snapshot_id refering to this table.

## Note
* Testing this may be difficult as it'll require a file in CGMES format to be loaded into pypowsybl but maybe something can be done, maybe there are mock data to be found.
* Testing, if possibly, can be done using sqlite3.