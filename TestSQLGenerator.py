import unittest
from core import sql_generator
from core import GroupLinkOptions

class TestSQLGenerator(unittest.TestCase):

    def test_create_channel(self):
        self.assertEqual(sql_generator.create_channel('item', 1, 100000, 1, 'Item and pricing data'), \
            "insert into sym_channel (channel_id, processing_order, max_batch_size, enabled, description) values ('item', 1, 100000, 1, 'Item and pricing data');")

    def test_generate_node_gp_sql(self):
        self.assertEqual(sql_generator.create_node_group('store','A retail store node'), \
            'insert into SYM_NODE_GROUP (node_group_id, description) values (\'store\', \'A retail store node\');')
    
    def test_generate_node_gp_link(self):
        self.assertEqual(sql_generator.create_node_group_link('store','corp', GroupLinkOptions.PUSH), \
            'insert into SYM_NODE_GROUP_LINK (source_node_group_id, target_node_group_id, data_event_action) values (\'store\', \'corp\', \'P\');')

if __name__ == '__main__':
    unittest.main()