from sdmanager.core import Architecture, GroupType, utils


class Validator():

    def __init__(self, config):
        self.project = config
    
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

        - check that only one group is parent
        - check that parent group contains only one node

        Otherwise, check that all other required parameters with 
        the replication properties

        Returns
        -------
        bool
            The object's properties validation result
        
        list
            Error messages
        """

        keys = self.validate_primary_keys()
        if not keys[0]:
            return keys
        group = self.validate_groups()
        if not group[0]:
            return group
        node = self.validate_nodes()
        if not node[0]:
            return node
        table = self.validate_table()
        if not table[0]:
            return table
        
        return self.success()
    
    def success(self) -> tuple[ bool, str] :
        """Generic validation success response

        Returns:
            tuple[ bool, str]: Validation state and message
        """

        return True , 'Valid'

    def validate_primary_keys(self) -> tuple[bool, str]:
        """Checks that all required main keys exist in config

        Returns:
            tuple[bool, str]: Validation result and message
        """
        required_primary_keys = ['groups', 'architecture', 'channels', 'tables']
        for key in required_primary_keys:
            if not key in self.project:
                return False, f"'{key}' must be configured."
        
        return self.success()

    def validate_groups(self) -> tuple[ bool, str]:
        if len(self.project['groups']) < 2:
           return False, 'Minimum of 2 groups is required'

        self.groups = []
        group_required_keys = ['id' , 'sync', 'nodes']
        for group in self.project['groups']:
            for key in group_required_keys:
                if not key in group:
                    return False, f"'{key}' key is required for group configuration"
            
            if not group['id']:
                return False, 'Required group field (id) must not be empty'

            if not len(group['nodes']) > 0:
                return False, 'Groups must contain at least one node.'
            
            self.groups.append(group['id'])

            if group['sync'] not in ['P', 'W', 'R']:
                return False, 'Synchronization mode of P, W or R is required for group configuration'
        
        group_ids = [gp['id'] for gp in self.project['groups']]
        contains_duplicates = any(group_ids.count(element) > 1 for element in group_ids)
        if contains_duplicates:
            return False, 'Group ID must be unique'
        
        return self.success()
    
    def validate_nodes(self) -> tuple[ bool, str]:

        nodes = []
        for group in self.project['groups']:
            import copy
            tmp = copy.copy([utils.append_to_dict(n, 'group_type', group['type']) for n in group['nodes']])
            nodes.extend(tmp)
        
        for node in nodes:
            result, error = self.validate_node(node)
            if not result:
                return result, error

        node_engine_names = [n['engine_name'] for n in nodes]
        contains_duplicate_engine_name = any(node_engine_names.count(element) > 1 for element in node_engine_names)
        if contains_duplicate_engine_name:
            return False, 'Node engine name must be unique.'
        
        node_external_id_list = [n['external_id'] for n in nodes]
        contains_duplicate_external_id= any(node_external_id_list.count(element) > 1 for element in node_external_id_list)
        if contains_duplicate_external_id:
            return False, 'Node external ID must be unique.'
            
        return self.success()
    
    def validate_node(self, node):
        """Validates a single node

        Args:
            node (dict[str, str]): The node to validate

        Returns:
            tuple[bool, str]: A tuple of validation result and message
        """
        node_required_keys = ['engine_name', 'external_id', 'db_driver', 'db_url', 'db_user', 'db_password']
        for key in node_required_keys:
            if not key in node:
                return False, f"'{key}' field is required for node configuration"
            
            if not node[key]:
                return False, f"Required node field ({key}) must not be empty"
        group_type: GroupType = node['group_type']

        if not group_type in [GroupType.PARENT, GroupType.CHILD, GroupType.LOAD_ONLY]:
            return False, "Type of 'parent', 'child' or 'router' is required for node configurations"
        
        if group_type == GroupType.PARENT and not 'url' in node:
                return False, "A parent node must have a synchronization url"
        
        if group_type == GroupType.CHILD and not 'url' in node:
                return False, "A child node must have a replication url"

        return self.success()

    def get_node_types(self, nodes):
        ls = []
        for node in nodes:
            ls.append(node['group_id'])
        print(ls)

    
    def validate_table(self) -> tuple[ bool, str]:
        # Table validation
        table_required_keys = ['name', 'channel']
        for table in self.project['tables']:
            for key in table_required_keys:
                if not key in table:
                     return False, f"Table {table['name']} '{key}' attribute is required for all tables'"

            # For master to master a route has to be specified as well
            if self.project['architecture'] == Architecture.BIDIRECTIONAL and 'route' in table: # table exceptions
                return False, f"Table {table['name']} 'route' key is required for table configuration '{arch}'"
            
            #TODO Code smell ? Check required keys for initial load tables
        
        return self.success()