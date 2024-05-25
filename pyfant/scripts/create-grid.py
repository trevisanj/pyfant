#!/usr/bin/env python

"""
Merges several atmospheric models into a single file (_i.e._, the "grid")

"Collects" several files in current directory and creates a single file
containing atmospheric model grid.

Working modes (option "-m"):
 "opa" (default mode): looks for MARCS[1] ".mod" and ".opa" text file pairs and
                       creates a *big* binary file containing *all* model
                       information including opacities.
                       Output will be in ".moo" format.

 "modtxt": looks for MARCS ".mod" text files only. Resulting grid will not contain
           opacity information.
           Output will be in binary ".mod" format.


 "modbin": looks for binary-format ".mod" files. Resulting grid will not contain
           opacity information.
           Output will be in binary ".mod" format.

References:
  [1] http://marcs.astro.uu.se/

.
.
.
"""

import argparse
import logging
import glob
import os
import sys
import a99
import pyfant
import tabulate

a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
     )
    parser.add_argument('--pattern', type=str, help='file name pattern (with wildcards)',
     nargs="?", default="*.mod")
    parser.add_argument('-m', '--mode', type=str, nargs="?", default="opa",
     choices=["opa", "modtxt", "modbin"],
     help='working mode (see description above)')
    VDOM = "\"grid.moo\" or \"grid.mod\", depending on mode"
    parser.add_argument('fn_output', type=str, help='output file name', nargs="?",
     default=VDOM)

    args = parser.parse_args()

    logger = a99.get_python_logger()

    if args.fn_output == VDOM:
        args.fn_output = "grid.moo" if args.mode == "opa" else "grid.mod"
        logger.info("Setting output filename to '{0!s}'".format(args.fn_output))

    filenames = glob.glob("./"+args.pattern)
    n = len(filenames)
    print("{0:d} file{1!s} matching pattern '{2!s}'".format(n, "s" if n != 1 else "", args.pattern))

    records = []
    skipped, reasons = [], []
    for filename in filenames:
        if args.mode == "opa":
            name = os.path.splitext(os.path.basename(filename))[0]
            print("Considering files '{0!s}'+('.mod', '.opa') ...".format(name))
            try:
                f = pyfant.FileModTxt()
                f.load(filename)
                g = pyfant.FileOpa()
                g.load(name+".opa")
                r = pyfant.MooRecord()
                r.from_marcs_files(f, g)
                records.append(r)
            except BaseException as e:
                logger.exception("Error loading '{0!s}', skipping...".format(name))
                skipped.append(name)
                reasons.append(str(e))
        else:
            nameext = os.path.basename(filename)
            print("Considering file '{0!s}'+('.mod', '.opa') ...".format(nameext))
            try:
                if args.mode == "modtxt":
                    f = pyfant.FileModTxt()
                    f.load(filename)
                    records.append(f.record)
                else:
                    f = pyfant.FileModBin()
                    f.load(filename)
                    records.extend(f.records)
            except BaseException as e:
                logger.exception("Error loading file '{0!s}', skipping...".format(filename))
                skipped.append(filename)
                reasons.append(str(e))

    if len(records) == 0:
        print("No valid models found, nothing to save.")
        sys.exit()

    records.sort(key=lambda r: r.asalog*1e10+r.teff*100+r.glog)

    if args.mode == "opa":
        g = pyfant.FileMoo()
    else:
        g = pyfant.FileModBin()
    g.records = records
    g.save_as(args.fn_output)

    if skipped:
        logger.info("\n".join(a99.format_box(f"Files skipped ({len(skipped)})")))
        logger.info(tabulate.tabulate(zip(skipped, reasons), ["Name", "Reason"]))

    logger.info(f"Final number of records: {len(records)}")

    print("Successfully created file '{0!s}'".format(args.fn_output))
