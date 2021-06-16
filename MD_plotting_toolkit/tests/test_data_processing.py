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
Unit tests for the module `MD_plotting_toolkit.data_processing`.
"""
import os

import numpy as np

import MD_plotting_toolkit.data_processing as data_processing

current_path = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(current_path, "sample_inputs")
output_path = os.path.join(current_path, "sample_outputs")

fes_file = input_path + "/fes.dat"
potential_file = input_path + "/potential.xvg"
hills_corrupted = input_path + "/corrupted_HILLS"
dhdl_corrupted = input_path + "/corrupted_dhdl.xvg"


def test_read_2d_data():
    # Case 1: readable by np.loadtxt
    x1, y1 = data_processing.read_2d_data(fes_file)

    # Case 2: not readable by np.loadtxt
    x2, y2 = data_processing.read_2d_data(potential_file)

    # Case 3: Non-default col_idx
    x3, y3 = data_processing.read_2d_data(fes_file, col_idx=4)

    # Here we only compare the first 5 elements to save up some space
    x1, y1 = x1[:5], y1[:5]
    x2, y2 = x2[:5], y2[:5]
    x3, y3 = x3[:5], y3[:5]

    # Expected results
    xx1 = np.array([-3.14159265, -3.0787608, -3.01592895, -2.95309709, -2.89026524])
    yy1 = np.array([-0.00035355, -0.00035355, -0.00035355, -0.00035355, -0.00035355])
    xx2 = np.array([0, 2, 4, 6, 8])
    yy2 = np.array(
        [-20045.462891, -19989.603516, -19909.130859, -20057.402344, -19812.580078]
    )
    xx3 = np.array([-3.14159265, -3.0787608, -3.01592895, -2.95309709, -2.89026524])
    yy3 = np.array(
        [-8778.4411543, -8765.49326731, -8748.15371253, -8727.40373623, -8703.7556338]
    )

    np.testing.assert_array_almost_equal(x1, xx1)
    np.testing.assert_array_almost_equal(y1, yy1)
    np.testing.assert_array_almost_equal(x2, xx2)
    np.testing.assert_array_almost_equal(y2, yy2)
    np.testing.assert_array_almost_equal(x3, xx3)
    np.testing.assert_array_almost_equal(y3, yy3)


def test_deduplicate_data():
    x1 = [2, 4, 6, 2, 7, 8, 4, 3]  # not the x-data for a typical time seris
    y1 = [1, 2, 3, 4, 5, 6, 7, 8]

    # Below we test from reading the file to cleaning the data

    x2, y2 = data_processing.read_2d_data(hills_corrupted)  # PLUMED output
    x3, y3 = data_processing.read_2d_data(dhdl_corrupted)  # GROMACS output

    x1, y1 = data_processing.deduplicate_data(x1, y1)
    x2, y2 = data_processing.deduplicate_data(x2, y2)
    x3, y3 = data_processing.deduplicate_data(x3, y3)

    assert x1 == [6, 2, 7, 8, 4, 3]
    assert y1 == [3, 4, 5, 6, 7, 8]
    assert len(x2) == 3000
    assert len(y2) == 3000
    assert len(x3) == 1501
    assert len(y3) == 1501
    assert int(np.sum(np.diff(x2))) == (len(x2) - 1) * 1
    assert int(np.sum(np.diff(x3))) == (len(x3) - 1) * 2


def test_scale_data():
    f = 2
    T = 300
    c1 = 1.38064852 * 6.022 * T / 1000
    c2 = np.pi / 180
    c3 = 0.239005736
    data = np.random.rand(100)

    conversion_dict = {
        "ns to ps": 1000,
        "ps to ns": 1 / 1000,
        "kT to kJ/mol": c1,
        "kJ/mol to kT": 1 / c1,
        "kT to kcal/mol": c1 * c3,
        "kcal/mol to kT": 1 / (c1 * c3),
        "kJ/mol to kcal/mol": c3,
        "kcal/mol to kJ/mol": 1 / c3,
        "degree to radian": c2,
        "radian to degree": 1 / c2,
    }

    np.testing.assert_array_almost_equal(data_processing.scale_data(data), data)
    for i in conversion_dict:
        expected = data * conversion_dict[i] * f
        np.testing.assert_array_almost_equal(
            data_processing.scale_data(data, i, f, T), expected
        )


def test_slice_data():
    data = np.arange(100)
    data_unchaged = data_processing.slice_data(data)
    data_1 = data_processing.slice_data(data, truncate=20)
    data_2 = data_processing.slice_data(data, truncate_b=20)
    data_3 = data_processing.slice_data(data, truncate=20, truncate_b=20)

    np.testing.assert_equal(data, data_unchaged)
    assert data_1[0] == 20
    assert data_2[-1] == 19
    assert data_3[0] == 20
    assert data_3[-1] == 79


def test_analyze_data():
    x = np.arange(100)
    y = np.arange(100, 200)
    outfile = output_path + "/test_output.txt"

    # Test 1: When input data is not a time series
    x_label = "Dihedral (deg)"
    y_label = "Free energy (kT)"
    data_processing.analyze_data(x, y, x_label, y_label, outfile)

    line_1 = "Maximum of free energy: 199.000 kT, which occurs at 99.000 deg.\n"
    line_2 = "Minimum of free energy: 100.000 kT, which occurs at 0.000 deg.\n"
    texts = [line_1, line_2]

    infile = open(outfile, "r")
    lines = infile.readlines()
    infile.close()

    assert os.path.isfile(outfile) is True
    assert texts == lines
    os.remove(outfile)

    # Test 2: When input data is a time series
    x_label = "Time (ns)"
    y_label = "Distance (nm)"
    data_processing.analyze_data(x, y, x_label, y_label, outfile)
    line_1 = (
        "The average of distance: 149.500 (RMSF: 0.193, max: 199.000, min: 100.000)\n"
    )
    line_2 = "The maximum of distance occurs at 99.000 ns.\n"
    line_3 = "The minimum of distance occurs at 0.000 ns.\n"
    line_4 = "The distance (149.000 nm) at 49.000 ns is closet to the average.\n"
    texts = [line_1, line_2, line_3, line_4]

    infile = open(outfile, "r")
    lines = infile.readlines()
    infile.close()

    assert os.path.isfile(outfile) is True
    assert texts == lines
    os.remove(outfile)
