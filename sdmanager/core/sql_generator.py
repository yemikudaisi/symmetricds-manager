# Note: Generally avoided multiline string to ensure consistency
# in built SQL thus enabling unit tests.


def create_channel(channel_id, processing_order: int=1, max_batch_size: int=100000, enabled: int=1, description: str="") -> str:
    return f"insert into sym_channel (channel_id, processing_order, max_batch_size, enabled, description) values ('{channel_id}', {processing_order}, {max_batch_size}, {enabled}, '{description}');"

def create_node_group(id: str, description: str = '') -> str:
    return f"insert into SYM_NODE_GROUP (node_group_id, description) values ('{id}', '{description}');"

def create_node_group_link(source: str, target: str, option: str) -> str:
    return f"insert into SYM_NODE_GROUP_LINK (source_node_group_id, target_node_group_id, data_event_action) values ('{source}', '{target}', '{option}');"

def create_channel_trigger(trigger_id: str, source_table: str, channel: str) -> str:
    """
    Generates SQL for a single channel trigger

    Parameter
    ---------
    trigger_id : str
        The trigger ID to be assigned to the trigger
    source_table : str
        The source table which will activate the trigger
    channel : str
        The channel the source table belongs to
    
    Returns
    -------
    str
        The generated SQl query
    """

    return f"insert into sym_trigger (trigger_id,source_table_name,channel_id,last_update_time,create_time) values ('{trigger_id}','{source_table}','{channel}',current_timestamp,current_timestamp);"

def create_table_trigger(tbl):
    return f"insert into sym_trigger (trigger_id,source_table_name,channel_id,last_update_time,create_time) values ('{tbl['name']}','{tbl['name']}','{tbl['channel']}',current_timestamp,current_timestamp);"
    
def create_table_load_only_trigger(tbl) -> str:
    """
    This does not carry out validation, user are to ensure validation 
    before passing table dictionary to this method
    """
    trigger_id = f"{tbl['name']}_{tbl['initial_load_route'].split('-')[0]}"
    return f"insert into sym_trigger (trigger_id,source_table_name,channel_id, sync_on_insert, sync_on_update, sync_on_delete,last_update_time,create_time) values ('{trigger_id}','{tbl['name']}','{tbl['channel']}',0,0,0,current_timestamp,current_timestamp);"

def create_default_router(router_id, source_node_group_id, target_node_group_id) -> str:
    return f"insert into sym_router (router_id,source_node_group_id,target_node_group_id,router_type,create_time,last_update_time) values ('{router_id}','{source_node_group_id}','{target_node_group_id}','default',current_timestamp,current_timestamp);"

def create_column_router(router_id, source_node_group_id, target_node_group_id, expression="" ) -> str:
    # TODO Unit tests
    return f"insert into sym_router (router_id,source_node_group_id,target_node_group_id,router_type,router_expression,create_time,last_update_time) values ('{router_id}','{source_node_group_id}','{target_node_group_id}','column','{expression}',current_timestamp,current_timestamp);"

def create_router_trigger(trigger_id, router_id, initial_load_order = 100):
    return f"insert into sym_trigger_router (trigger_id,router_id,initial_load_order,last_update_time,create_time) values ('{trigger_id}','{router_id}',{initial_load_order},current_timestamp,current_timestamp);"
