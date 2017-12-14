#!/usr/bin/env python

"""
Editor for molecules SQLite database

This application can edit files of class FileMolDB.
"""

import pyfant
import sys
import argparse
import a99
import logging
import os


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":

    deffn = pyfant.FileMolDB.default_filename

    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='Molecules database file name',
                        default=deffn, nargs='?')
    args = parser.parse_args()

    if args.fn == deffn and not os.path.isfile(deffn):
        args.fn = None

    m = None
    if args.fn is not None:
        m = pyfant.FileMolDB()
        m.load(args.fn)
    app = a99.get_QApplication([])
    form = pyfant.XFileMolDB(None, [m,])
    form.showMaximized()
    sys.exit(app.exec_())







