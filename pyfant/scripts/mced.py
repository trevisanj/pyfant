#!/usr/bin/env python

"""
Editor for molecular constants file

This application can edit files of class FileMolConsts.
"""

import sys
import argparse
import a99
import logging
import os
import pyfant


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":

    deffn = pyfant.FileMolConsts.default_filename

    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='Molecular constants file name',
                        default=deffn, nargs='?')
    args = parser.parse_args()

    if args.fn == deffn and not os.path.isfile(deffn):
        args.fn = None


    # Currently making copy of FileMolDB database and deleting afterwards
    moldb = pyfant.FileMolDB()
    moldb.init_default()
    try:
        fobj = None
        if args.fn is not None:
            fobj = pyfant.FileMolConsts()
            fobj.load(args.fn)
        app = a99.get_QApplication([])
        form = pyfant.XFileMolConsts(None)
        form.set_moldb(moldb)
        form.load(fobj)
        form.show()
    finally:
        try:
            os.unlink(moldb.filename)
        except FileNotFoundError:
            pass  # nevermind

    sys.exit(app.exec_())







