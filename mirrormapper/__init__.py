"""
    Given a git repo URL, see if we can map it to a mirror name
"""

__version__ = "0.2.1"

from mirrormapper.mapurl import get_mirror_name
from mirrormapper.mapurl import MirrorMapperException
from mirrormapper.mapurl import known_mappings

__all__ = ['get_mirror_name', 'MirrorMapperException', 'known_mappings']
