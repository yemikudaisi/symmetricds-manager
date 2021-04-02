------------------------------------------------------------------------------
-- Clear and load SymmetricDS Configuration
------------------------------------------------------------------------------

delete from sym_trigger_router;
delete from sym_trigger;
delete from sym_router;
delete from sym_channel where channel_id in ($channels_list);
delete from sym_node_group_link;
delete from sym_node_group;
delete from sym_node_host;
delete from sym_node_identity;
delete from sym_node_security;
delete from sym_node;

------------------------------------------------------------------------------
-- Channels
------------------------------------------------------------------------------
$channel
------------------------------------------------------------------------------
-- Node Groups
------------------------------------------------------------------------------
$group
------------------------------------------------------------------------------
-- Node Group Links
------------------------------------------------------------------------------
$group_links
------------------------------------------------------------------------------
-- Triggers
------------------------------------------------------------------------------

-- Triggers for tables on "item" channel
$table_triggers
-- Triggers with capture disabled, so they are used for initial load only
$initial_load_table_triggers
------------------------------------------------------------------------------
-- Routers
------------------------------------------------------------------------------

-- Default router sends all data from corp to store 
$router
------------------------------------------------------------------------------
-- Trigger Routers
------------------------------------------------------------------------------
$router_triggers
$initial_load_router_triggers
