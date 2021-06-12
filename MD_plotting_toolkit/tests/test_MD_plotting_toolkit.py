"""
Unit and regression test for the MD_plotting_toolkit package.
"""

import sys

import pytest

# Import package, test suite, and other packages as needed
import MD_plotting_toolkit


def test_MD_plotting_toolkit_imported():
    """Sample test, will always pass so long as import statement worked"""
    assert "MD_plotting_toolkit" in sys.modules
