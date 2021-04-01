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
registration.url=$url

# Node group this node belongs to, which defines what it will sync with who.
# Must match the sym_node_group configuration in database.
group.id=$group_id

# External ID for this node, which is any unique identifier you want to use.
external.id=$external_id

# How to run routing (in millis), which puts changes into batches.
job.routing.period.time.ms=$job_routing_period_time_ms

# How often to run push (in millis), which sends changes to other nodes.
job.push.period.time.ms=$job_push_period_time_ms

# How often to run pull (in millis), which receives changes from other nodes.
job.pull.period.time.ms=$job_pull_period_time_ms