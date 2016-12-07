#!/usr/bin/env python3

"""Testing widget"""

import pyfant as pf
from pyfant import *
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import argparse
import logging
# import a_WStateConst
from pyfant.convmol import a_WMolConst, moldb
import astroapi as aa

# from pyfant.gui import guiaux

def _format_title0(s):
    return "<h3>{}</h3>".format(s)

pf.logging_level = logging.INFO


app = aa.get_QApplication([])
form = pf.convmol.XConvMol()
form.w_mol.w_mol._populate()
form.show()
app.exec_()

aa = form.get_all_consts()
for key, value in aa.items():
    print(key, "=", value)

# for fn in form.w_state._fieldnames:
#     print("{} = {}".format(fn, form.w_state[fn]))


