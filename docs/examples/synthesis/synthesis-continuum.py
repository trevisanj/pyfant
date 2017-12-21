"""Runs synthesis over large wavelength range, then plots continuum"""

import pyfant
import f311
import matplotlib.pyplot as plt
import a99

if __name__ == "__main__":
    # Copies files main.dat and abonds.dat to local directory (for given star)
    pyfant.copy_star(starname="sun-grevesse-1996")
    # Creates symbolic links to all non-star-specific files, such as atomic & molecular lines,
    # partition functions, etc.
    pyfant.link_to_data()

    # Creates object that will run the four Fortran executables (innewmarcs, hydro2, pfant, nulbad)
    obj = pyfant.Combo()
    oo = obj.conf.opt
    # synthesis interval start (angstrom)
    oo.llzero = 2500
    # synthesis interval end (angstrom)
    oo.llfin = 30000
    # savelength step (angstrom)
    oo.pas = 1.
    # Turns off hydrogen lines
    oo.no_h = True
    # Turns off atomic lines
    oo.no_atoms = True
    # Turns off molecular lines
    oo.no_molecules = True

    obj.run()
    obj.load_result()
    print("obj.result = {}".format(obj.result))
    res = obj.result
    f311.draw_spectra_stacked([res["cont"]], setup=f311.PlotSpectrumSetup(fmt_ylabel=None))
    K = .75
    a99.set_figure_size(plt.gcf(), 1300*K, 450*K)
    plt.tight_layout()
    plt.savefig("continuum.png")
    plt.show()
