#!/usr/bin/env python

"""
Atomic lines file editor
"""

import sys
import argparse
import logging
import a99
import pyfant


a99.logging_level = logging.INFO
a99.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='atoms file name',
                        default=pyfant.FileAtoms.default_filename, nargs='?')
    args = parser.parse_args()

    m = pyfant.FileAtoms()
    m.load(args.fn)
    app = a99.get_QApplication([])
    form = pyfant.XFileAtoms()
    form.show()
    form.load(m)
    sys.exit(app.exec_())
