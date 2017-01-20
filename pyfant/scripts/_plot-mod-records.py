#!/usr/bin/env python3
"""
Opens several windows to show what is inside a NEWMARCS grid file.
"""

import argparse
import hypydrive as hpd
import logging


hpd.logging_level = logging.INFO
hpd.flag_log_file = True


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
   description=hpd.VisModCurves.__doc__,
   formatter_class=hpd.SmartFormatter
   )

  parser.add_argument('fn', type=str, help='NEWMARCS grid file name')

  args = parser.parse_args()

  m = pf.FileModBin()
  m.load(args.fn)


  v = hpd.VisModCurves()
  v.title = args.fn
  v.use(m)
