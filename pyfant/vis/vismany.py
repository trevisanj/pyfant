"""Visualization classes for pyfant file types"""

import pyfant
from f311 import Vis
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D  # yes, required (see below)
import a99


__all__ = ["VisFileToH", "draw_toh", "VisAtoms", "VisMolecules", "VisMain", "VisAbonds",]


class VisFileToH(Vis):
    """
    Plots hydrogen lines: each atmospheric layer is plotted as a y-axis-dislocated
    Spectrum in a 3D plot.
    """

    input_classes = (pyfant.FileToH,)
    action = "Visualize hydrogen lines profiles"

    def _do_use(self, r):
        fig = plt.figure()
        mpl.rcParams['legend.fontsize'] = 10
        fig.canvas.setWindowTitle(self.title)  # requires the Axes3D module
        # requires the Axes3D module
        ax = fig.add_subplot(projection='3d')
        draw_toh(r, ax)
        # ax.set_zlabel('log10(Intensity)')
        # ax.set_zlabel('?')
        plt.tight_layout()
        plt.show()


def draw_toh(r, ax):
    x = np.concatenate((2 * r.lambdh[0] - r.lambdh[-2::-1], r.lambdh))
    _y = np.ones(len(x))
    for i in range(r.th.shape[1]):
        z = np.concatenate((r.th[-2::-1, i], r.th[:, i]))
        # ax.plot(x, _y * (i + 1), np.log10(z), label='a', color='k')
        ax.plot(x, _y * (i + 1), z, label='a', color='k')
    ax.set_xlabel('Wavelength ($\AA$)')
    ax.set_ylabel("Atmospheric layer #")


# # Editors

class VisAtoms(Vis):
    """Opens the ated window."""
    input_classes = (pyfant.FileAtoms,)
    action = "Edit using atomic lines editor"

    def _do_use(self, r):
        form = a99.keep_ref(pyfant.XFileAtoms(self.parent_form))
        form.load(r)
        form.show()


class VisMolecules(Vis):
    """Opens the mled window."""
    input_classes = (pyfant.FileMolecules,)
    action = "Edit using molecular lines editor"

    def _do_use(self, r):
        form = a99.keep_ref(pyfant.XFileMolecules(self.parent_form))
        form.load(r)
        form.show()


class VisMain(Vis):
    """Opens the mained window."""
    input_classes = (pyfant.FileMain,)
    action = "Edit using main configuration file editor"

    def _do_use(self, r):
        form = a99.keep_ref(pyfant.XFileMain(self.parent_form, r))
        form.show()


class VisAbonds(Vis):
    """Opens the abed window."""
    input_classes = (pyfant.FileAbonds,)
    action = "Edit using abundances file editor"

    def _do_use(self, r):
        form = a99.keep_ref(pyfant.XFileAbonds(self.parent_form, r))
        form.show()


class VisWhatever(Vis):
    cls_form = None

    def _do_use(self, r):
        cls_form = self._get_cls_form()
        form = a99.keep_ref(cls_form(self.parent_form, r))
        form.show()

    def _get_cls_form(self):
        """Method to return the class of the form to instantiate"""
        raise NotImplementedError()


class VisOptions(VisWhatever):
    """Allows for editing a FileOptions object"""
    input_classes = (pyfant.FileOptions,)
    action = "Edit using command-line options file editor"

    def _get_cls_form(self):
        return pyfant.XFileOptions

