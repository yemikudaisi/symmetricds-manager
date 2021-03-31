# Friendly name to refer to this node from command line
engine.name=$engine_name

# The class name for the JDBC Driver
db.driver=$db_driver

# The JDBC URL used to connect to the database
db.url=$db_url

# The database user that SymmetricDS should use.
db.user=$db_user

# The database password
db.password=$db_password

# This node will contact the root node's sync.url to register itself.
# Leave blank to indicate this is the root node.
registration.url=

# Sync URL where other nodes can contact this node to push/pull data or register.
sync.url=$url

# Node group this node belongs to, which defines what it will sync with who.
# Must match the sym_node_group configuration in database.
group.id=$group_id

# External ID for this node, which is any unique identifier you want to use.
external.id=$external_id

# How often to run purge job,
job.purge.period.time.ms=$job_purge_period_time_ms

# How to run routing (in millis), which puts changes into batches.
job.routing.period.time.ms=$job_routing_period_time_ms

# How often to run push (in millis), which sends changes to other nodes.
job.push.period.time.ms=$job_push_period_time_ms

# How often to run pull (in millis), which receives changes from other nodes.
job.pull.period.time.ms=$job_pull_period_time_ms

# Automatically register new nodes when they request it.
# If this is false, accept the registration requests using "symadmin open-registration" command.
auto.registration=$auto_registration

# When this node sends an initial load of data to another node, first send table create scripts.
initial.load.create.first=$initial_load_create_first