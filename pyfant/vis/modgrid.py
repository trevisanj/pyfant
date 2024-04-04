from mpl_toolkits.mplot3d import Axes3D  # yes, required
import matplotlib.pyplot as plt
import pyfant

__all__ = ["plot_mod_grid"]


def plot_mod_grid(ff, title=None):
    """Plots Teff x glog x metallicity in 3D"""

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    teff, glog, asalog = [], [], []
    for f in ff:
        assert isinstance(f, pyfant.FileModBin)
        for r in f.records:
            teff.append(r.teff)
            glog.append(r.glog)
            asalog.append(r.asalog)
    ax.scatter(teff, glog, asalog, c='r', s=60, marker='o')
    ax.set_xlabel('teff')
    ax.set_ylabel('glog')
    ax.set_zlabel('asalog')
    fig.canvas.setWindowTitle('teff-glog-asalog scatterplot')
    plt.show()
