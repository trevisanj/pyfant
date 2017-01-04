#!/usr/bin/env python3

"""Molecular lines file editor."""

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import argparse
import logging
import pyfant as pf
import pyscellanea as pa


if __name__ == "__main__":
    pa.logging_level = logging.INFO
    pa.flag_log_file = True

    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=pa.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='molecules file name',
                        default=pf.FileMolecules.default_filename, nargs='?')
    args = parser.parse_args()

    m = pf.FileMolecules()
    m.load(args.fn)
    app = pa.get_QApplication([])
    form = pf.XFileMolecules()
    form.show()
    form.load(m)
    sys.exit(app.exec_())











