#!/usr/bin/env python3

"""
Atomic lines file editor
"""

import sys
import argparse
import logging
import pyfant as pf
import astrogear as ag
import logging


ag.logging_level = logging.INFO
ag.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=ag.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='atoms file name',
                        default=pf.FileAtoms.default_filename, nargs='?')
    args = parser.parse_args()

    m = pf.FileAtoms()
    m.load(args.fn)
    app = ag.get_QApplication([])
    form = pf.XFileAtoms()
    form.show()
    form.load(m)
    sys.exit(app.exec_())
