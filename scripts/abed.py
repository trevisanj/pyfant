#!/usr/bin/env python3

"""Abundances file editor"""

import sys
from PyQt4.QtGui import *
import argparse
import pyfant as pf
import pyscellanea as pa
import logging


pa.logging_level = logging.INFO
pa.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=pa.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='abundances file name', default='abonds.dat', nargs='?')
    args = parser.parse_args()

    m = pf.FileAbonds()
    m.load(args.fn)
    app = pa.get_QApplication([])
    form = pf.XFileAbonds()
    form.show()
    form.load(m)
    sys.exit(app.exec_())
