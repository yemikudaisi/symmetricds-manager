from core import GroupLinkOptions

# Note: Generally avoided multiline string to ensure consistency
# in built SQL thus enabling unit tests.


def create_channel(channel_id, processing_order=1, max_batch_size=100000, enabled=1, description="") -> str:
    return f"insert into sym_channel (channel_id, processing_order, max_batch_size, enabled, description) values ('{channel_id}', {processing_order}, {max_batch_size}, {enabled}, '{description}');"

def create_node_group(id: str, description: str) -> str:
    return f"insert into SYM_NODE_GROUP (node_group_id, description) values ('{id}', '{description}');"

def create_node_group_link(source: str, target: str, option: GroupLinkOptions) -> str:
    return f"insert into SYM_NODE_GROUP_LINK (source_node_group_id, target_node_group_id, data_event_action) values ('{source}', '{target}', '{option.value}');"

def create_channel_triggers(tables) -> str:
    """
    builds symmetric channel triggers for each table
    """
    # TODO
    pass

def create_single_channel_trigger(trigger_id: str, source_table: str, channel: str) -> str:
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

def create_triggers(groups) -> str:
    # TODO
    pass