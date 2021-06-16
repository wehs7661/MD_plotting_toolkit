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
The `combine_plots` module combines given plots with specified dimensions.
"""
import argparse
import sys

sys.path.append("../")
import cv2  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

import MD_plotting_toolkit.plotting_utils as plotting_utils  # noqa: E402


def initialize():
    parser = argparse.ArgumentParser(
        description="This code plots the angle and dihedral angle distribution for the modified System 2."
    )
    parser.add_argument(
        "-f", "--figs", nargs="+", help="The number of figures to be combined."
    )
    parser.add_argument(
        "-d",
        "--dimension",
        type=int,
        nargs="+",
        help="The dimension of the subplots (n_cols, n_rows).",
    )
    parser.add_argument(
        "-s",
        "--size",
        type=int,
        nargs="+",
        help="The dimensions of the figure (length, width).",
    )
    parser.add_argument("-t", "--titles", nargs="+", help="The title of each subplot.")
    parser.add_argument(
        "-b",
        "--border",
        default=False,
        action="store_true",
        help="Whether to show the border lines of each subplot.",
    )
    parser.add_argument(
        "-n", "--pngname", help="The name of the figure, not cluding the extension."
    )

    args_parse = parser.parse_args()

    return args_parse


def main():
    args = initialize()

    # Step 1. Setting things up
    plotting_utils.default_settings()

    if args.size is None:
        fig = plt.figure()
    else:
        if len(args.size) != 2:
            print("Warning: wrong number of arguments for specifying the figure size.")
        else:
            fig = plt.figure(figsize=tuple(args.size))

    if args.dimension is None:
        n_cols, n_rows = plotting_utils.get_fig_dimension(len(args.figs))
    else:
        if len(args.dimension) != 2:
            print(
                "Warning: wrong number of arguments for specifying the dimension of the subplots."
            )
        else:
            n_cols = args.dimension[0]
            n_rows = args.dimension[1]

    if args.titles is not None:
        if len(args.figs) != len(args.titles):
            print("Error: The number of titles does not match the number of subplots.")
            sys.exit()

    # Step 2. Combine plots@
    for i in range(len(args.figs)):
        image = cv2.imread(args.figs[i], cv2.IMREAD_COLOR)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        fig.add_subplot(n_rows, n_cols, i + 1)
        plt.imshow(image_rgb)
        if args.border is True:
            plt.xticks([])
            plt.yticks([])
        elif args.border is False:
            plt.axis("off")
        if args.titles is not None:
            plt.title(args.titles[i])

    plt.tight_layout(rect=[0, 0, 1, 1])
    plt.savefig(f"{args.pngname}.png", dpi=600)
