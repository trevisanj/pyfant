#!/usr/bin/env python3
"""
Opens several windows to show what is inside a NEWMARCS grid file.
"""

import argparse
import astrogear as ag
import logging


ag.logging_level = logging.INFO
ag.flag_log_file = True


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
   description=ag.VisModCurves.__doc__,
   formatter_class=ag.SmartFormatter
   )

  parser.add_argument('fn', type=str, help='NEWMARCS grid file name')

  args = parser.parse_args()

  m = pf.FileModBin()
  m.load(args.fn)


  v = ag.VisModCurves()
  v.title = args.fn
  v.use(m)
