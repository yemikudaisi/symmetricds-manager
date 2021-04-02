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

-- Channel "sale_transaction" for tables related to sales and refunds
insert into sym_channel 
(channel_id, processing_order, max_batch_size, enabled, description)
values('sale_transaction', 1, 100000, 1, 'sale_transactional data from register and back office');

-- Channel "item" for tables related to items for purchase
insert into sym_channel 
(channel_id, processing_order, max_batch_size, enabled, description)
values('item', 1, 100000, 1, 'Item and pricing data');

------------------------------------------------------------------------------
-- Node Groups
------------------------------------------------------------------------------

insert into sym_node_group (node_group_id) values ('corp');
insert into sym_node_group (node_group_id) values ('store');

------------------------------------------------------------------------------
-- Node Group Links
------------------------------------------------------------------------------

-- Corp sends changes to Store when Store pulls from Corp
insert into sym_node_group_link (source_node_group_id, target_node_group_id, data_event_action) values ('corp', 'store', 'W');

-- Store sends changes to Corp when Store pushes to Corp
insert into sym_node_group_link (source_node_group_id, target_node_group_id, data_event_action) values ('store', 'corp', 'P');

------------------------------------------------------------------------------
-- Triggers
------------------------------------------------------------------------------

-- Triggers for tables on "item" channel
insert into sym_trigger 
(trigger_id,source_table_name,channel_id,last_update_time,create_time)
values('item_selling_price','item_selling_price','item',current_timestamp,current_timestamp);

insert into sym_trigger 
(trigger_id,source_table_name,channel_id,last_update_time,create_time)
values('item','item','item',current_timestamp,current_timestamp);

-- Triggers for tables on "sale_transaction" channel
insert into sym_trigger 
(trigger_id,source_table_name,channel_id,last_update_time,create_time)
values('sale_transaction','sale_transaction','sale_transaction',current_timestamp,current_timestamp);

insert into sym_trigger 
(trigger_id,source_table_name,channel_id,last_update_time,create_time)
values('sale_return_line_item','sale_return_line_item','sale_transaction',current_timestamp,current_timestamp);

-- Triggers with capture disabled, so they are used for initial load only
insert into sym_trigger 
(trigger_id,source_table_name,channel_id, sync_on_insert, sync_on_update, sync_on_delete,last_update_time,create_time)
values('sale_transaction_corp','sale_transaction','sale_transaction',0,0,0,current_timestamp,current_timestamp);

insert into sym_trigger 
(trigger_id,source_table_name,channel_id, sync_on_insert, sync_on_update, sync_on_delete,last_update_time,create_time)
values('sale_return_line_item_corp','sale_return_line_item','sale_transaction',0,0,0,current_timestamp,current_timestamp);

------------------------------------------------------------------------------
-- Routers
------------------------------------------------------------------------------

-- Default router sends all data from corp to store 
insert into sym_router 
(router_id,source_node_group_id,target_node_group_id,router_type,create_time,last_update_time)
values('corp_2_store', 'corp', 'store', 'default',current_timestamp, current_timestamp);

-- Default router sends all data from store to corp
insert into sym_router 
(router_id,source_node_group_id,target_node_group_id,router_type,create_time,last_update_time)
values('store_2_corp', 'store', 'corp', 'default',current_timestamp, current_timestamp);

-- Column match router will subset data from corp to specific store
insert into sym_router 
(router_id,source_node_group_id,target_node_group_id,router_type,router_expression,create_time,last_update_time)
values('corp_2_one_store', 'corp', 'store', 'column','STORE_ID=:EXTERNAL_ID or OLD_STORE_ID=:EXTERNAL_ID',current_timestamp, current_timestamp);


------------------------------------------------------------------------------
-- Trigger Routers
------------------------------------------------------------------------------

-- Send all items to all stores
insert into sym_trigger_router 
(trigger_id,router_id,initial_load_order,last_update_time,create_time)
values('item','corp_2_store', 100, current_timestamp, current_timestamp);

-- Send item prices to associated stores
insert into sym_trigger_router 
(trigger_id,router_id,initial_load_order,initial_load_select,last_update_time,create_time)
values('item_selling_price','corp_2_one_store',100,'store_id=''$(externalId)''',current_timestamp,current_timestamp);

-- Send all sales transactions to corp
insert into sym_trigger_router 
(trigger_id,router_id,initial_load_order,last_update_time,create_time)
values('sale_transaction','store_2_corp', 200, current_timestamp, current_timestamp);

insert into sym_trigger_router 
(trigger_id,router_id,initial_load_order,last_update_time,create_time)
values('sale_return_line_item','store_2_corp', 200, current_timestamp, current_timestamp);

-- Send all sales transactions to store during initial load
insert into sym_trigger_router 
(trigger_id,router_id,initial_load_order,last_update_time,create_time)
values('sale_transaction_corp','corp_2_store', 200, current_timestamp, current_timestamp);

insert into sym_trigger_router 
(trigger_id,router_id,initial_load_order,last_update_time,create_time)
values('sale_return_line_item_corp','corp_2_store', 200, current_timestamp, current_timestamp);

