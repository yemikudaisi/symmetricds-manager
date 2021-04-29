import unittest
from sdmanager.core import GroupNodeMediator

class TestGroupMediator(unittest.TestCase):

    group_config =  [
        {
            "id":"store",
            "description": "Akilli branch stores",
            "sync": 1,
            "type": "child",
            "nodes":[
                {
                    "engine_name": "store-001",
                    "external_id": "001",
                    "db_driver": "com.mysql.jdbc.Driver",
                    "db_url": "jdbc:mysql://localhost/sotre?tinyInt1isBit=false",
                    "db_user": "symmetric",
                    "db_password": "symmetric",
                    "url": "http://localhost:31415/sync/corp-000"
                }
            ]
        },
        {
            "id": "corp",
            "description": "Akilli Corporation",
            "sync": "P",
            "type": 0,
            "nodes": [
                {
                    "engine_name": "corp-000",
                    "external_id": "000",
                    "db_driver": "com.mysql.jdbc.Driver",
                    "db_url": "jdbc:mysql://localhost/corp?tinyInt1isBit=false",
                    "db_user": "symmetric",
                    "db_password": "symmetric",
                    "is_server": 1,
                    "url": "http://localhost:31415/sync/corp-000"
                }
            ]
        }
    ]
    mediator = GroupNodeMediator(group_config)

    def test_initialize(self):
        """Test GroupNodeMediator initialization"""
        self.assertEqual(str(self.mediator), "parent:corp, child:store")

    def test_that_parent_group_node_is_accesible(self):
        """Tests that the child group nodes are accessible through the object property"""
        self.assertEqual(self.mediator.parent_group.nodes[0].external_id, "000")

    def test_that_child_group_node_is_accesible(self):
        """Tests that the child group nodes are accessible through the object property"""
        self.assertEqual(self.mediator.child_group.nodes[0].external_id, "001")

if __name__ == '__main__':
    unittest.main()