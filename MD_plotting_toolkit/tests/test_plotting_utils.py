####################################################################
#                                                                  #
#    MD_plotting_toolkit,                                          #
#    a python package to visualize the results obtained from MD    #
#                                                                  #
#    Written by Wei-Tse Hsu <wehs7661@colorado.edu>                #
#    Copyright (c) 2021 University of Colorado Boulder             #
#                                                                  #
####################################################################
"""
Unit tests for the module `MD_plotting_toolkit.plotting_utils`.
"""
import matplotlib.pyplot as plt

import MD_plotting_toolkit.plotting_utils as plotting_utils


def test_default_settings():
    plotting_utils.default_settings()

    assert plt.rcParams["font.family"] == ["serif"]
    assert plt.rcParams["font.sans-serif"] == ["DejaVu Sans"]
    assert plt.rcParams["font.size"] == 10.0
    assert plt.rcParams["mathtext.default"] == "regular"


def test_identify_var_units():
    v1, u1 = plotting_utils.identify_var_units(None)
    v2, u2 = plotting_utils.identify_var_units("X-axis")
    v3, u3 = plotting_utils.identify_var_units("Y-axis")
    v4, u4 = plotting_utils.identify_var_units("Free energy ($ k_{B}T $)")
    v5, u5 = plotting_utils.identify_var_units("Dihedral (deg)")
    v6, u6 = plotting_utils.identify_var_units("Dihedral")

    assert v1 is None
    assert u1 == ""
    assert v2 == "x"
    assert u2 == ""
    assert v3 == "y"
    assert u3 == ""
    assert v4 == "free energy"
    assert u4 == " k_{B}T"
    assert v5 == "dihedral"
    assert u5 == " deg"
    assert v6 == "dihedral"
    assert u6 == ""
