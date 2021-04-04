import unittest
from manager import manager
from click.testing import CliRunner

class TestCommands(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    def test_set_config_key_combination(self):
        result = self.runner.invoke(manager.get_config, ['foo'])
        self.assertEqual(result.output, "Comibation of INI section and key separated by '.' required.\n")

    def test_set_config_section_exist(self):
        result = self.runner.invoke(manager.get_config, ['foo.bar'])
        self.assertEqual(result.output, "INI section 'foo' does not exist.\n")

if __name__ == '__main__':
    unittest.main()