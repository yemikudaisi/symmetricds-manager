import unittest
from core import sql_generator

class TestSQLGenerator(unittest.TestCase):

    def test_create_channel(self):
        self.assertEqual(sql_generator.create_channel('item', 1, 100000, 1, 'Item and pricing data'), \
            "insert into sym_channel (channel_id, processing_order, max_batch_size, enabled, description) values ('item', 1, 100000, 1, 'Item and pricing data');")

    def test_generate_node_gp_sql(self):
        self.assertEqual(sql_generator.create_node_group('store','A retail store node'), \
            'insert into SYM_NODE_GROUP (node_group_id, description) values (\'store\', \'A retail store node\');')
    
    def test_generate_node_gp_link(self):
        self.assertEqual(sql_generator.create_node_group_link('store','corp', 'P'), \
            'insert into SYM_NODE_GROUP_LINK (source_node_group_id, target_node_group_id, data_event_action) values (\'store\', \'corp\', \'P\');')
    
    def test_create_table_trigger(self):
        self.assertEqual(sql_generator.create_table_trigger(
            {
                "name": "item_selling_price",
                "channel": "item"
            }), \
            "insert into sym_trigger (trigger_id,source_table_name,channel_id,last_update_time,create_time) values ('item_selling_price','item_selling_price','item',current_timestamp,current_timestamp);")
    
    def test_create_load_only_trigger(self):
        self.assertEqual(sql_generator.create_table_load_only_trigger(
            {
                "name": "sale_transaction",
                "channel": "sale_transaction",
                "route": "child-parent",
                "initial-load": 1,
                "initial-load-route": "parent-child"
            }), \
            "insert into sym_trigger (trigger_id,source_table_name,channel_id, sync_on_insert, sync_on_update, sync_on_delete,last_update_time,create_time) values ('sale_transaction_parent','sale_transaction','sale_transaction',0,0,0,current_timestamp,current_timestamp);")

    def test_create_router(self):
        self.assertEqual(sql_generator.create_router('corp_2_store', 'corp', 'store', 'default'), \
            "insert into sym_router (router_id,source_node_group_id,target_node_group_id,router_type,create_time,last_update_time) values ('corp_2_store','corp','store','default',current_timestamp,current_timestamp);")
    
    def test_create_router_trigger(self):
        
        self.assertEqual(sql_generator.create_router_trigger('item','corp_2_store', 100), \
            "insert into sym_trigger_router (trigger_id,router_id,initial_load_order,last_update_time,create_time) values ('item','corp_2_store',100,current_timestamp,current_timestamp);")

if __name__ == '__main__':
    unittest.main()