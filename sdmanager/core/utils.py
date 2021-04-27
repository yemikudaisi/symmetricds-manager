from collections import namedtuple
from typing import Any

def new_object(object_name, dictionary) -> Any:
    """Creates and object instance from dictionary using `namedtuple`.

    Args:
        object_name ([type]): The objects type name
        dictionary ([type]): dictionary to be converted to an object

    Returns:
        Any: [description]
    """
    return namedtuple(object_name, dictionary.keys())(*dictionary.values())