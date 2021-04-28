from collections import namedtuple
from typing import Any

def new_object(object_name, dictionary) -> Any:
    """Creates and object instance from dictionary using `namedtuple`.

    Args:
        object_name (Any): The objects type name
        dictionary (dict): The dictionary to be converted to an object

    Returns:
        Any: The object instance
    """
    return namedtuple(object_name, dictionary.keys())(*dictionary.values())

def append_to_dict(the_dict, key, value):
    """Appends key value pair to dict

    Helper function for use in list experession

    Args:
        the_dict (dict): The dictionary to append to
        key (str): The key to the key-value entry
        value (str): The key to the key-value entry

    Returns:
        dict: The dictionary with appended entry
    """
    the_dict[key] = value
    return the_dict