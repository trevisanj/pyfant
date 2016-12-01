#!/usr/bin/env python3
"""
Cuts molecular lines file to wavelength interval specified

The interval is [llzero, llfin]
"""


import argparse
import logging
import pyfant as pf
import astroapi as aa


aa.logging_level = logging.INFO
aa.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=aa.SmartFormatter
     )
    parser.add_argument('llzero', type=float, nargs=1,
     help='lower wavelength boundary (angstrom)')
    parser.add_argument('llfin', type=float, nargs=1,
     help='upper wavelength boundary (angstrom)')
    parser.add_argument('fn_input', type=str, help='input file name', nargs=1)
    parser.add_argument('fn_output', type=str, help='output file name', nargs=1)

    args = parser.parse_args()

    file_molecules = pf.FileMolecules()
    file_molecules.load(args.fn_input[0])

    lmbdam = file_molecules.lmbdam
    m, M = min(lmbdam), max(lmbdam)

    print("Original interval: [%g, %g]" % (m, M))
    print("New interval: [%g, %g]" % (args.llzero[0], args.llfin[0]))

    file_molecules.cut(args.llzero[0], args.llfin[0])
    file_molecules.save_as(args.fn_output[0])
    print("Successfully created file '%s'" % args.fn_output[0])
