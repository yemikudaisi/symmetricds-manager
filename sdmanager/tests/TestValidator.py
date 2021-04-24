import unittest
from sdmanager.core import Validator

class TestSQLValidator(unittest.TestCase):
    success = True , 'Valid'
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
        """Test that validation will fail if group key is not unique"""
        self.assertEqual(True, False)

if __name__ == '__main__':
    unittest.main()