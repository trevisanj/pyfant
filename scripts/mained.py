#!/usr/bin/env python3

"""Main configuration file editor."""

import sys
from PyQt4.QtGui import *
import argparse
import logging
import pyfant as pf
import pyscellanea as pa


pa.logging_level = logging.INFO
pa.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=pa.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='main configuration file name', default='main.dat', nargs='?')
    args = parser.parse_args()

    m = pf.FileMain()
    m.load(args.fn)
    app = pa.get_QApplication([])
    form = pf.XFileMain()
    form.load(m)
    form.show()
    sys.exit(app.exec_())
