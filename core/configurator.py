import json
import os
import copy
from string import Template
from core import sql_generator

# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}

class Configurator():

    child_node_default_properties = {}
    parent_node_default_properties = {}

    def __init__(self, properties, output_dir=None) -> None:
        
        self.parse_properties(properties)
        result, txt = self.validate()
        if not result:
            raise ValueError(f"Validation failed: {txt}")
        
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
    
    def validate(self) -> tuple[bool, str]:
        """
        Validates the porperties required for a successful SymmetricDS replication

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

        if len(self.properties['nodes']) < 2:
           return False, 'minimum of 2 nodes required'
        
        groups = []
        group_required_keys = ['id' , 'sync']
        for group in self.properties['groups']:
            for key in group_required_keys:
                if not key in group:
                    return False, f"'{key}' key is required for group configuration"
            
            groups.append(group['id'])

            if group['sync'] not in ['P', 'W', 'R']:
                return False, 'Synchronization mode of P, W or R is required for group configuration'
        
        # Nodes validation
        node_required_keys = ['engine_name', 'external_id', 'type', 'db_driver', 'db_url', 'db_user', 'db_password']
        for node in self.properties['nodes']:
            for key in node_required_keys:
                if not key in node:
                    return False, f"'{key}' key is required for node configuration"
            
            if node['type'] not in ['parent', 'child', 'router'] in node:
                return False, "Type of 'parent', 'child' or 'router' is required for node configurations"
            
            if node['group_id'] not in groups:
                return False, f"Node {node['external_id']}'s assigned group '{node['group_id']}' is not in {groups}"
        
        return True, "success"

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
        sql_mappings = {}

        sql_mappings['channel_list'], sql_mappings['channel'], = self.build_channel_query()
        sql_mappings['group'], sql_mappings['group_links'], = self.build_group_queries()
        sql_mappings['table_triggers'], sql_mappings['initial_load_table_triggers'] = self.build_table_trigger_queries()
        sql_mappings['router'], = self.build_router_query()
        sql_mappings['router_triggers'], sql_mappings['initial_load_router_triggers'] = self.build_router_queries()

        self.generate_node_property_files()
        self.generate_sql_file()
    
    def build_channel_query(self) -> tuple[str, str]:
        channel_list =' '
        channel_sql = ''
        for idx,channel in enumerate(self.properties['channels']):

            channel_sql += f"{sql_generator.create_channel(channel['id'])}\n\n"
            channel_list += f"'{channel['id']}'"
            if (idx + 1) != len(self.properties['channels']):
                channel_list += ","

        return channel_list, channel_sql
    
    def build_group_queries(self) -> tuple[str, str]:
        gp_link_sql = ''
        gp_sql = ''
         # Groups
        for idx,group in enumerate(self.properties['groups']):
            # links
            groups_buffer = copy.copy(self.properties['groups'])
            self.groups_buffer.pop(idx)
            for gp in groups_buffer:
                gp_link_sql += f"{sql_generator.create_node_group_link(group['id'], gp['id'], group['sync'])}\n\n"
            
            gp_sql += f"{sql_generator.create_node_group(group['id'], ['description'])}\n\n"
        
        return gp_sql, gp_link_sql
    
    def build_table_trigger_queries(self) -> tuple[str, str]:
        table_trigger = ''
        load_only_table_triggers = ''
        for table in self.properties['tables']:
            table_trigger += f"{sql_generator.create_table_trigger(table)}\n\n"
            if 'initial_load' in table and table['initial_load']:
                load_only_table_triggers += f"{sql_generator.create_table_load_only_trigger(table)}\n\n"

        return table_trigger, load_only_table_triggers

    def build_router_query(self)  -> str:
        arch = self.properties['replication-arch']
        router_sql = ''

        if arch == 'bi-directional':
            router_sql = f"{sql_generator.create_router('parent_2_child')}\n\n"
            router_sql += f"{sql_generator.create_router('parent_2_master')}\n\n"
            router_sql += f"{sql_generator.create_router('parent_2_one_child')}\n\n"
        elif arch == 'parent-child':
            router_sql = sql_generator.create_router('parent_2_child')
        elif arch == 'child-parent':
            router_sql =sql_generator.create_router('child_2_parent')
        
        return router_sql
        
    def build_router_trigger_queries(self):
        router_triggers = ''
        return router_triggers

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
         self.generate_routers()



        
