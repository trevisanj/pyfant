#!/usr/bin/env python3
"""
Plots one record of a binary .mod file (e.g., modeles.mod, newnewm050.mod).
"""

import hypydrive as hpd
import argparse
import matplotlib.pyplot as plt
import logging


hpd.logging_level = logging.INFO
hpd.flag_log_file = True



if __name__ == "__main__":
  parser = argparse.ArgumentParser(
   description=hpd.VisModRecord.__doc__,
   formatter_class=hpd.SmartFormatter
   )

  parser.add_argument('--inum', type=int, default=1, help='Record number (>= 1)')
  parser.add_argument('fn', type=str, help='.mod binary file name', default='modeles.mod', nargs='?')

  args = parser.parse_args()

  m = pf.FileModBin()
  m.load(args.fn)

  v = hpd.VisModRecord()
  v.title = args.fn
  v.inum = args.inum
  v.use(m)
  plt.show()

