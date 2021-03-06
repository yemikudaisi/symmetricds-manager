# SymmetricDS Manager

A manager for easing the creation of node properties file and relivant SQL queries for instantiating [SymmetricDS](https://www.symmetricds.org/d) replications.

## Why another SymmetricDS Manager ?

Well, [SymmetricDS](https://www.symmetricds.org/d) has a compatible manager that comes with the [JumpMind's](https://www.jumpmind.com/) [SymmetricDS Pro version](https://www.jumpmind.com/products/symmetricds/overview). But the starting price is $2,400 USD.

## Compatibility

This manager has **ONLY** been tested with SymmetricDS Community Version 3.12.

## Requirements

- [Python 3](https://www.python.org/download/releases/3.0/)
- [PIP](https://pypi.org/project/pip/)

## Installation

```sh
git clone https://github.com/yemikudaisi/symmetricds-manager.git
cd symmetricds-manager
pip install --editable .
```

## Basic Usage

### Create SymmetricDS node properties and SQL queries:

```sh
 sd-manager --properties "/path/to/replication/properties" --output "/path/to/output/directory"
```

#### Options

| Options       | Function      |
| :-------------: |:-------------|
| `-p`/`--properties`| Path to replications properties JSON file |
| `-o`/`--output`    | **Optional** path to output directory for generated symmetricDS files. **Note** If this options is not supplied, file contents will output to shell.|

## Replications Properties

Sample [JSON](https://www.json.org/json-en.html) configuration [file](samples/cnf.json) is included in the samples directory.

**NOTE** The values `parent-child` and `child-parent` are used differently within 2 different context in the replication properties.

In one context, replication architecture (`repl-arch`) can be set to either of the above. For example, if `child-parent` is set as replication architecture, all synchronizations for all tables will be routed from child to parent only.

For the other context, when the replication architecture is set as `bi-directional`, each table is required to specify the direction (`route`) for synchronization of data. Additionally, another direction (`intitial-load-route`) is also required if all data from a table in one group is to be loaded to another group only on initialization of replication.

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
