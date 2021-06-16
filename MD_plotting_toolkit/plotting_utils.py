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
The `plotting_utils` module provides various utilities for plotting.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc


def default_settings():
    """
    This function adopts the plotting settings shown below.
    """
    rc("font", **{"family": "sans-serif", "sans-serif": ["DejaVu Sans"], "size": 10})
    # Set the font used for MathJax - more on this later
    rc("mathtext", **{"default": "regular"})
    plt.rc("font", family="serif")


def identify_var_units(label):
    """
    This function parses the x-label or y-label to figure out the
    variable name and unit if possible.

    Parameters
    ----------
    label : str
        The label of x- or y-axis.

    Returns
    -------
    var : str
        The name of the variable.
    unit :str
        The units of the variable.
    """
    if label is not None:
        if "(" in label:
            if "$" in label.split("(")[1]:
                unit = " ".join(label.split("$")[1].split("$")[0].split(" ")[:-1])
            else:
                unit = " " + label.split("(")[1].split(")")[0]
            var = " ".join(label.split("(")[:-1]).lower()
            if var[-1] == " ":
                var = " ".join(var.split(" ")[:-1]).lower()
        else:
            unit = ""
            var = label.lower()
    else:
        unit = ""
        var = None

    if label == "X-axis":
        var = "x"
    if label == "Y-axis":
        var = "y"

    return var, unit


def get_fig_dimension(n_subplots):
    """
    Gets the number of plots in each row/column given the total number of subplots. The dimensions
    will be as close as to a square as possible.

    Parameters
    ----------
    n_subplots (int): The number of subplots.

    Returns
    -------
    n_rows (int): The number of rows in the figure.
    n_cols (int): The number of columns in the figure.
    """
    if int(np.sqrt(n_subplots) + 0.5) ** 2 == n_subplots:
        # perfect square number
        n_cols = int(np.sqrt(n_subplots))
    else:
        n_cols = int(np.floor(np.sqrt(n_subplots))) + 1

    if n_subplots % n_cols == 0:
        n_rows = int(n_subplots / n_cols)
    else:
        n_rows = int(np.floor(n_subplots / n_cols)) + 1

    return n_cols, n_rows
