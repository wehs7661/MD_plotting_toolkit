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
The `plot_hist` module plots a histogram given the data of a variable.
"""
import argparse
import glob
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
sys.path.append("../")
import matplotlib.pyplot as plt  # noqa: E402
import natsort  # noqa: E402
import numpy as np  # noqa: E402

import MD_plotting_toolkit.data_processing as data_processing  # noqa: E402
import MD_plotting_toolkit.plotting_utils as plotting_utils  # noqa: E402
import MD_plotting_toolkit.utils as utils  # noqa: E402


def initialize():

    parser = argparse.ArgumentParser(
        description="This code plots a hisotgram given the data of a variable."
    )
    parser.add_argument(
        "-i",
        "--input",
        nargs="+",
        help="The filename(s) of the input(s). Wildcards can be used.",
    )
    parser.add_argument(
        "-l", "--legend", type=str, nargs="+", help="Legends of the histograms."
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
        default="Count",
        help='The name and units of y-axis. Default: "Count".',
    )
    parser.add_argument(
        "-c",
        "--column",
        type=int,
        default=1,
        help="The column index of the variable to be analyzed.",
    )
    parser.add_argument("-t", "--title", type=str, help="Title of the plot")
    parser.add_argument(
        "-n",
        "--pngname",
        type=str,
        help="The filename of the figure, not including the extension",
    )
    parser.add_argument(
        "-nb",
        "--nbins",
        type=int,
        default=200,
        help="The number of bins for the histogram.",
    )
    parser.add_argument(
        "-nr",
        "--normalized",
        default=False,
        action="store_true",
        help="Whether to normalize the counts.",
    )
    parser.add_argument(
        "-cc",
        "--conversion",
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
        "-ff",
        "--factor",
        type=float,
        help="The factor to be multiplied to the x values of the histogram.",
    )
    parser.add_argument(
        "-T",
        "--temp",
        type=float,
        default=298.15,
        help="Temperature for unit convesion involving kT. Default: 298.15.",
    )
    parser.add_argument(
        "-ol",
        "--outlines",
        default=False,
        action="store_true",
        help="Whether to plot the histogram outlines.",
    )
    parser.add_argument(
        "-tr",
        "--truncate",
        help="-tr 1 means truncate the first 1%% of the data from the beginning. \
                            This typically applies for, but not is restricted to time series data.",
    )
    parser.add_argument(
        "-trb",
        "--truncate_b",
        help="-r 1 means only analyze the first 1%% of the data from the end. \
            This typically applies for, but not is restricted to time series data.",
    )
    parser.add_argument(
        "-Nb",
        "--Nr_bound",
        type=float,
        nargs="+",
        help="The lower and upper bounds of the x axis for N_ratio calculations.",
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
    args_parse = parser.parse_args()

    return args_parse


def main():
    args = initialize()

    # Step 1. Setting things up
    plotting_utils.default_settings()

    if isinstance(args.input, str):
        if "*" in args.xvg:  # allow wildcards
            args.input = natsort.natsorted(glob.glob(args.input), reverse=False)
        else:  # only one input file
            args.input = list(args.xvg)

    if args.pngname is None:
        args.pngname = ".".join(
            args.input[0].split(".")[:-1]
        )  # '.png' will be appended later

    if args.output is None:
        args.output = "results_" + args.pngname.split(".png")[0] + ".txt"

    if args.normalized is True:
        args.ylabel = "Probability density"
    else:
        args.ylabel = "Count"

    L = utils.Logging(args.dir + args.output)

    # Step 2. Read and preprocess (e.g. deduplicatoin, unit conversion) the input data
    if len(args.input) > 1:
        alpha = 0.7  # more transparent if multiple hisotgrams are plotted
    else:
        alpha = 1

    for i in range(len(args.input)):
        result_str = f"\nData analysis of the file: {args.input[i]}"
        L.logger(result_str)
        L.logger("=" * (len(result_str) - 1))  # len(result_str) includes \n
        L.logger(f"- Working directory: {os.getcwd()}")
        L.logger(f'- Command line: {" ".join(sys.argv)}')
        x, y = data_processing.read_2d_data(args.input[i], args.column)

        if "Time" in args.xlabel or "time" in args.xlabel:  # time series
            x, y = data_processing.deduplicate_data(x, y)

        if args.conversion is not None or args.factor is not None:
            y = data_processing.scale_data(y, args.conversion, args.factor, args.temp)

        # Data slicing if needed
        x = data_processing.slice_data(x, args.truncate, args.truncate_b)
        y = data_processing.slice_data(y, args.truncate, args.truncate_b)

        # Calculate the N_ratio
        if args.Nr_bound is not None:  # N_ratio = x(max) / x(min)
            lower_b, upper_b = args.Nr_bound[0], args.Nr_bound[1]
            truncated_y = np.array(
                list(set(y[y < upper_b]).intersection(y[y > lower_b]))
            )
            results = np.histogram(
                truncated_y, bins=args.nbins, density=args.normalized
            )
            N_ratio = np.max(results[0]) / np.min(results[0])
        else:
            results = np.histogram(y, bins=args.nbins, density=args.normalized)
            N_ratio = np.max(results[0]) / np.min(results[0])
        L.logger(f"Assessment of the hsitogram flatness: N_ratio = {N_ratio:.3f}")

        # Plot the histogram
        if args.legend is None:
            if args.outlines is True:
                results = plt.hist(
                    y,
                    bins=args.nbins,
                    edgecolor="black",
                    linewidth=1.2,
                    density=args.normalized,
                    alpha=alpha,
                )
            elif args.outlines is False:
                plt.hist(y, bins=args.nbins, density=args.normalized, alpha=alpha)
        else:
            if args.outlines is True:
                results = plt.hist(
                    y,
                    bins=args.nbins,
                    edgecolor="black",
                    linewidth=1.2,
                    label=f"{args.legend[i]}",
                    density=args.normalized,
                    alpha=alpha,
                )
            elif args.outlines is False:
                results = plt.hist(
                    y,
                    bins=args.nbins,
                    label=f"{args.legend[i]}",
                    density=args.normalized,
                    alpha=alpha,
                )

            if len(args.input) > 1:
                plt.legend(ncol=args.legend_col)

    # Some simple statistics
    x_var, x_unit = plotting_utils.identify_var_units(args.xlabel)
    y_var, y_unit = plotting_utils.identify_var_units(args.ylabel)
    max_n = np.max(results[0])
    max_n_idx = list(results[0]).index(max_n)
    b1 = results[1][max_n_idx]  # left bound
    b2 = results[1][max_n_idx + 1]  # right bound
    L.logger(f"The maximum of {x_var} is {np.max(y):.6f}{x_unit}.")
    L.logger(f"The minimum of {x_var} is {np.min(y):.6f}{x_unit}.")
    L.logger(f"The total number of counts is {len(x)}.")
    L.logger(
        f"{x_var[0].upper() + x_var[1:]} between {b1:.6f} and {b2:.6f}{x_unit} has the highest probability density."
    )

    if args.title is not None:
        plt.title(f"{args.title}", weight="bold")
    plt.xlabel(f"{args.xlabel}")
    plt.ylabel(f"{args.ylabel}")
    if max(abs(x)) >= 10000:
        plt.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    if max(abs(y)) >= 10000:
        plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))
    plt.grid(True)

    plt.savefig(f"{args.dir}{args.pngname}.png")
    plt.show()
