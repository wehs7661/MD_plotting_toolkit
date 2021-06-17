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
The `plot_xyz` module a contour plot and a 3D plot given x, y, and z data.
"""
def initialize():
    parser = argparse.ArgumentParser(
        description='This code plots the angle and dihedral angle distribution for the modified System 2.')
    parser.add_argument('-t',
                        '--trial',
                        type=int)
    parser.add_argument('-n',
                        '--n_max',
                        type=int,
                        default=10,
                        help='The upper bound of n for plotting')
    args_parse = parser.parse_args()
    return args_parse