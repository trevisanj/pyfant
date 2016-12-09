#!/usr/bin/env python3

"""
Prints table of diatomic molecular constants

If ID is specified, prints data for single molecule;
otherwise, prints full table
"""

import pyfant as pf
import argparse
import logging
import astroapi as aa


pf.logging_level = logging.INFO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=aa.SmartFormatter
    )
    parser.add_argument('ID', type=str, help='HITRAN Molecule ID',
                        default='(all)', nargs='?')
    args = parser.parse_args()

    kwargs = {}
    if not args.ID == "(all)":
        kwargs["molecule.ID"] = args.ID

    pf.hitrandb.print_isotopologues(**kwargs)