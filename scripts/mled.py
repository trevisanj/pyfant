#!/usr/bin/env python3

"""Molecular lines file editor."""

import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import argparse
import logging
import pyfant as pf
import astroapi as aa


if __name__ == "__main__":
    aa.logging_level = logging.INFO
    aa.flag_log_file = True

    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=aa.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='molecules file name',
                        default=pf.FileMolecules.default_filename, nargs='?')
    args = parser.parse_args()

    m = pf.FileMolecules()
    m.load(args.fn)
    app = aa.get_QApplication([])
    form = pf.XFileMolecules()
    form.show()
    form.load(m)
    sys.exit(app.exec_())
