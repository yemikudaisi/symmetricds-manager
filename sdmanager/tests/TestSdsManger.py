import os
import unittest
from sdmanager.core import SdsManager

class TestSdsManager(unittest.TestCase):

    def setUp(self) -> None:
        self.manager = SdsManager(os.path.join('samples','bidirectional.json'))
        return super().setUp()

    def test_initialize(self):
        expected ="""insert into sym_node_group (node_group_id) values ('corp');
insert into sym_node_group (node_group_id) values ('store');"""

        self.assertEqual(self.manager.build_group_queries(), expected)

if __name__ == '__main__':
    unittest.main()