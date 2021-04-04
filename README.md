# SymmetricDS Manager

A manager for easing the creation of node properties file and relivant SQL queries for instantiating [SymmetricDS](https://www.symmetricds.org/d) replications.

## Why another SymmetricDS Manager ?
[SymmetricDS](https://www.symmetricds.org/d) has a compatible manager that comes with the [JumpMind's](https://www.jumpmind.com/) [SymmetricDS Pro version](https://www.jumpmind.com/products/symmetricds/overview) with starting price at $2,400 USD.

## Compatibility

This manager has **ONLY** been tested with SymmetricDS Community Version 3.12.

## Configuration Properties

Sample [JSON](https://www.json.org/json-en.html) configuration [file](samples/cnf.json) is included in the samples directory.

### Groups

A list of groups in the replication has to be supplied. Each groups can have the following properties:

- `name` The groups unique name
- `description` An optional description of the group
- `sync` A synchronization mode which determines how the group links will be created. options are `P` (Push), `W` (Wait for pull), `R` (Route-only).

See SymetricDS Docummentation on [groups](https://www.symmetricds.org/doc/3.12/html/user-guide.html#_groups) and [group links](https://www.symmetricds.org/doc/3.12/html/user-guide.html#_group_links) for more details.

### Replication Architecture Options

- `bi-directional` This architecture allows information to flow in both directions between nodes. For example, specific data can be shared between a Headquarter and multiple branches in all direction. This architecture can still be used to replicate functionality of a parent-child or child-parent architecture. A router has to be specified for each table in the manager's JSON configuration file. Additional channel triggers will be created for each table that requires initial load. Thus, for tables within `inital_load` property set to `1`, it is required that an `inital_load_route` property is set to either `parent-child` `child-parent`.

- `parent-child` Allows repliaction of data in one direction from parent to children only. No need for table-specific routing information.All data will be routed from parent to child

- `child-parent` Allows repliaction of data in one direction from children to parent only.The router direction for each table has to be specified
