#!/usr/bin/env python3
"""
Plots one record of a binary .mod file (e.g., modeles.mod, newnewm050.mod).
"""

import astrogear as ag
import argparse
import matplotlib.pyplot as plt
import logging


ag.logging_level = logging.INFO
ag.flag_log_file = True



if __name__ == "__main__":
  parser = argparse.ArgumentParser(
   description=ag.VisModRecord.__doc__,
   formatter_class=ag.SmartFormatter
   )

  parser.add_argument('--inum', type=int, default=1, help='Record number (>= 1)')
  parser.add_argument('fn', type=str, help='.mod binary file name', default='modeles.mod', nargs='?')

  args = parser.parse_args()

  m = pf.FileModBin()
  m.load(args.fn)

  v = ag.VisModRecord()
  v.title = args.fn
  v.inum = args.inum
  v.use(m)
  plt.show()

