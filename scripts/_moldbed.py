#!/usr/bin/env python3

"""
Molecular Constants DB editor
"""

import sys
import argparse
import logging
import pyfant as pf
import pyscellanea as pa
import logging
import os


pa.logging_level = logging.INFO
pa.flag_log_file = True


if __name__ == "__main__":

    deffn = pf.FileMolDB.default_filename

    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=pa.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='SQLite file name',
                        default=deffn, nargs='?')
    args = parser.parse_args()

    if args.fn == deffn and not os.path.isfile(deffn):
        args.fn = None

    m = None
    if args.fn is not None:
        m = pf.FileMolDB()
        m.load(args.fn)
    app = pa.get_QApplication([])
    form = pf.convmol.XFileMolDB(None, m)
    form.show()
    sys.exit(app.exec_())
