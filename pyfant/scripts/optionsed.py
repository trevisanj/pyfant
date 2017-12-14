#!/usr/bin/env python

"""PFANT command-line options file editor."""

import sys
import argparse
import logging
import a99
import pyfant
import os

a99.logging_level = logging.INFO
a99.flag_log_file = True

CLS_FILE = pyfant.FileOptions
CLS_FORM = pyfant.XFileOptions

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=a99.SmartFormatter)
    parser.add_argument('fn', type=str, help="{} file name".format(a99.get_obj_doc0(CLS_FILE)),
                        default=CLS_FILE.default_filename, nargs='?')
    args = parser.parse_args()

    app = a99.get_QApplication([])
    form = CLS_FORM()

    if not os.path.isfile(args.fn):
        a99.get_python_logger().info("File not found: '{}'".format(args.fn))
    else:
        form.load_filename(args.fn)

    form.show()
    sys.exit(app.exec_())
