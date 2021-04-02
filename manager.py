from core import Configurator
from core.sql_generator import create_router, create_node_group_link
import copy

configurator = Configurator('cnf.json', 'build')
x, y = configurator.build_router_trigger_queries()
print(x)
print(y)

