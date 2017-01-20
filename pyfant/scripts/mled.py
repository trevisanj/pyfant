#!/usr/bin/env python3

"""Molecular lines file editor."""

import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import argparse
import logging
import pyfant as pf
import hypydrive as hpd


if __name__ == "__main__":
    hpd.logging_level = logging.INFO
    hpd.flag_log_file = True

    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=hpd.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='molecules file name',
                        default=pf.FileMolecules.default_filename, nargs='?')
    args = parser.parse_args()

    m = pf.FileMolecules()
    m.load(args.fn)
    app = hpd.get_QApplication([])
    form = pf.XFileMolecules()
    form.show()
    form.load(m)
    sys.exit(app.exec_())











