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
import warnings
import natsort
import glob

warnings.filterwarnings("ignore")
sys.path.append("../")

import cv2  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from mpl_toolkits.axes_grid.inset_locator import inset_axes  # noqa: E402

import MD_plotting_toolkit.plotting_utils as plotting_utils  # noqa: E402
import MD_plotting_toolkit.utils as utils  # noqa: E402


def initialize():
    parser = argparse.ArgumentParser(
        description="This code combines the given plots in a specified way."
    )
    parser.add_argument(
        "-f",
        "--figs",
        nargs="+",
        help="The filenames of the figures to be combined. Wildcards can be used.",
    )
    parser.add_argument(
        "-d",
        "--dimension",
        type=int,
        nargs="+",
        help="The dimension of the subplots (n_cols, n_rows) in the new figure.",
    )
    parser.add_argument(
        "-s",
        "--size",
        type=float,
        nargs="+",
        help="The size of the new figure (length, width). By default, the size will \
            be automatically estimated to enable a tight layout of the new figure.",
    )
    parser.add_argument("-t", "--titles", nargs="+", help="The title of each subplot.")
    parser.add_argument(
        "-b",
        "--border",
        default=False,
        action="store_true",
        help="Whether to show the border lines of each subplot. If one of the figures\
            is embedded, setting this to True only plots the border lines of the parent figure.",
    )
    parser.add_argument(
        "-a",
        "--annotate",
        default=False,
        action="store_true",
        help="Whether to annotate the figures with panel labels.",
    )
    parser.add_argument(
        "-fo",
        "--font",
        choices=['Arial', 'serif'],
        default='Arial',
        help="The font for annotation.",
    )
    parser.add_argument(
        "-n", "--pngname", help="The name of the figure, not cluding the extension."
    )
    parser.add_argument(
        "-e",
        "--embedded",
        default=False,
        action="store_true",
        help="Whether to embed the second figure in the first one.",
    )
    parser.add_argument(
        "-se",
        "--size_e",
        type=float,
        default=0.3,
        help="The size of the embedded figure in the units relative to \
            the the parent axes.",
    )
    parser.add_argument(
        "-pe",
        "--pos_e",
        type=float,
        nargs="+",
        default=[0.15, 0.59],
        help="The position of the lower left corner of the embedded figure \
            relative to the parent axes.",
    )
    parser.add_argument(
        "-be",
        "--border_e",
        default=False,
        action="store_true",
        help="Whether to show the border lines of the embedded figure.",
    )
    parser.add_argument(
        "-bgr",
        "--bgr",
        default=False,
        action="store_true",
        help="Whether to show the embedded figure in BGR instead of RGB. This could \
            make the embedded stand out if both input figures are of the same color.",
    )

    args_parse = parser.parse_args()

    return args_parse


def main():
    args = initialize()

    plotting_utils.default_settings(args.font)

    # Method 1: Making the input files as the subplots of the new figure
    # Step 1. Setting things up
    if '*' in args.figs[0]:
        args.figs = natsort.natsorted(glob.glob(args.figs[0]))

    if args.embedded is False:
        print(
            "Method 1 of combination is used: The input figures will be made subplots in the new figure."
        )
        if args.dimension is None:
            n_cols, n_rows = plotting_utils.get_fig_dimension(len(args.figs))
        else:
            if len(args.dimension) != 2:
                raise utils.ParameterError(
                    "Wrong number of arguments for specifying the dimension of the subplots."
                )
            else:
                n_cols = args.dimension[0]
                n_rows = args.dimension[1]

        if args.size is None:
            # estimate the size of the figure to enable a tight layout
            length = n_cols * 5
            width = n_rows * 4
            while length > 30 or width > 30:
                length *= 0.8
                width *= 0.8
            fig = plt.figure(figsize=(length, width))
        else:
            if len(args.size) != 2:
                raise utils.ParameterError(
                    "Wrong number of arguments for specifying the figure size."
                )
            else:
                fig = plt.figure(figsize=tuple(args.size))

        if args.titles is not None:
            if len(args.figs) != len(args.titles):
                raise utils.ParameterError(
                    "The number of titles does not match the number of subplots."
                )

        # Step 2. Combine plots
        panel_labels='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i in range(len(args.figs)):
            image = cv2.imread(args.figs[i], cv2.IMREAD_COLOR)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            ax = fig.add_subplot(n_rows, n_cols, i + 1)
            plt.imshow(image_rgb)
            if args.border is True:
                plt.xticks([])
                plt.yticks([])
            elif args.border is False:
                plt.axis("off")
            if args.titles is not None:
                plt.title(args.titles[i])
            if args.annotate is True:
                plt.text(0.02, 0.95, f'{panel_labels[i]}', transform = ax.transAxes, fontsize=26, weight='bold')

        plt.tight_layout(rect=[0, 0, 1, 1])

    # Method 2: Embed one figure in the other
    else:
        print(
            "Method 2 of combination is used: The second figure will be embedded in the first one."
        )
        if len(args.figs) != 2:
            raise utils.ParameterError(
                "Only 2 figures should be specified if an embedded picture is wanted."
            )
        if len(args.pos_e) != 2:
            raise utils.ParameterError(
                "Wrong number of values for specifying the position of the embedded figure."
            )

        img1 = cv2.imread(args.figs[0], cv2.IMREAD_COLOR)
        img1_rgb = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)

        img2 = cv2.imread(args.figs[1], cv2.IMREAD_COLOR)
        img2_rgb = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)

        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.imshow(img1_rgb)  # parent figure
        plt.xticks([])
        plt.yticks([])
        if args.border is False:
            plt.axis("off")

        embed_config = args.pos_e
        embed_config.extend([args.size_e, args.size_e])
        embed_config = tuple(embed_config)
        inset_axes(
            ax,
            width="100%",
            height="100%",
            bbox_to_anchor=embed_config,
            bbox_transform=ax.transAxes,
        )

        # embedded figure
        if args.bgr is True:
            plt.imshow(img2)
        else:
            plt.imshow(img2_rgb)  # embedded figure
        plt.xticks([])
        plt.yticks([])
        if args.border_e is False:
            plt.axis("off")

    plt.tight_layout(rect=[0, 0, 1, 1])
    plt.savefig(f"{args.pngname}.png", dpi=600)
