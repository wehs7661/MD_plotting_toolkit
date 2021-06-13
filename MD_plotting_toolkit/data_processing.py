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
The `data_processing` module provides functions for processing data.
"""
import sys

import numpy as np

sys.path.append("../")
import MD_plotting_toolkit.plotting_utils as plotting_utils  # noqa: E402
import MD_plotting_toolkit.utils as utils  # noqa: E402


def deduplicate_data():
    pass


def read_2d_data(f_input, col_idx=1):
    """
    This function reads in any input file that is readable by np.loadtxt or the
    ones that follow the GROMACS xvg format. It returns a 2 x n array, where
    n is the number of data points of each variable. By default, the independent
    variable and the dependent variable are the data of the first and second column.
    The user can decide which column to read as the dependent variable.

    Parameters
    ----------
    f_input : str
        The filename of the input file.
    col_idx : int
        The index (starting from 0) of the column to be read as the dependent variable.

    Returns
    -------
    x_data : np.array
        The data of independent variable read from the input file.
    y_data : np.array
        The data of dependent variable read from the input file.
    """
    try:
        data = np.transpose(np.loadtxt(f_input))
        x_data, y_data = data[0], data[col_idx]
    except ValueError:
        x_data, y_data = [], []
        infile = open(f_input, "r")
        lines = infile.readlines()
        infile.close()

        for line in lines:
            if "#" not in line and "@" not in line:
                x_data.append(float(line.split()[0]))
                y_data.append(float(line.split()[col_idx]))

        x_data, y_data = np.array(x_data), np.array(y_data)

    return x_data, y_data


def scale_data(data, conversion=None, factor=None, T=298.15):
    """
    This function scales the input data according to the desired unit conversion
    or scaling factor specified by the user.

    Parameters
    ----------
    data : np.array
        The input data to be scaled.
    conversion : str
        The string describing what units the conversion should be carried out between.
        Available conversions include "ps to ns", "kT to kJ/mol", "kT to kcal/mol",
        "kJ/mol to kcal/mol", "degree to radian", and their respective conversion in
        the opposite direction. Note that the list of available conversions does not
        mean to be comprehensive since the user could just specify the scaling factor.
    factor : float
        The scaling factor for data scaling.
    T : float
        The temperature to be considered to convert energy units to kT or vice versa.

    Returns
    -------
    data : np.array
        The processed data
    """
    c1 = 1.38064852 * 6.022 * T / 1000  # multiply to convert from kT to kJ/mol
    c2 = np.pi / 180  # multiply to convert from degree to radian
    c3 = 0.239005736  # multiply to convert from J to cal (or kJ/mol to kcal/mol)

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

    if conversion is not None:
        if conversion in conversion_dict:
            data *= conversion_dict[conversion]
        else:
            raise utils.ParameterError(
                "The specified conversion is not available. \
                                 Try using the scaling factor. "
            )

    if factor is None:
        factor = 1

    data *= factor

    return data


def slice_data(data, truncate=None, truncate_b=None):
    """
    This function slices the data given the truncation fraction or the fraction of data
    to be retained. The values should be with 0 to 100 (units: percent).

    Parameters
    ----------
    data : np.array
        The input data to be sliced.
    truncate : float
        The percentage of data to be truncated from the beginning. 20 means 20%.
    truncate_b : float
        The percentage of data to be truncated from the end. 20 means 20%.

    Returns
    -------
    data : data
        The processed data.
    """

    if truncate is not None and truncate_b is None:
        data = data[int(0.01 * float(truncate) * len(data)) :]  # noqa E203

    if truncate_b is not None and truncate is None:
        data = data[: int(0.01 * float(truncate_b) * len(data))]

    if truncate is not None and truncate_b is not None:
        data = data[
            int(0.01 * float(truncate_b) * len(data)) : -int(  # noqa E203
                0.01 * float(truncate) * len(data)
            )
        ]

    return data


def analyze_data(x, y, x_label, y_label, outfile):
    """
    This function performs simple data analysis and prints out the results.

    Parameters
    ----------
    x : np.array
        The data of variable x.
    y : np.array
        The data of variable y.
    x_label : str
        The label of the x-axis.
    y_label : str
        The lable of the y-axis.
    """
    L = utils.Logging(outfile)
    x_var, x_unit = plotting_utils.identify_var_units(x_label)
    y_var, y_unit = plotting_utils.identify_var_units(y_label)

    if x_unit == " ns" or x_unit == " ps":
        y_avg = np.mean(y)
        y2_avg = np.mean(np.power(y, 2))
        RMSF = np.sqrt((y2_avg - y_avg ** 2)) / y_avg

        y = list(y)
        L.logger(
            f"The average of {y_var}: {y_avg:.3f} (RMSF: {RMSF:.3f}, max: {max(y):.3f}, min: {min(y):.3f})"
        )
        L.logger(f"The maximum of {y_var} occurs at {x[y.index(max(y))]:.3f}{x_unit}.")
        L.logger(f"The minimum of {y_var} occurs at {x[y.index(min(y))]:.3f}{x_unit}.")
        y = np.array(y)
        diff = np.abs(y - y_avg)
        t_avg = x[np.argmin(diff)]
        L.logger(
            f"The {y_var} ({y[np.argmin(diff)]:.3f}{y_unit}) at {t_avg:.3f}{x_unit} is closet to the average."
        )
    else:  # input data is not a time series
        y = list(y)
        L.logger(
            f"Maximum of {y_var}: {max(y):.3f}{y_unit}, which occurs at {x[y.index(max(y))]:.3f}{x_unit}."
        )
        L.logger(
            f"Minimum of {y_var}: {min(y):.3f}{y_unit}, which occurs at {x[y.index(min(y))]:.3f}{x_unit}."
        )
