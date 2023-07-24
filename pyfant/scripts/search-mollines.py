"""
Searches molecular lines around given wavelength interval

Included inverval will be central_lambda-tolerance <= line_wavelength <= central_lambra+tolerance.
"""

import argparse, logging, a99, pyfant, tabulate


a99.logging_level = logging.INFO
a99.flag_log_file = False


# Searching which molecule and (v', v'') has line with given wavelength
import pyfant, f311, a99, a107

# FILENAME = "molecules.dat"
# FILENAME = "CO_dV11_stable.PFANT.dat"
# FILENAME = "CN1214-Brookeetal-2014-list.PFANT.dat"
# LAMBDA = 16388.6
# FILENAME = "molecule-CNredAX.dat"
FILENAME = "molecules.dat"
# LAMBDA = 15577.42
# LAMBDA = 15568.8
LAMBDA = 15328.5

TOLERANCE = 1

def pprint(s):
    for line in s.split("\n"):
        print(line)


def main(args):
    central_lambda = args.central_lambda
    tolerance = args.tolerance
    l0 = central_lambda-tolerance
    l1 = central_lambda+tolerance

    f = pyfant.FileMolecules()
    f.load(args.fn_input)

    mols = []
    rows = []
    header = ["Molecule #", "Set-of-lines #", "vl", "v2l", "lmbdam", "sj", "jj", "branch"]
    floatfmts = ["", "", "", "", ".4f", "", "", ""]

    for i_m, mol in enumerate(f.molecules):
        found = False
        for i_s, sol_ in enumerate(mol.sol):
            for i, (lmbdam, sj, jj, branch) in enumerate(zip(sol_.lmbdam, sol_.sj, sol_.jj, sol_.branch)):
                if l0 <= lmbdam <= l1:
                    rows.append([i_m+1, i_s+1, sol_.vl, sol_.v2l, lmbdam, sj, jj, branch])

                    if not found:
                        mols.append([i_m+1, mol.description])
                        found = True

    pprint("\n"+"\n".join(a99.format_box("Lines found")))
    pprint(tabulate.tabulate(rows, header, floatfmt=floatfmts))
    pprint("\n"+"\n".join(a99.format_box("Molecules indexes from table above")))
    pprint(tabulate.tabulate(mols, ["Molecule #", "Description"]))




if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
     )
    parser.add_argument('central_lambda', type=float,
     help='Central wavelength (angstrom)')
    parser.add_argument('fn_input', type=str, help='input file name')
    parser.add_argument('-t', "--tolerance", type=float, default=0.5,
                        help='Wavelength tolerance around central wavelength (left and right)')

    args = parser.parse_args()

    main(args)