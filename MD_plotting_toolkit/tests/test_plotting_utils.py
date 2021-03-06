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
import numpy as np
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


def test_get_fig_dimension():
    c1, r1 = plotting_utils.get_fig_dimension(49)
    c2, r2 = plotting_utils.get_fig_dimension(50)
    c3, r3 = plotting_utils.get_fig_dimension(56)

    assert c1 == 7
    assert r1 == 7
    assert c2 == 8
    assert r2 == 7
    assert c3 == 8
    assert r3 == 7


def test_get_bars_locations():
    # Test 1: Large spacing (spacing = 1)
    locs_1 = plotting_utils.get_bars_locations(3, 5, 0.2)
    expected_1 = np.array([0.1, 0.3, 0.5])
    np.testing.assert_array_almost_equal(locs_1[0], expected_1)
    shift = 3 * 0.2 + 3 * 0.2 * 2 / 3  # n_bars * width + spacing
    for i in range(1, 5):
        np.testing.assert_array_almost_equal(expected_1 + shift * i, locs_1[i])

    # Test 2: Small spacing (spacing = 0.1)
    locs_2 = plotting_utils.get_bars_locations(5, 8, 0.1)
    expected_2 = np.array([0.05, 0.15, 0.25, 0.35, 0.45])
    np.testing.assert_array_almost_equal(locs_2[0], expected_2)
    shift = 5 * 0.1 + 5 * 0.1 * 1 / 5  # n_bars * width + spacing
    for i in range(1, 8):
        np.testing.assert_array_almost_equal(expected_2 + shift * i, locs_2[i])
