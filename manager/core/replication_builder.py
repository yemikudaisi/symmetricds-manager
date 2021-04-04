import json
import os
import copy
from string import Template
from manager.core import sql_generator, validator
from manager.core import Validator

# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}

class ReplicationBuilder():
    """Generates SymmetricDS replication files based on JSON config
    """

    child_node_default_properties = {}
    parent_node_default_properties = {}

    def __init__(self, properties, output_dir=None) -> None:
        
        self.parse_properties(properties)
        result, txt = Validator(self.properties).validate()
        if not result:
            raise ValueError(f"Validation failed: {txt}")

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

    def parse_properties(self, path_to_json):
        """
        Parameter
        ---------
        json : str
            Path to JSON file to be parsed for properties
        """
        with open(path_to_json) as f:
            self.properties = json.load(f)

    
    def generate_files(self):
        self.generate_node_property_files()

        sql_mappings = {}
        sql_mappings['channels_list'], sql_mappings['channel'], = self.build_channel_query()
        sql_mappings['group'], sql_mappings['group_links'], = self.build_group_queries()
        sql_mappings['table_triggers'], sql_mappings['initial_load_table_triggers'] = self.build_table_trigger_queries()
        sql_mappings['router'] = self.build_router_query()
        sql_mappings['router_triggers'], sql_mappings['initial_load_router_triggers'] = self.build_router_trigger_queries()

        self.generate_sql_file(sql_mappings)
    
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
            groups_buffer.pop(idx)
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
            router_sql = f"{sql_generator.create_router('parent_2_child', self.parent_group, self.child_group)}\n\n"
            router_sql += f"{sql_generator.create_router('child_2_parent', self.child_group, self.parent_group)}\n\n"
            router_sql += f"{sql_generator.create_router('parent_2_one_child', self.child_group, self.parent_group, 'column')}\n\n" #TODO Implement column router generator
        elif arch == 'parent-child':
            router_sql = sql_generator.create_router('parent_2_child')
        elif arch == 'child-parent':
            router_sql =sql_generator.create_router('child_2_parent')
        
        return router_sql
        
    def build_router_trigger_queries(self):
        router_triggers = ''
        initial_load_router_triggers = ''

        for table in self.properties['tables']:
            initial_load_router_triggers += self.build_router_initial_load_trigger_query(table)
            if self.properties['replication-arch'] == 'bi-directional':
                if table['route'] == 'parent-child':
                    router_triggers += f"{sql_generator.create_router_trigger(table['name'], 'parent_2_child')}\n\n"
                elif table['route'] == 'child-parent':
                    router_triggers += f"{sql_generator.create_router_trigger(table['name'], 'child_2_parent')}\n\n"

            elif self.properties['replication-arch'] == 'parent-child':
                 router_triggers += f"{sql_generator.create_router_trigger(table['name'], 'parent_2_child')}\n\n"

            elif self.properties['replication-arch'] == 'child-parent':
                 router_triggers += f"{sql_generator.create_router_trigger(table['name'], 'child_2_parent')}\n\n"

        return router_triggers, initial_load_router_triggers
    
    def build_router_initial_load_trigger_query(self, table):
        query = ''

        if 'initial_load' in table and table['initial_load'] == 1:
            if table['initial_load_route'] == 'parent-child':
                query = f"{sql_generator.create_router_trigger(table['name'], 'parent_2_child')}\n\n"
            elif table['initial_load_route'] == 'child-parent':
                query = f"{sql_generator.create_router_trigger(table['name'], 'child_2_parent')}\n\n"
        
        return query

    parent_group = ''
    child_group = ''
    def generate_node_property_files(self):
        """
        Generates property file for each node
        """
        for node in self.properties['nodes']:
            result = ''
            parameters = {}

            if node['type'] == 'parent':
                self.parent_group = node['group_id']
                parameters = { **self.parent_node_default_properties, **node}
            else:
                self.child_group = node['group_id']
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

            if self.output_dir != None:
                # Writes propertes file for node
                with open(os.path.join(self.output_dir, f'{node["engine_name"]}.properties'), 'w') as node_properties_file:
                                node_properties_file.writelines(result)
            else:
                print(result)
    
    def generate_sql_file(self, mappings):
        """
        Generates SQL queries necessary for SymmetricDS to function appropriately
        """
        result =''
        try:
            with open('templates\sql.st', 'r') as template_file:
                src = Template(template_file.read())            
                result = src.substitute(mappings)
        except FileNotFoundError:
            print(f"SQL template file not found")
        except Exception as e:
            print(f"Unable to generate sql template: {e}")

        if self.output_dir != None:
            # Writes propertes file for node
            with open(os.path.join(self.output_dir, 'symmetricds.sql'), 'w') as node_properties_file:
                node_properties_file.writelines(result)
        else:
            print(result)



        
