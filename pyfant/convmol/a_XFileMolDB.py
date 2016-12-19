from PyQt4.QtCore import *
from PyQt4.QtGui import *
import astroapi as aa
import pyfant as pf
# from a_WState import WState
# import moldb as db
from .a_WDBMolecule import WDBMolecule
from .a_WDBState import WDBState
from . import hapi
import os
import datetime


__all__ = ["XFileMolDB"]


class _WMolDB(aa.WBase):


    @property
    def f(self):
        return self._f

    # @f.setter
    # def f(self, x):
    #     self._f = x
    #     self.w_mol.f = x
    #     self.w_state.f = x

    def __init__(self, *args):
        aa.WBase.__init__(self, *args)

        self._f = None

        # # Main layout & splitter
        lmain = self.keep_ref(QVBoxLayout(self))
        sp = self.keep_ref(QSplitter(Qt.Vertical))


        # ## Line showing the File Name
        l1 = self.keep_ref(QHBoxLayout())
        lmain.addLayout(l1)
        l1.setMargin(0)
        l1.addWidget(self.keep_ref(QLabel("<b>File:<b>")))
        w = self.label_fn = QLabel()
        l1.addWidget(w)
        l1.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))


        # ## First widget of splitter
        w0 = self.keep_ref(QWidget())
        l0 = QVBoxLayout(w0)
        l0.setMargin(2)
        l0.setSpacing(2)

        a = self.title_mol = QLabel(aa.format_title0("Select a molecule:"))
        l0.addWidget(a)

        w = self.w_mol = WDBMolecule(self.parent_form)
        w.layout().setContentsMargins(15, 1, 1, 1)
        w.id_changed.connect(self.mol_id_changed)
        l0.addWidget(w)

        # ## Second widget of splitter
        w1 = self.keep_ref(QWidget())
        l1 = QVBoxLayout(w1)
        l1.setMargin(2)
        l1.setSpacing(2)

        a = self.title_state = self.keep_ref(QLabel(aa.format_title0("States")))
        l1.addWidget(a)

        w = self.w_state = WDBState(self.parent_form)
        w.layout().setContentsMargins(15, 1, 1, 1)
        l1.addWidget(w)

        sp.addWidget(w0)
        sp.addWidget(w1)
        lmain.addWidget(sp)

        # # Final adjustments
        aa.nerdify(self)

    def load(self, x):
        self._f = x
        self.w_mol.f = x
        self.w_state.f = x
        self.update_gui_label_fn()


    def mol_id_changed(self):
        id_ = self.w_mol.id
        row = self.w_mol.row
        self.w_state.set_id_molecule(id_)
        s = "States (no molecule selected)" if not row else "Select a State for molecule '{}'".format(
            row["formula"])
        self.title_state.setText(aa.format_title0(s))


    # # Override
    #   ========

    def update_gui_label_fn(self):
        if not self._f:
            text = "(not loaded)"
        elif self._f.filename:
            text = os.path.relpath(self._f.filename, ".")
        else:
            text = "(filename not set)"
        self.label_fn.setText(text)



class XFileMolDB(aa.XFileMainWindow):
    def __init__(self, parent=None, fileobj=None):
        aa.XFileMainWindow.__init__(self, parent)

        # # Synchronized sequences
        _VVV = pf.FileMolDB.description
        self.tab_texts[0] =  "{} (Alt+&1)".format(_VVV)
        self.tabWidget.setTabText(0, self.tab_texts[0])
        self.save_as_texts[0] = "Save %s as..." % _VVV
        self.open_texts[0] = "Load %s" % _VVV
        self.clss[0] = pf.FileMolDB
        self.clsss[0] = (pf.FileMolDB,)
        self.wilds[0] = "*.sqlite"


        lv = self.keep_ref(QVBoxLayout(self.gotting))
        me = self.moldb_editor = _WMolDB(self)
        lv.addWidget(me)
        me.edited.connect(self._on_edited)
        self.editors[0] = me


        if fileobj is not None:
            self.load(fileobj)

    def wants_auto(self):
        idx = self.w_source.index
        filename = None
        if idx == 0:
            lines = self.w_hitran.data
            if lines:
                filename = "{}.dat".format(lines["header"]["table_name"])

        if filename is None:
            # Default
            filename = aa.new_filename("mol", "dat")

        self.w_out.value = filename


    def on_fill_missing(self):
        self.w_mol.None_to_zero()
        self.w_state.None_to_zero()

    # def mol_id_changed(self):
    #     id_ = self.w_mol.w_mol.id
    #     row = self.w_mol.w_mol.row
    #     self.w_state.set_id_molecule(id_)
    #     s = "States (no molecule selected)" if not row else "Select a State for molecule '{}'".format(row["formula"])
    #     self.title_state.setText(aa.format_title0(s))


    # # Override
    #   ========

