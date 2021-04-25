import json
import os
import copy
import sys
from string import Template
from typing import Any
from sdmanager.core import Validator, sql_generator

# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
class GroupNodeMediator:

    master_group_id: str = ''
    child_groups_id: list[str] = []
    master_node: dict[str, str] = {}
    children_nodes: list[dict[str, str]] = []
    def __init__(self, groups: list[dict[str, Any]]):
        """Acts as mediator for referencing a replication project's
        groups and node.

        Args:
            groups (list[dict[str, Any]]): A list of groups/node hierarchy for a replication project
        """
        for g in groups:
            if g['type'] == 'parent':
                self.master_group_id = g['id']
                # assuming validator has ensured there is one node in
                # master group
                self.master_node = g['nodes'][0]
            else:
                for n in g['nodes']:
                    self.children_nodes.append(n)
                self.child_groups_id.append(g['id'])
    @property
    def all_nodes(self) -> list[dict[str, Any]]:
        """ Generates a collection of all nodes regardless of group

        Returns:
            list[dict[str, Any]]: Collection of all replication nodes
        """
        return [self.master_node] + self.children_nodes

class NotImplementationException(Exception):
    pass
class ReplicationBuilder():
    """Generates SymmetricDS replication files based on JSON config
    """

    child_node_default_properties = {}
    parent_node_default_properties = {}

    def __init__(self, properties, output_dir=None) -> None:
        
        self.parse_properties(properties)
        result, txt = Validator(self.properties).validate()
        if not result:
            raise ValueError(f"Validation Error: {txt}")

        self.mediator = GroupNodeMediator(self.properties['groups'])

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
        try:
            with open(path_to_json) as f:
                self.properties = json.load(f)
        except Exception as e:
            sys.exit(f"Unable to upon supplied config file: {e}")
    
    def generate_files(self):
        self.generate_node_property_files()

        sql_mappings = {}
        sql_mappings['group'], sql_mappings['group_links'], = self.build_group_queries()
        sql_mappings['channels_list'], sql_mappings['channel'], = self.build_channel_query()
        sql_mappings['table_triggers'], sql_mappings['initial_load_table_triggers'] = self.build_table_trigger_queries()
        sql_mappings['router'] = self.build_router_query()
        sql_mappings['router_triggers'], sql_mappings['initial_load_router_triggers'] = self.build_router_trigger_queries()

        self.generate_sql_file(sql_mappings)
    
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
    
    def build_channel_query(self) -> tuple[str, str]:
        channel_list =' '
        channel_sql = ''
        for idx,channel in enumerate(self.properties['channels']):

            channel_sql += f"{sql_generator.create_channel(channel['id'])}\n\n"
            channel_list += f"'{channel['id']}'"
            if (idx + 1) != len(self.properties['channels']):
                channel_list += ","

        return channel_list, channel_sql
    
    def build_table_trigger_queries(self) -> tuple[str, str]:
        table_trigger = ''
        load_only_table_triggers = ''
        for table in self.properties['tables']:
            table_trigger += f"{sql_generator.create_table_trigger(table)}\n\n"
            if 'initial-load' in table and table['initial-load']:
                load_only_table_triggers += f"{sql_generator.create_table_load_only_trigger(table)}\n\n"

        return table_trigger, load_only_table_triggers

    def build_router_query(self)  -> str:
        arch = self.properties['project']['architecture']
        router_sql = ''

        if arch == 'parent->child':
            for g in self.mediator.child_groups_id:
                router_sql += f"{sql_generator.create_default_router(f'{self.mediator.master_group_id}_2_{g}', self.mediator.master_group_id, g)}\n\n"
                router_sql += f"{sql_generator.create_default_router(f'{g}_2_{self.mediator.master_group_id}', g, self.mediator.master_group_id)}\n\n"
                expression = 'STORE_ID=:EXTERNAL_ID or OLD_STORE_ID=:EXTERNAL_ID'
                router_sql += f"{sql_generator.create_column_router(f'{self.mediator.master_group_id}_2_one_{g}', self.mediator.master_group_id, g, expression)}\n\n" #TODO Implement column router generator
        elif arch == 'parent<-child':
            for g in self.mediator.child_groups_id:
                router_sql += f"{sql_generator.create_default_router(f'{self.mediator.master_group_id}_2_{g}', self.mediator.master_group_id, g)}\n\n"
                router_sql += f"{sql_generator.create_default_router(f'{g}_2_{self.mediator.master_group_id}', g, self.mediator.master_group_id)}\n\n"
        elif arch =='parent<->parent':
            raise Exception('Parent to parent architecture has not been implemented')
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

        if 'initial-load' in table and table['initial-load'] == 1:
            if table['initial-load-route'] == 'parent-child':
                query = f"{sql_generator.create_router_trigger(table['name'], 'parent_2_child')}\n\n"
            elif table['initial-load-route'] == 'child-parent':
                query = f"{sql_generator.create_router_trigger(table['name'], 'child_2_parent')}\n\n"
        
        return query

    def generate_node_property_files(self):
        print(os.environ['SDMANAGER_BASE_DIR'])
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
                with open(os.path.join(os.environ['SDMANAGER_BASE_DIR'], 'templates', f"{node['type']}.st"), 'r') as template_file:
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
            with open(os.path.join(os.environ['SDMANAGER_BASE_DIR'], 'templates', 'sql.st'), 'r') as template_file:
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