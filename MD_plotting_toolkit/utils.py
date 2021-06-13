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
The `utils` module provide various general utilities.
"""


class Logging:
    def __init__(self, file_name):
        self.f = file_name

    def logger(self, *args, **kwargs):
        """
        Prints the results on screen and to the file free_energy_results.txt

        Parameters
        ---------
        file_name : str
            The file name of the output.
        """
        print(*args, **kwargs)
        with open(self.f, "a") as f:
            print(file=f, *args, **kwargs)


class ParameterError(Exception):
    """
    An error due to improperly specified parameters has been deteced.
    """

    pass


class InputFileError(Exception):
    """
    An error indicating that the input file was not properly specified.
    """

    pass
