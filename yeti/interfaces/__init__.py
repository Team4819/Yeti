"""
Interfaces are the primary method for inter-module communication. They store data in
the current :class:`yeti.Context`, using it's :meth:`yeti.Context.get_interface_data()` method. Yeti comes
with two default Interfaces, which should be sufficient for most uses. However, more may easily
be created to expand Yeti's functionality.
"""

from .events import *
from .datastreams import *