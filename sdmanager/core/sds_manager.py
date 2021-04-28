import json
import os
import copy
import sys
from string import Template
from typing import Any
from sdmanager.core import Validator, sql_generator, utils, GroupType, Architecture

# Output: {'name': 'Bob', 'languages': ['English', 'Fench']}
class GroupNodeMediator:
    """Mediates node/group parent/child relationship

    Helps keep track of groups by parent or child
    in addition to identifying the master node
    """

    parent_group = None
    child_group = None
    def __init__(self, groups: list[dict[str, Any]]):
        """Acts as mediator for referencing a replication project's
        groups and node.

        Args:
            groups (list[dict[str, Any]]): A list of groups/node hierarchy for a replication project
        """
        for g in groups:
            nodes = []
            group = utils.new_object("Group", g)
            if group.type == GroupType.PARENT:
                self.parent_group = group
                nodes.append(utils.new_object("Node", g['nodes'][0])) # assuming validator has ensured there is one node in master group
            else:
                self.child_group = utils.new_object('Group', g)
                for node in g['nodes']:
                    try:
                        nodes.append(utils.new_object('Node', node))
                    except AttributeError as e:
                        print(e)
                        print(node)
            group.nodes.clear()
            group.nodes.extend(nodes)
        
    def __repr__(self) -> str:
        return f"parent:{self.parent_group.id}, child:{self.child_group.id}"

    @property
    def all_nodes(self) -> list[dict[str, Any]]:
        """ Generates a collection of all nodes regardless of group

        Returns:
            list[dict[str, Any]]: Collection of all replication nodes
        """
        return self.parent_group.nodes + self.child_group.nodes

class NotImplementedException(Exception):
    pass

class SdsManager():
    """Generates required SymmetricDS properties and sql query from JSON

    Adds the benfit of using a structured JSON data that visually
    reflects intended the replication architecture.
    """

    child_node_default_attributes = {}
    parent_node_default_attributes = {}

    def __init__(self, project_file_path, output_dir=None) -> None:
        """
        Args:
            properties ([type]): path to project JSON file
            output_dir ([type], optional): path to output directory for generated files

        Raises:
            ValueError: [description]
        """
        
        self.parse_project(project_file_path)
        result, txt = Validator(self.project).validate()
        if not result:
            raise ValueError(f"Validation Error: {txt}")

        self.mediator = GroupNodeMediator(self.project['groups'])

        self.output_dir = output_dir
        self.common_default_attributes = {
            "job_routing_period_time_ms":5000,
            "job_push_period_time_ms":10000,
            "job_pull_period_time_ms":10000
        }

        self.child_node_default_attributes = self.common_default_attributes

        self.parent_node_default_attributes = {
            **self.common_default_attributes, 
            **{
                "job_purge_period_time_ms":7200000,
                "auto_registration": "true",
                "initial_load_create_first":"true"
            }
        }


    def parse_project(self, path_to_json):
        """Parsea replication project from json file

        Parameter
        ---------
        path_to_json : str
            Path to JSON file to be parsed for properties
        """

        try:
            with open(path_to_json) as f:
                self.project = json.load(f)
        except Exception as e:
            sys.exit(f"Unable to upon supplied config file: {e}")
    
    def generate_files(self):
        self.generate_property_files()

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
        for idx,group in enumerate(self.project['groups']):
            # links
            groups_buffer = copy.copy(self.project['groups'])
            groups_buffer.pop(idx)
            for gp in groups_buffer:
                gp_link_sql += f"{sql_generator.create_node_group_link(group['id'], gp['id'], group['sync'])}\n\n"
            
            gp_sql += f"{sql_generator.create_node_group(group['id'], ['description'])}\n\n"
        
        return gp_sql, gp_link_sql
    
    def build_channel_query(self) -> tuple[str, str]:
        channel_list =' '
        channel_sql = ''
        for idx,channel in enumerate(self.project['channels']):

            channel_sql += f"{sql_generator.create_channel(channel['id'])}\n\n"
            channel_list += f"'{channel['id']}'"
            if (idx + 1) != len(self.project['channels']):
                channel_list += ","

        return channel_list, channel_sql
    
    def build_table_trigger_queries(self) -> tuple[str, str]:
        table_trigger = ''
        load_only_table_triggers = ''
        for table in self.project['tables']:
            table_trigger += f"{sql_generator.create_table_trigger(table)}\n\n"
            if 'initial_load' in table and table['initial_load']:
                load_only_table_triggers += f"{sql_generator.create_table_load_only_trigger(table)}\n\n"

        return table_trigger, load_only_table_triggers

    def build_router_query(self)  -> str:
        self.parent_2_child = f'{self.mediator.parent_group.id}_2_{self.mediator.child_group.id}'
        self.child_2_parent = f'{self.mediator.child_group.id}_2_{self.mediator.parent_group.id}'
        self.parent_2_one_child = f'{self.mediator.parent_group.id}_2_one_{self.mediator.child_group.id}'
        self.arch = self.project['project']['architecture']
        router_sql = ''

        if self.arch == Architecture.BIDIRECTIONAL:
            router_sql += f"{sql_generator.create_default_router(self.parent_2_child, self.mediator.parent_group.id, self.mediator.child_group.id)}\n\n"
            router_sql += f"{sql_generator.create_default_router(self.child_2_parent, self.mediator.child_group.id, self.mediator.parent_group.id)}\n\n"
            expression = f'{self.mediator.child_group.id.upper()}_ID=:EXTERNAL_ID or OLD_{self.mediator.child_group.id.upper()}_ID=:EXTERNAL_ID'
            router_sql += f"{sql_generator.create_column_router(self.parent_2_one_child, self.mediator.parent_group.id, self.mediator.child_group.id, expression)}\n\n"
        elif self.arch == Architecture.PARENT_2_CHILD:
            router_sql += f"{sql_generator.create_default_router(self.parent_2_child, self.mediator.parent_group.id, self.mediator.child_group.id)}\n\n"
        elif self.arch ==Architecture.CHILD_2_PARENT:
            router_sql += f"{sql_generator.create_default_router(self.child_2_parent, self.mediator.child_group.id, self.mediator.parent_group.id)}\n\n"
        return router_sql
        
    def build_router_trigger_queries(self):
        router_triggers = ''
        initial_load_router_triggers = ''

        for table in self.project['tables']:
            initial_load_router_triggers += self.build_router_initial_load_trigger_query(table)
            if self.architecture == 'parent<->parent':
                if table['route'] == 'parent-child':
                    router_triggers += f"{sql_generator.create_router_trigger(table['name'], self.parent_2_child)}\n\n"
                elif table['route'] == 'child-parent':
                    router_triggers += f"{sql_generator.create_router_trigger(table['name'], self.child_2_parent)}\n\n"

            elif self.architecture == 'parent->child':
                 router_triggers += f"{sql_generator.create_router_trigger(table['name'], self.parent_2_child)}\n\n"

            elif self.architecture == 'child<-parent':
                 router_triggers += f"{sql_generator.create_router_trigger(table['name'], self.child_2_parent)}\n\n"

        return router_triggers, initial_load_router_triggers
    
    def build_router_initial_load_trigger_query(self, table):
        query = ''

        if 'initial_load' in table and table['initial_load'] == 1:
            if table['initial_load_route'] == 'parent->child':
                query = f"{sql_generator.create_router_trigger(table['name'], 'parent_2_child')}\n\n"
            elif table['initial_load_route'] == 'child->parent':
                query = f"{sql_generator.create_router_trigger(table['name'], 'child_2_parent')}\n\n"
        
        return query

    def generate_property_files(self):
        print(os.environ['SDMANAGER_BASE_DIR'])
        """
        Generates property file for each node
        """
        for node in self.project['nodes']:
            result = ''
            parameters = {}

            if node['type'] == GroupType.PARENT:
                parameters = { **self.parent_node_default_attributes, **node}
            else:
                parameters = { **self.child_node_default_attributes, **node}

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