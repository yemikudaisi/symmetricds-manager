from core import ReplicationBuilder
from core.sql_generator import create_router, create_node_group_link
from core import Validator

if __name__ == '__main__':
    v = Validator({})
    print(v.validate())
    # builder = ReplicationBuilder('cnf.json', 'build')
    # builder.generate_files();