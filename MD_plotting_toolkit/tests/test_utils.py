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
Unit tests for the module `MD_plotting_toolkit.utils`.
"""
import os

import MD_plotting_toolkit.utils as utils

current_path = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(current_path, "sample_outputs")
outfile = output_path + "/test_utils.txt"


class Test_Logging:
    def test_init(self):
        L = utils.Logging(outfile)
        assert vars(L) == {"f": outfile}

    def test_Logging(self):
        L = utils.Logging(outfile)
        L.logger("Test")

        infile = open(outfile, "r")
        lines = infile.readlines()
        infile.close()

        assert os.path.isfile(outfile) is True
        assert "Test\n" == lines[0]
