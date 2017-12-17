"""
Calculates hydrogen lines profiles, then plots them in several 3D subplots
"""

import pyfant
import a99
import os
import shutil
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # yes, required (see below)

def mylog(*args):
    print("^^ {}".format(", ".join(args)))


def main(flag_cleanup=True):
    tmpdir = a99.new_filename("hydrogen-profiles")

    # Saves current directory
    pwd = os.getcwd()
    mylog("Creating directory '{}'...".format(tmpdir))
    os.mkdir(tmpdir)
    try:
        pyfant.link_to_data()
        _main()
    finally:
        # Restores current directory
        os.chdir(pwd)
        # Removes temporary directory
        if flag_cleanup:
            mylog("Removing directory '{}'...".format(tmpdir))
            shutil.rmtree(tmpdir)
        else:
            mylog("Not cleaning up.")


def _main():
    fm = pyfant.FileMain()
    fm.init_default()
    fm.llzero, fm.llfin = 1000., 200000.  # spectral synthesis range in Angstrom

    ei = pyfant.Innewmarcs()
    ei.conf.file_main = fm
    ei.run()
    ei.clean()

    eh = pyfant.Hydro2()
    eh.conf.file_main = fm
    eh.run()
    eh.load_result()
    eh.clean()

    _plot_profiles(eh.result["profiles"])


def _plot_profiles(profiles):
    fig = plt.figure()
    i = 0
    for filename, ftoh in profiles.items():
        if ftoh is not None:
            mylog("Drawing '{}'...".format(filename))
            # ax = plt.subplot(2, 3, i+1)
            ax = fig.add_subplot(2, 3, i+1, projection='3d')
            ax.set_title(filename)
            pyfant.draw_toh(ftoh, ax)
            i += 1

    plt.tight_layout()
    plt.savefig("hydrogen-profiles.png")
    plt.show()


if __name__ == "__main__":
    main(flag_cleanup=True)