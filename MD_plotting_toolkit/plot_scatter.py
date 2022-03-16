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
The `plot_xy` module plots variable y against x given a set of 2d data.
"""
import argparse
import glob
import os
import sys

sys.path.append("../")
import matplotlib.pyplot as plt  # noqa: E402
import natsort  # noqa: E402

import MD_plotting_toolkit.data_processing as data_processing  # noqa: E402
import MD_plotting_toolkit.plotting_utils as plotting_utils  # noqa: E402
import MD_plotting_toolkit.utils as utils  # noqa: E402


def initialize():

    parser = argparse.ArgumentParser(
        description="This code plots variable y against x given a set of 2d data."
    )
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        help="The filename(s) of the input(s). Wildcards can be used.",
    )
    parser.add_argument(
        "-l", "--legend", nargs="+", help="Legends of the curves. Default: No legends."
    )
    parser.add_argument(
        "-x",
        "--xlabel",
        type=str,
        default="X-axis",
        help='The name and units of x-axis. Default: "X-axis".',
    )
    parser.add_argument(
        "-y",
        "--ylabel",
        type=str,
        default="Y-axis",
        help='The name and units of y-axis. Default: "Y-axis".',
    )
    parser.add_argument(
        "-c",
        "--column",
        type=int,
        default=1,
        help="The column index (starting from 0) of the dependent variable. Default: 1.",
    )
    parser.add_argument(
        "-t", "--title", type=str, help="Title of the plot. Default: No title."
    )
    parser.add_argument(
        "-n",
        "--pngname",
        type=str,
        help="The filename of the figure, not including the extension. \
                            The default is the filename of the input with .png as the extension.",
    )
    parser.add_argument(
        "-cx",
        "--x_conversion",
        choices=[
            "degree to radian",
            "radian to degree",
            "kT to kcal/mol",
            "kcal/mol to kT",
            "kT to kJ/mol",
            "kJ/mol to kT",
            "kJ/mol to kcal/mol",
            "kcal/mol to kJ/mol",
            "ns to ps",
            "ps to ns",
        ],
        help="The unit conversion for the data in x-axis.",
    )
    parser.add_argument(
        "-cy",
        "--y_conversion",
        choices=[
            "degree to radian",
            "radian to degree",
            "kT to kcal/mol",
            "kcal/mol to kT",
            "kT to kJ/mol",
            "kJ/mol to kT",
            "kJ/mol to kcal/mol",
            "kcal/mol to kJ/mol",
        ],
        help="The unit conversion for the data in y-axis.",
    )
    parser.add_argument(
        "-fx",
        "--factor_x",
        type=float,
        help="The factor to be multiplied to the x values.",
    )
    parser.add_argument(
        "-fy",
        "--factor_y",
        type=float,
        help="The factor to be multiplied to the y values.",
    )
    parser.add_argument(
        "-T",
        "--temp",
        type=float,
        default=298.15,
        help="Temperature for unit convesion involving kT. Default: 298.15.",
    )
    parser.add_argument(
        "-tr",
        "--truncate",
        help="-tr 1 means truncate the first 1%% of the data from the beginning.\
            This typically applies for, but not is restricted to time series data.",
    )
    parser.add_argument(
        "-trb",
        "--truncate_b",
        help="-r 1 means only analyze the first 1%% of the data from the end. \
            This typically applies for, but not is restricted to time series data.",
    )
    parser.add_argument(
        "-lc",
        "--legend_col",
        type=int,
        default=1,
        help="The number of columns of the legends.",
    )
    parser.add_argument(
        "-d",
        "--dir",
        default="",
        help="The output directory. The default is where the command is executed.",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="The file name of output documenting the statistics of the input data.",
    )

    return parser