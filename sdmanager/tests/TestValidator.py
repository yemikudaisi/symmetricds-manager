import unittest
from sdmanager.core import Validator

class TestValidator(unittest.TestCase):
    success = True , 'Valid'

    ##########################
    """TOP LEVEL KEYS TESTS"""
    ##########################
    def test_fail_if_main_key_absent(self):
        """Test that validation will fail if any top level key is absent"""
        props = {
            "groups": [],
            "nodes": [],
            'replication-arch': [],
            'channels': []
        }
        validator = Validator(props)
        self.assertEqual(validator.validate_primary_keys(), \
            (False, "'tables' must be configured."))
    
    def test_pass_if_main_keys_present(self):
        """Test that validation will pass if all top level keys is present"""
        props = {
            "groups": [],
            "nodes": [],
            'replication-arch': [],
            'channels': [],
            'tables': []
        }
        validator = Validator(props)
        self.assertEqual(validator.validate_primary_keys(), self.success)
        
    #################
    """GROUP TESTS"""
    #################

    def test_fail_if_less_than_two_gps(self):
        """Test that validation will fail if one or more required group keys are absent"""
        props = {
            "groups": [],
        }
        validator = Validator(props)
        self.assertEqual(validator.validate_groups(),
            (False, "Minimum of 2 groups is required")
        )
    
    def test_fail_if_reqd_gp_keys_absent(self):
        """Test that validation will fail if any required group keys is absent"""
        props = {
            "groups": [{'id': ''},{'id': '','sync': ''}]
        }
        validator = Validator(props)
        self.assertEqual(validator.validate_groups(), 
            (False, "'sync' key is required for group configuration")
        )
    def test_fail_if_reqd_group_id_empty(self):
        """Tests that validation will fail if a group ID field value is empty"""
        props = {
            "groups": [{'id': 'pak', 'sync':'W'},{'id': '','sync': 'P'}]
        }
        validator = Validator(props)
        self.assertEqual(validator.validate_groups(), 
            (False, "Required group field (id) must not be empty")
        )

    def test_fail_if_invalid_gp_sync(self):
        """Test that validation will fail for invalid group 'sync' property"""
        props = {
            "groups": [{'id': '23', 'sync':'X'},{'id': 're','sync': 'P'}]
        }
        validator = Validator(props)
        self.assertEqual(validator.validate_groups(), 
            (False, "Synchronization mode of P, W or R is required for group configuration")
        )
    
    def test_fail_if_not_unique_gp_id(self):        
        """Test that validation will fail if duplicate group id exists"""
        props = {
            "groups": [{'id':'1','sync':'P'},{'id':'1','sync':'P'}],
        }
        validator = Validator(props)
        self.assertEqual(validator.validate_groups(), (False, 'Group ID must be unique'))
    
    def test_pass_gp_validation(self):        
        """Test that validation passes if all group requirement are met"""
        props = {
            "groups": [{'id':'1','sync':'P'},{'id':'2','sync':'P'}],
        }
        validator = Validator(props)
        self.assertEqual(validator.validate_groups(), (True, 'Valid'))
    
    #################
    """NODES TESTS"""
    #################
    _DB_DRIVER = "com.mysql.jdbc.Driver"
    _DB_URL  = "jdbc:mysql://localhost/corp?tinyInt1isBit=false"
    _DB_USER = "symmetric"
    _DB_PASSWORD = "symmetric"

    def test_fail_if_less_than_two_nodes(self):
        """Tests that validation will faill if nodes are less than 2"""
        prop = {
            "nodes": [{}]
        }
        validator = Validator(prop)
        validator.groups = ['corp', 'store']
        self.assertEqual(validator.validate_nodes(), 
            (False, 'Minimum of 2 nodes required.')
        )

    def test_fail_if_reqd_node_field_absent(self):
        """Tests that validation will fail if any required group fields are absent"""
        node =  {
            "group_id": "corp",
            "type": "parent",
            "external_id": "000",
            "db_driver": self._DB_DRIVER,
            "db_url": self._DB_URL,
            "db_user": self._DB_USER,
            "db_password": self._DB_PASSWORD
        }
        validator = Validator({})
        validator.groups = ['corp', 'store']
        self.assertEqual(validator.validate_node(node), 
            (False, "'engine_name' field is required for node configuration")
        )
    
    def test_fail_if_reqd_node_field_empty(self):
        """Tests that validation will fail if a required field's value is empty"""
        node =  {
            "group_id": "car",
            "engine_name": "",
            "type": "parent",
            "external_id": "000",
            "db_driver": self._DB_DRIVER,
            "db_url": self._DB_URL,
            "db_user": self._DB_USER,
            "db_password": self._DB_PASSWORD
        }
        validator = Validator({})
        validator.groups = ['corp', 'store']
        self.assertEqual(validator.validate_node(node), 
            (False, "Required node field (engine_name) must not be empty")
        )
    
    def test_fail_if_invalid_node_type(self):
        """Tests that validation will faill if an invalid node type is supplied"""
        node =  {
            "engine_name": 'corp',
            "group_id": "corp",
            "type": "kalesi",
            "external_id": "000",
            "db_driver": self._DB_DRIVER,
            "db_url": self._DB_URL,
            "db_user": self._DB_USER,
            "db_password": self._DB_PASSWORD,
            "url": ""
        }
        validator = Validator({})
        validator.groups = ['corp', 'store']
        self.assertEqual(validator.validate_node(node), 
            (False, "Type of 'parent', 'child' or 'router' is required for node configurations")
        )
    
    def test_fail_if_no_node_url(self):
        """Tests that validation will faill if no URL value"""
        node =  {
            "engine_name": 'caronwi',
            "group_id": "corp",
            "type": "parent",
            "external_id": "000",
            "db_driver": self._DB_DRIVER,
            "db_url": self._DB_URL,
            "db_user": self._DB_USER,
            "db_password": self._DB_PASSWORD
        }
        validator = Validator({})
        validator.groups = ['corp', 'store']
        self.assertEqual(validator.validate_node(node), 
            (False, 'A parent node must have a synchronization url')
        )
    
    def test_fail_if_less_than_two_groups(self):
        """Tests that validation will fail if nodes are less than 2"""
        prop = {
            "nodes": [
                {
                    "engine_name": 'caronwi',
                    "group_id": "corp",
                    "type": "parent",
                    "external_id": "000",
                    "db_driver": self._DB_DRIVER,
                    "db_url": self._DB_URL,
                    "db_user": self._DB_USER,
                    "db_password": self._DB_PASSWORD,
                    "url": ""
                },
                {
                    "engine_name": 'caronwi',
                    "group_id": "corp",
                    "type": "parent",
                    "external_id": "000",
                    "db_driver": self._DB_DRIVER,
                    "db_url": self._DB_URL,
                    "db_user": self._DB_USER,
                    "db_password": self._DB_PASSWORD,
                    "url": ""
                }
            ]
        }
        validator = Validator(prop)
        validator.groups = ['corp', 'store']
        self.assertEqual(validator.validate_nodes(), 
            (False, 'Minimum of 2 node groups required.')
        )

    def test_fail_if_duplicate_node_engine_name(self):
        """Tests that validation will fail if there are duplicate node engine name"""
        prop = {
            "nodes": [
                {
                    "engine_name": 'caronwi',
                    "group_id": "corp",
                    "type": "parent",
                    "external_id": "000",
                    "db_driver": self._DB_DRIVER,
                    "db_url": self._DB_URL,
                    "db_user": self._DB_USER,
                    "db_password": self._DB_PASSWORD,
                    "url": ""
                },
                {
                    "engine_name": 'caronwi',
                    "group_id": "store",
                    "type": "parent",
                    "external_id": "000",
                    "db_driver": self._DB_DRIVER,
                    "db_url": self._DB_URL,
                    "db_user": self._DB_USER,
                    "db_password": self._DB_PASSWORD,
                    "url": ""
                }
            ]
        }
        validator = Validator(prop)
        validator.groups = ['corp', 'store']
        self.assertEqual(validator.validate_nodes(), 
            (False, 'Node engine name must be unique.')
        )
    
    def test_fail_if_duplicate_node_external_id(self):
        """Tests that validation will fail if there are duplicate node external IDs"""
        prop = {
            "nodes": [
                {
                    "engine_name": 'corp-000',
                    "group_id": "corp",
                    "type": "parent",
                    "external_id": "000",
                    "db_driver": self._DB_DRIVER,
                    "db_url": self._DB_URL,
                    "db_user": self._DB_USER,
                    "db_password": self._DB_PASSWORD,
                    "url": ""
                },
                {
                    "engine_name": 'store-000',
                    "group_id": "store",
                    "type": "parent",
                    "external_id": "000",
                    "db_driver": self._DB_DRIVER,
                    "db_url": self._DB_URL,
                    "db_user": self._DB_USER,
                    "db_password": self._DB_PASSWORD,
                    "url": ""
                }
            ]
        }
        validator = Validator(prop)
        validator.groups = ['corp', 'store']
        self.assertEqual(validator.validate_nodes(), 
            (False, 'Node external ID must be unique.')
        )


if __name__ == '__main__':
    unittest.main()