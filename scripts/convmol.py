#!/usr/bin/env python3

"""Converion of molecular lines data to PFANT format"""

import sys
import argparse
import pyfant as pf
import astroapi as aa
import logging
import os


aa.logging_level = logging.INFO
aa.flag_log_file = True


if __name__ == "__main__":

    deffn = pf.FileMolDB.default_filename

    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=aa.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='Molecular constants database file name',
                        default=deffn, nargs='?')
    args = parser.parse_args()

    if args.fn == deffn and not os.path.isfile(deffn):
        args.fn = None

    m = None
    if args.fn is not None:
        m = pf.FileMolDB()
        m.load(args.fn)
    app = aa.get_QApplication([])
    form = pf.convmol.XConvMol(None, m)
    form.show()
    sys.exit(app.exec_())







