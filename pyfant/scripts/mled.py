#!/usr/bin/env python

"""Molecular lines file editor."""

import sys
import argparse
import logging
import pyfant
import a99


if __name__ == "__main__":
    a99.logging_level = logging.INFO
    a99.flag_log_file = True

    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=a99.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='molecules file name',
                        default=pyfant.FileMolecules.default_filename, nargs='?')
    args = parser.parse_args()

    m = pyfant.FileMolecules()
    m.load(args.fn)
    app = a99.get_QApplication([])
    form = pyfant.XFileMolecules()
    form.show()
    form.load(m)
    sys.exit(app.exec_())











