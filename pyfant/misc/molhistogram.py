import matplotlib.pyplot as plt, numpy, a99, numpy as np

__all__ = ["plot_molhistogram"]

def plot_molhistogram(mol, num_bins=100, color=None, label=None):
    """Plots histogram that gives a general profile of where the lines are wavelength-wise"""
    import pyfant
    assert isinstance(mol, pyfant.Molecule)

    x0 = mol.llzero
    x1 = mol.llfin
    data = mol.lmbdam

    bins = np.logspace(np.log10(x0), np.log10(x1), num_bins+1, endpoint=True)
    h = np.histogram(data, bins=bins, density=False)[0]
    widths = np.diff(bins)

    ax = plt.gca()
    plt.bar(bins[:-1], h, width=widths, align="edge", color=color, label=label)
    plt.xscale("log")

    plt.xlabel("Wavelength ($\AA$)")
    plt.ylabel("Number of lines")
    a99.format_BLB()
