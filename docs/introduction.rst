Introduction
============
`MD_plotting_toolkit` is a Python package providing useful tools for 
visualizing simulation data obtained from molecular dynamics (especially
for GROMACS). The tools available in this package are aimed to enable 
easy one-line command to generate publication-quality figures. With entry
points set upon the installation of this package, these commands can be
executed in any directory from the terminal. These comands include `plot_xy`,
`plot_xyz`, `plot_hist`, `plot_bar`, `plot_violin`, `plot_matrix`, and 
`combine_plots`. For more information about these commands, please refer
to the tutorials.

Installation
============
The package has not been published to PyPI, but can be installed from our
`github repository`_ using the following commands:
::

    git clone https://github.com/wehs7661/MD_plotting_toolkit.git
    cd MD_plotting_toolkit/
    pip install -e .

Note that this package requries a bunch of other Python packages to be installed,
including NumPy, SciPy, matplotlib, pymbar, natsort, and argparse. 

.. _`github repository`: https://github.com/wehs7661/MD_plotting_toolkit.git
