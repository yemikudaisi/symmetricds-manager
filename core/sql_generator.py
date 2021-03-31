from core import GroupLinkOptions

def create_node_group(id: str, description: str) -> str:
    return f"insert into SYM_NODE_GROUP (node_group_id, description) values ('{id}', '{description}');"

def create_node_group_link(source: str, target: str, option: GroupLinkOptions) -> str:
    return f"insert into SYM_NODE_GROUP_LINK (source_node_group_id, target_node_group_id, data_event_action) values ('{source}', '{target}', '{option.value}');"
