class Architecture:
    """Replication architecture types.
    
    note an enum, for easy serialization and deserialization
    """
    PARENT_2_CHILD = 0
    CHILD_2_PARENT = 1
    BIDIRECTIONAL = 2

class GroupType:
    """Group types
    
    note an enum, for easy serialization and deserialization
    """
    PARENT = 0
    CHILD = 1
    LOAD_ONLY = 2

from sdmanager.core.validator import Validator
from sdmanager.core.sds_manager import SdsManager
from sdmanager.core.sds_manager import GroupNodeMediator