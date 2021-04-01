import json
import os
from string import Template

# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}

class Configurator():

    child_node_default_properties = {}
    parent_node_default_properties = {}

    def __init__(self, properties=None, output_dir=None) -> None:
        
        if properties is not None:
            self.parse_properties(properties)
            self.from_json = True
        
        if output_dir is None:
            self.output_dir = os.getcwd()
        else:
            self.output_dir = output_dir

        self.common_default_properties = {
            "job_routing_period_time_ms":5000,
            "job_push_period_time_ms":10000,
            "job_pull_period_time_ms":10000
        }

        self.child_node_default_properties = self.common_default_properties

        self.parent_node_default_properties = {
            **self.common_default_properties, 
            **{
                "job_purge_period_time_ms":7200000,
                "auto_registration": "true",
                "initial_load_create_first":"true"
            }
        }
    
    def validate(self):
        """
        Validates the porperties required for SymmetricDS replication

        2-Tier Architecture Validation
        ------------------------------
        check inital load tables and confirm a direction 
        is specified possible give errors and with line numbers
        if configuration is parsed from JSON file
        
        - Ensure parent and child nodes contain sync and registration url respectively
        - Ensure assigned groups in node properties exit as group
        - if duplicate Node external IDs exists in replication properties fail
        - if duplicate node engine names exists in replication properties, fail
        - if node type not 'parent' or 'child' fail

        Otherwise, check that all other required parameters with 
        the replication properties

        Returns
        -------
        bool
            The object's properties validation result
        
        list
            Error messages
        """

        pass

    def parse_properties(self, path_to_json):
        """
        Parameter
        ---------
        json : str
            Path to JSON file to be parsed for properties
        """
        with open(path_to_json) as f:
            self.properties = json.load(f)

    def generate_sysmmetric_ds_files(self):
        """
        """
        self.validate()
        self.generate_node_property_files()
        self.generate_sql_file()

    def generate_node_property_files(self):
        """
        Generates property file for each node
        """
        for node in self.properties['nodes']:
            result = ''
            parameters = {}

            if node['type'] == 'parent':
                parameters = { **self.parent_node_default_properties, **node}
            else:
                parameters = { **self.child_node_default_properties, **node}

            # Substite template placeholders with generated parameter
            try:
                with open(f"templates\{node['type']}.st", 'r') as template_file:
                    src = Template(template_file.read())            
                    result = src.substitute(parameters)
            except FileNotFoundError:
                print(f"Template for {node['type']} was not found")
            except Exception:
                print(f"Unable to generate {node['type']} template for {node['external_id']}")

            # Writes propertes file for node
            with open(os.path.join(self.output_dir, f'{node["engine_name"]}.properties'), 'w') as node_properties_file:
                            node_properties_file.writelines(result)
    
    def generate_sql_file(self):
         """
         Generates SQL queries necessary for SymmetricDS to function appropriately
         """
         pass

        
