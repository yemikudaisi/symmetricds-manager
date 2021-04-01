from core import Configurator
from core.sql_generator import create_single_channel_trigger

configurator = Configurator('cnf.json', 'build')
print(configurator.generate_node_property_files())
# print(create_single_channel_trigger('some_trigger','some','some'))