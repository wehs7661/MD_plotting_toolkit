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
        help="Temperature for unit convesion involving kT. Default: 298.15.",
    )
    parser.add_argument(
        "-tr",
        "--truncate",
        help="-tr 1 means truncate the first 1%% of the data from the beginning.",
    )
    parser.add_argument(
        "-trb",
        "--truncate_b",
        help="-r 1 means only analyze the first 1%% of the data from the end.",
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


if __name__ == "__main__":
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

    if args.temp is None:
        args.temp = 298.15

    if args.output is None:
        args.output = "results_" + args.pngname.split(".png")[0] + ".txt"

    L = utils.Logging(args.dir + args.output)

    # Steo 2. Read and preprocess (e.g. deduplication, unit conversion) the input data
    for i in range(len(args.input)):
        result_str = "\nData analysis of the file: %s" % args.input[i]
        L.logger(result_str)
        L.logger("=" * (len(result_str) - 1))  # len(result_str) includes \n
        L.logger(f"- Working directory: {os.getcwd()}")
        L.logger(f'- Command line: {" ".join(sys.argv)}')
        L.logger("Analyzing the file ... ")
        L.logger("Plotting and saving figure ...")
        x, y = data_processing.read_2d_data(args.input[i], args.column)

        if args.x_conversion is not None or args.factor_x is not None:
            x = data_processing.scale_data(
                x, args.x_conversion, args.factor_x, args.temp
            )

        if args.y_conversion is not None or args.factor_y is not None:
            y = data_processing.scale_data(
                y, args.y_conversion, args.factor_y, args.temp
            )

        # Data slicing as needed
        x = data_processing.slice_data(x, args.truncate, args.truncate_b)
        y = data_processing.slice_data(y, args.truncate, args.truncate_b)

        # simple data analysis of y
        data_processing.analyze_data(x, y, args.xlabel, args.ylabel, args.output)

        # Plot the figure
        if args.legend is None:
            plt.plot(x, y)
        else:
            plt.plot(x, y, label=f"{args.legend[i]}")
            if len(args.input) > 1:
                plt.legend(ncol=args.legend_col)

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
