#!/usr/bin/env python
"""
Converts VALD3 atomic/molecular lines file to PFANT atomic lines file.

Molecular lines and certain elements are skipped.

Usage examples:

    To skip only H and He:
    > vald3-to-atoms --skip "H, He"


"""

import argparse
import logging
import numpy as np
import a99
import pyfant
import sys


a99.logging_level = logging.INFO
a99.flag_log_file = True


DEFOUT = "atoms-untuned-<fn_input>"

TO_REMOVE = "H, He, F, Ne, P, Ar, Cl, As, Br, Kr, Xe"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=a99.SmartFormatter)
    parser.add_argument('fn_input', type=str, help='input file name', nargs=1)
    parser.add_argument('fn_output', type=str, help='output file name', nargs="?",
     default=DEFOUT)
    parser.add_argument('--min_algf', type=float, nargs='?', default=-7,
     help='minimum algf (log gf)')
    parser.add_argument('--max_kiex', type=float, nargs='?', default=15,
     help='maximum kiex')
    parser.add_argument("-s", "--skip", type=str, nargs='?', default=TO_REMOVE,
     help='list of elements to skip (use quotes and separate elements by commas)')

    args = parser.parse_args()
    logger = a99.get_python_logger()

    fn_out = args.fn_output
    if fn_out == DEFOUT:
        fn_out = "atoms-untuned-"+args.fn_input[0]

    logger.info("Converting file...")
    with open(args.fn_input[0], 'r') as file_:
        file_atoms = pyfant.vald3_to_atoms(file_)

    n0 = file_atoms.num_lines
    logger.info("Number of lines before filtering: %d" % n0)

    logger.info("    Removing all (algf < %g)..." % args.min_algf)
    file_atoms.filter(lambda line: line.algf >= args.min_algf)
    logger.info("    Number of lines removed: %d" % (n0-file_atoms.num_lines))

    n0 = file_atoms.num_lines
    logger.info("    Filtering all (kiex > %g)..." % args.max_kiex)
    file_atoms.filter(lambda line: line.kiex <= args.max_kiex)
    logger.info("    Number of lines removed: %d" % (n0-file_atoms.num_lines))


    # Skipping elements (actually removing them after conversion is done)
    skip = [x.strip() for x in args.skip.split(",")]
    for ele in skip:
        n0 = file_atoms.num_lines
        logger.info("    Removing '{}' lines...".format(ele))
        file_atoms.remove_element(ele)
        logger.info("    Number of '{}' lines removed: {}".format(ele, n0-file_atoms.num_lines))

    logger.info("Number of lines after filtering: %d" % file_atoms.num_lines)

    logger.info("Saving file...")
    file_atoms.save_as(fn_out)
    print("File %s was successfully created." % fn_out)
    zz = file_atoms.zinf
    if len(zz) > 0:
        if np.all(zz == zz[0]):
            logger.warning("All zinf's set to %g. Now they must be fine-tuned with tune-zinf.py." % zz[0])
