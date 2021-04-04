class Validator():

    def __init__(self, config):
        self.properties = config
    
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

        keys = self.validate_primary_keys()
        if not keys[0]:
            return keys
        group = self.validate_group()
        if not group[0]:
            return group
        node = self.validate_node()
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
        required_primary_keys = ['groups', 'nodes', 'replication-arch', 'channels', 'tables']
        for key in required_primary_keys:
            if not key in self.properties:
                return False, f"'{key}' must be configured."
        
        return self.success()

    def validate_group(self) -> tuple[ bool, str]:
        self.groups = []
        group_required_keys = ['id' , 'sync']
        for group in self.properties['groups']:
            for key in group_required_keys:
                if not key in group:
                    return False, f"'{key}' key is required for group configuration"
            
            self.groups.append(group['id'])

            if group['sync'] not in ['P', 'W', 'R']:
                return False, 'Synchronization mode of P, W or R is required for group configuration'
        
        return self.success()
    
    def validate_node(self) -> tuple[ bool, str]:
                
        if len(self.properties['nodes']) < 2:
           return False, 'minimum of 2 nodes required'

        node_required_keys = ['engine_name', 'external_id', 'type', 'db_driver', 'db_url', 'db_user', 'db_password']
        for node in self.properties['nodes']:
            for key in node_required_keys:
                if not key in node:
                    return False, f"'{key}' key is required for node configuration"
            
            if node['type'] not in ['parent', 'child', 'router'] in node:
                return False, "Type of 'parent', 'child' or 'router' is required for node configurations"
            
            if node['group_id'] not in self.groups:
                return False, f"Node {node['external_id']}'s assigned group '{node['group_id']}' is not in {self.groups}"
        return self.success()
    
    def validate_table(self) -> tuple[ bool, str]:
        # Table validation
        table_required_keys = ['name', 'channel', 'route']
        for table in self.properties['tables']:
            for key in table_required_keys:
                if not key in table:
                    return False, f"{table['name']}: '{key}' key is required for table configuration"
            
            #TODO Check required keys for initial load tables
        
        return self.success()