"""Matplotlib-related routines"""


__all__ = ["set_facecolor_white", "format_BLB", "format_legend", "set_figure_size"]


from matplotlib import rc, pyplot as plt
from matplotlib.ticker import AutoMinorLocator


def set_facecolor_white():
    rc("figure", facecolor="white")

def format_BLB():
    """Sets some formatting options in Matplotlib."""
    rc("figure", facecolor="white")
    rc('font', family = 'serif', size=14) #, serif = 'cmr10')
    rc('xtick', labelsize=14)
    rc('ytick', labelsize=14)
    rc('axes', linewidth=1)
    rc('xtick.major', size=4, width=1)
    rc('xtick.minor', size=2, width=1)
    rc('ytick.major', size=4, width=1)
    rc('ytick.minor', size=2, width=1)
    # plt.minorticks_on()
    #minorLocator = AutoMinorLocator()
    # plt.tick_params(which="both", width=2)
    # plt.tick_params(which="major", width=2)
    #rc('text', usetex=True)

def format_legend(leg):
    """Sets some formatting options in a matplotlib legend object."""
    # rect = leg.get_frame()
    # rect.set_linewidth(2.)

def set_figure_size(fig, width, height):
    """Sets MatPlotLib figure width and height in pixels

    Reference: https://github.com/matplotlib/matplotlib/issues/2305/
    """
    dpi = float(fig.get_dpi())
    fig.set_size_inches(float(width) / dpi, float(height) / dpi)
