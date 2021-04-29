import os
import unittest
from sdmanager.core import SdsManager

class TestSdsManager(unittest.TestCase):

    def setUp(self) -> None:
        self.manager = SdsManager(os.path.join('samples','bidirectional.json'))
        self.maxDiff = None
        super().setUp()

    def test_initialization_as_expected(self):
        """Test that SDS Manager initializes as expected"""

        self.assertEqual(str(self.manager), str({"project file name":"bidirectional.json", "project name":"VINO"}))

    def test_group_query(self):
        """Tests that the generated group query is correct"""

        expected_gp = """insert into SYM_NODE_GROUP (node_group_id, description) values ('corp', 'Company Corporation');\n\ninsert into SYM_NODE_GROUP (node_group_id, description) values ('store', 'Company branch stores');\n\n"""

        self.assertEqual(self.manager.build_group_queries()[0], expected_gp)
    
    def test_group_link_query(self):
        """Test that the generated group link query is accurate"""

        expected_gp_links = """insert into SYM_NODE_GROUP_LINK (source_node_group_id, target_node_group_id, data_event_action) values ('corp', 'store', 'P');\n\ninsert into SYM_NODE_GROUP_LINK (source_node_group_id, target_node_group_id, data_event_action) values ('store', 'corp', 'W');\n\n"""
        #print(self.manager.build_group_queries()[0])
        self.assertEqual(self.manager.build_group_queries()[1], expected_gp_links)

if __name__ == '__main__':
    unittest.main()