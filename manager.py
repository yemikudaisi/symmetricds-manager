from string import Template
from core import Configurator

"""with open('templates\master.st', 'r') as template_file:
    src = Template(template_file.read())
    
    mapping = {'engine': 'John Doe', 'url': 'StackAbuse.com'}
    result = src.substitute(mapping)
    print(result)"""

configurator = Configurator('cnf.json')
print(configurator.generate_node_properties())