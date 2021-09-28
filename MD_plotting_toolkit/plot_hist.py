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
import itertools
import os
import sys
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
sys.path.append("../")
import matplotlib.pyplot as plt  # noqa: E402
import natsort  # noqa: E402
import numpy as np  # noqa: E402
import scipy.stats as stats  # noqa: E402
import seaborn as sns  # noqa: E402

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
        "-l",
        "--legend",
        type=str,
        default=[None],
        nargs="+",
        help="Legends of the histograms.",
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
        help='The name and units of y-axis. Default: "Count", if -s is also not specified.',
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
        "-s",
        "--stats",
        default="count",
        choices=["count", "frequency", "density", "probability"],
        help="Aggregate statistic to compute in each bin.\
            (1) 'count' shows the number of observations.\
            (2) 'frequency' shows the number of observations divided by the bin width.\
            (3) 'density' normalizes counts so that the area of the histogram is 1.\
            (4) 'probability' normalizes counts so that the sum of the bar heights is 1.",
    )
    parser.add_argument(
        "-k",
        "--kde",
        default=False,
        action="store_true",
        help="Whether to sketch a KDE (Kernel Density Estimation) plot or not.",
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
        "-r",
        "--range",
        type=float,
        nargs="+",
        help="The bounds for the histogram(s) (min, max)",
    )
    parser.add_argument(
        "-ks",
        "--ks_test",
        default=False,
        action="store_true",
        help="Whether to perform a Kolmogorov-Smirnov (K-S) test between any two distributions or not.",
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

    if args.stats == "count":
        args.ylabel = "Count"
    elif args.stats == "frequency":
        args.ylabel = "Frequency (count / bin width)"
    elif args.stats == "density":
        args.ylabel = "Probability density"
    elif args.stats == "probability":
        args.ylabel = "Probability"

    L = utils.Logging(args.dir + args.output)

    # Step 2. Read and preprocess (e.g. deduplicatoin, unit conversion) the input data
    if len(args.input) > 1:
        alpha = 0.7  # more transparent if multiple hisotgrams are plotted
    else:
        alpha = 1
    x_all, y_all = [], []
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

        x_all.append(x)
        y_all.append(y)

        # Out of bound warning
        if args.range is not None:
            args.range = tuple(args.range)
            adjusted = False
            if len(args.input) == 1:
                while np.min(y) < args.range[0]:
                    adjusted = True
                    args.range[0] *= 0.95
                while np.max(y) > args.range[1]:
                    adjusted = True
                    args.range[1] *= 1.05
                if adjusted is True:
                    L.logger(
                        "Note: The bounds for the histogram are adjusted to include all the data."
                    )
                    L.logger(
                        f"The new bounds are ({args.range[0]:.3f}, {args.range[1]:.3f})"
                    )
            else:
                if np.min(y) < args.range[0] or np.max(y) > args.range[1]:
                    raise utils.ParameterError(
                        f"The data (min: {np.min(y)}, max: {np.max(y)}) is out of the specified bounds {args.range} for this histogram. \
                        Please consider not specifying the bounds or specifying wider bounds."
                    )

        # Calculate the N_ratio
        if args.Nr_bound is not None:  # N_ratio = x(max) / x(min)
            lower_b, upper_b = args.Nr_bound[0], args.Nr_bound[1]
            truncated_y = np.array(
                list(set(y[y < upper_b]).intersection(y[y > lower_b]))
            )
            results = np.histogram(
                truncated_y, bins=args.nbins, density=(args.stats == "density"), range=args.range
            )
            N_ratio = np.max(results[0]) / np.min(results[0])
        else:
            results = np.histogram(
                y, bins=args.nbins, density=(args.stats == "density"), range=args.range
            )
            N_ratio = np.max(results[0]) / np.min(results[0])
        L.logger(f"Assessment of the hsitogram flatness: N_ratio = {N_ratio:.3f}")

        # Plot the histogram
        ax = sns.histplot(
            y,
            bins=args.nbins,
            binrange=args.range,
            label=f"{args.legend[i]}",
            stat=args.stats,
            kde=args.kde,
            line_kws=dict(color='yellow'),
            alpha=alpha,
        )
 
        if len(args.input) > 1:
            plt.legend(ncol=args.legend_col)

        # Get the data of count/frequency/probability/density 
        hist_data, bin_edges = np.histogram(y, bins=args.nbins, density=(args.stats=="density"))
        #hist_data /= 5
        if args.stats == 'count':
            pass
        elif args.stats == 'density':
            pass
        elif args.stats == 'frequency':
            bin_width = bin_edges[1] - bin_edges[0]
            hist_data /= bin_width
        elif args.stats == 'probability':
            hist_data /= np.sum(hist_data)
        
        if max(abs(y)) >= 10000 or max(abs(y)) <= 0.001:
            # variable y! (which is the x-axis in the plot)
            plt.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
        if max(abs(hist_data)) >= 10000 or max(abs(hist_data)) <= 0.001:
            plt.ticklabel_format(style="sci", axis="y", scilimits=(0, 0))

        # Some simple statistics
        x_var, x_unit = plotting_utils.identify_var_units(args.xlabel)
        max_n = np.max(hist_data)
        max_n_idx = list(hist_data).index(max_n)
        b1 = bin_edges[max_n_idx]  # left bound
        b2 = bin_edges[max_n_idx + 1]  # right bound
        L.logger(f"The maximum of {x_var} is {np.max(y):.6f}{x_unit}.")
        L.logger(f"The minimum of {x_var} is {np.min(y):.6f}{x_unit}.")
        L.logger(f"The total number of counts is {len(y)}.")
        L.logger(
            f"{x_var[0].upper() + x_var[1:]} between {b1:.6f} and {b2:.6f}{x_unit} has the highest {args.stats}, which is {max_n}."
        )

    if args.title is not None:
        plt.title(f"{args.title}", weight="bold")
    plt.xlabel(f"{args.xlabel}")
    plt.ylabel(f"{args.ylabel}")
    plt.grid(True)

    plt.savefig(f"{args.dir}{args.pngname}.png")
    plt.show()

    if args.ks_test is True:
        n_distribution = len(args.input)
        if n_distribution == 1:
            raise utils.ParameterError(
                "At least two input files are required to perform a K-S test."
            )
        else:
            pairs = list(itertools.combinations(range(n_distribution), 2))
            for i in pairs:
                L.logger("\n=== Kolmogorov-Smirnov test ===")
                L.logger(f"- Files of interest: {args.input[i[0]]}, {args.input[i[1]]}")
                L.logger(
                    f"- Null hypothesis: The distributions obtained from the two files are consistent with each other."
                )
                d_statistics, p_value = stats.kstest(y_all[i[0]], y_all[i[1]])
                L.logger(f"- D-statistics {d_statistics}")
                L.logger(f"- p-value: {p_value}")
                if p_value > 0.05:  # statistically significant
                    L.logger(
                        "- Interpretation: The two distributions are consistent with each other."
                    )
                else:
                    L.logger(
                        f"- Interpretation: The two distributions are not consistent with each other."
                    )
