__all__ = ["XQuery"]

import collections
import copy
import matplotlib.pyplot as plt
from pylab import MaxNLocator
import numbers
import numpy as np
import os
import os.path
from itertools import product, combinations, cycle
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pyfant import *
from pyfant.datatypes.filesplist import *
from pyfant.gui import *
from .basewindows import *
from .a_WChooseSpectrum import *
from .a_XScaleSpectrum import *
from .a_WSpectrumCollection import *


class XQuery(XLogMainWindow):
    """Rudimentary query system for SpectrumCollection"""

    def __init__(self, parent=None, file_main=None, file_abonds=None):
        XLogMainWindow.__init__(self, parent)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        self.setWindowTitle(get_window_title("Query"))

        self.splist = None

        # # Central layout
        cw = self.centralWidget = QWidget()
        self.setCentralWidget(cw)
        lantanide = self.centralLayout = QVBoxLayout(cw)
        lantanide.setMargin(1)
        # self.setLayout(lantanide)

        lgrid = keep_ref(QGridLayout())
        lantanide.addLayout(lgrid)
        lgrid.setMargin(0)
        lgrid.setVerticalSpacing(4)
        lgrid.setHorizontalSpacing(5)

        # field map: [(label widget, edit widget, field name, short description, long description), ...]
        pp = self._map0 = []
        ###
        x = keep_ref(QLabel())
        y = self.edit_expr = QLineEdit("SLB_SNR()")
        x.setBuddy(y)
        pp.append((x, y, "&Block expresion", "Other examples: 'SLB_MergeDown(np.mean)'", ""))
        ###
        x = keep_ref(QLabel())
        y = self.edit_group_by = QLineEdit()
        x.setBuddy(y)
        pp.append((x, y, "'&Group by' fieldnames", "Comma-separated without quotes", ""))

        for i, (label, edit, name, short_descr, long_descr) in enumerate(pp):
            # label.setStyleSheet("QLabel {text-align: right}")
            assert isinstance(label, QLabel)
            label.setText(enc_name_descr(name, short_descr))
            label.setAlignment(Qt.AlignRight)
            lgrid.addWidget(label, i, 0)
            lgrid.addWidget(edit, i, 1)
            label.setToolTip(long_descr)
            edit.setToolTip(long_descr)

        lgo = QHBoxLayout()
        lantanide.addLayout(lgo)
        ###
        lgo.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        ###
        b = keep_ref(QPushButton("&Run"))
        b.clicked.connect(self.on_run)
        lgo.addWidget(b)

        w = self.wsptable = WSpectrumCollection(self)
        lantanide.addWidget(w)

        self.setEnabled(False)  # disabled until load() is called
        style_checkboxes(self)

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface


    def set_splist(self, x):
        assert isinstance(x, SpectrumList)
        self.splist = x
        self.setEnabled(True)

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def on_run(self):
        try:
            expr = str(self.edit_expr.text())
            s_group_by = str(self.edit_group_by.text())
            group_by = [str(y).upper() for y in [x.strip() for x in s_group_by.split(",")] if len(y) > 0]
            other, errors = self.splist.query_merge_down(expr, group_by)

            if errors:
                S = "\n  - "
                show_error("Running query returned the following errors:"+S+S.join(errors))
            else:
                self.wsptable.set_collection(other)
                # f = self.keep_ref(FileSpectrumList())
                # f.splist = other
                # form = self.keep_ref(XFileSpectrumList())
                # form.load(f)
                # form.show()

        except Exception as E:
            msg = "Error running query: %s" % str_exc(E)
            self.add_log_error(msg, True)
            raise




    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear

