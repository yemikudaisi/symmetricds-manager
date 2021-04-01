from core import Configurator

configurator = Configurator('cnf.json', 'build')
print(configurator.generate_node_property_files())