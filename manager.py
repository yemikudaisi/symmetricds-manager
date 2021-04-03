import configparser
from core import ReplicationBuilder
from core.sql_generator import create_router, create_node_group_link
from core import Validator

def run():
    config = configparser.ConfigParser()
    config.sections()
    config.read('conf.ini')
    symmetric_home = None
    if "" in config.sections():
        symmetric_home = config['SYMMETRICDS']['HomeDirectory']
  
    v = Validator({})
    # print(v.validate())
    builder = ReplicationBuilder('cnf.json', 'build')
    builder.generate_files();

if __name__ == '__main__':
    run()
