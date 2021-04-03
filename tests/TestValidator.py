import unittest
from core import Validator

class TestSQLGenerator(unittest.TestCase):

    MBC = ' must be configured.'
    def test_groups_key_reqd(self):
        validator = Validator({})
        self.assertEqual(validator.validate(), \
            (False, f"'groups'{self.MBC}"))
    
    def test_nodes_key_reqd(self):
        validator = Validator({"groups":[]})
        self.assertEqual(validator.validate(), \
            (False, f"'nodes'{self.MBC}"))
    
    def test_repl_arch_key_reqd(self):
        conf = {
            "groups":[],
            "nodes": []
        }
        
        validator = Validator(conf)
        self.assertEqual(validator.validate(), \
            (False, f"'replication-arch'{self.MBC}"))

    def test_channels_key_reqd(self):
        conf = {
            "groups":[],
            "nodes": [],
            "replication-arch": ""
        }
        validator = Validator(conf)
        self.assertEqual(validator.validate(), \
            (False, f"'channels'{self.MBC}"))

    def test_tables_key_reqd(self):
        conf = {
            "groups":[],
            "nodes": [],
            "replication-arch": "",
            "channels": ""
        }
        validator = Validator(conf)
        self.assertEqual(validator.validate(), \
            (False, f"'tables'{self.MBC}"))

if __name__ == '__main__':
    unittest.main()