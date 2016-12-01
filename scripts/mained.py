#!/usr/bin/env python3

"""Main configuration file editor."""

import sys
from PyQt4.QtGui import *
import argparse
import logging
import pyfant as pf
import astroapi as aa


aa.logging_level = logging.INFO
aa.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=aa.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='main configuration file name', default='main.dat', nargs='?')
    args = parser.parse_args()

    m = pf.FileMain()
    m.load(args.fn)
    app = aa.get_QApplication([])
    form = pf.XFileMain()
    form.load(m)
    form.show()
    sys.exit(app.exec_())
