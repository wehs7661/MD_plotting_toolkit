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

sys.path.append("../")
import matplotlib.pyplot as plt  # noqa: E402
import natsort  # noqa: E402
import numpu as np  # noqa: E402

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
    parser.add_argument("-l", "--legend", nargs="+", help="Legends of the histograms.")
    parser.add_argument(
        "-x",
        "--xlabel",
        type=str,
        default="X-axis",
        help='The name and units of x-axis. Default: "X-axis".',
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
        "-o",
        "--outline",
        default=False,
        action="store_true",
        help="Whether to plot the histogram outline.",
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
            args.input.split(".")[:-1]
        )  # '.png' will be appended later

    if args.output is None:
        args.output = "results_" + args.pngname.split(".png")[0] + ".txt"

    L = utils.Logging(args.dir + args.output)

    # Step 2. Read and preprocess (e.g. deduplicatoin, unit conversion) the input data
    for i in range(len(args.xvg)):
        result_str = f"\nData analysis of the file: {args.input[i]}"
        L.logger(result_str)
        L.logger("=" * (len(result_str) - 1))  # len(result_str) includes \n
        L.logger(f"- Working directory: {os.getcwd()}")
        L.logger(f'- Command line: {" ".join(sys.argv)}')
        L.logger("Analyzing the file ... ")
        L.logger("Plotting and saving figure ...")
        x, y = data_processing.read_2d_data(args.input[i], args.column)

        if "Time" in args.xlabel or "time" in args.xlabel:  # time series
            x, y = data_processing.deduplicate_data(x, y)

        if args.conversion is not None or args.factor is not None:
            y = data_processing.scale_data(y, args.conversion, args.factor, args.temp)

        # Data slicing if needed
        x = data_processing.slice_data(x, args.truncate, args.truncate_b)
        y = data_processing.slice_data(y, args.truncate, args.truncate_b)

        # simple data analysis of y
        data_processing.analyze_data(x, y, args.xlabel, args.ylabel, args.output)

        # Calculate the N_ratio
        if args.Nr_bound is not None:  # N_ratio = x(max) / x(min)
            lower_b, upper_b = args.Nr_bound[0], args.Nr_bound[1]
            truncated_y = np.array(
                list(set(y[y < upper_b]).intersection(y[y > lower_b]))
            )
            results = np.histogram(truncated_y, bins=args.nbins)
            N_ratio = np.max(results[0]) / np.min(results[0])
        L.logger(f"N_ratio = {N_ratio:.3f}")

        # Plot the histogram
        if args.legend is None:
            if args.outline is True:
                plt.hist(y, bins=args.nbins, edgecolor="black", linewidth=1.2)
            elif args.outline is False:
                plt.hist(y, bins=args.nbins)
        else:
            if args.outline is True:
                plt.hist(
                    y,
                    bins=args.nbins,
                    edgecolor="black",
                    linewidth=1.2,
                    label=f"{args.legend[i]}",
                )
            elif args.outline is False:
                plt.hist(y, bins=args.nbins, label=f"{args.legend[i]}")

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
