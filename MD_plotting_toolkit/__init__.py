"""
MD_plotting_toolkit
This is a repository providing useufl codes for visualizing MD simulation data.
"""

# Add imports here
from .md_plotting_toolkit import *

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
