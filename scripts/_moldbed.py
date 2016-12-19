#!/usr/bin/env python3

"""
Molecular Constants DB editor
"""

import sys
import argparse
import logging
import pyfant as pf
import astroapi as aa
import logging


aa.logging_level = logging.INFO
aa.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=aa.SmartFormatter
    )
    parser.add_argument('fn', type=str, help='SQLite file name',
                        default=None, nargs='?')
    args = parser.parse_args()

    m = None
    if args.fn is not None:
        m = pf.FileMolDB(None, m)
        m.load(args.fn)
    app = aa.get_QApplication([])
    form = pf.convmol.XFileMolDB()
    form.show()
    sys.exit(app.exec_())
