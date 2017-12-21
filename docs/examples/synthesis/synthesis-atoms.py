"""Runs synthesis for specified atomic species separately. No molecules or hydrogen lines."""

import pyfant
import f311
import matplotlib.pyplot as plt
import a99

# ["<element name><ionization level>", ...] for which to draw panels
MY_SPECIES = ["Fe1", "Fe2", "Ca1", "Ca2", "Na1", "Si1"]

if __name__ == "__main__":
    pyfant.copy_star(starname="sun-grevesse-1996")
    pyfant.link_to_data()

    # Loads full atomic lines file
    fatoms = pyfant.FileAtoms()
    fatoms.load()

    runnables = []
    for elem_ioni in MY_SPECIES:
        atom = fatoms.find_atom(elem_ioni)

        # Creates atomic lines file object containing only one atom
        fatoms2 = pyfant.FileAtoms()
        fatoms2.atoms = [atom]

        ecombo = pyfant.Combo()
        # Overrides file "atoms.dat" with in-memory object
        ecombo.conf.file_atoms = fatoms2
        ecombo.conf.flag_output_to_dir = True
        oo = ecombo.conf.opt
        # Assigns synthesis range to match atomic lines range
        oo.llzero, oo.llfin = fatoms2.llzero, fatoms2.llfin
        # Turns off hydrogen lines
        oo.no_h = True
        # Turns off molecular lines
        oo.no_molecules = True

        runnables.append(ecombo)

    pyfant.run_parallel(runnables)

    # Draws figure
    f = plt.figure()
    a99.format_BLB()
    for i, (title, ecombo) in enumerate(zip(MY_SPECIES, runnables)):
        ecombo.load_result()
        plt.subplot(2, 3, i+1)
        f311.draw_spectra_overlapped([ecombo.result["spec"]],
                                   setup=f311.PlotSpectrumSetup(flag_xlabel=i/3 >= 1, flag_legend=False))
        plt.title(title)

    K = 1.
    a99.set_figure_size(plt.gcf(), 1300*K, 740*K)
    plt.tight_layout()
    plt.savefig("synthesis-atoms.png")
    plt.show()
