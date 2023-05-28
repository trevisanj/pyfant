from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from a99 import WDBRegistry
import a99
from .a_WDBFCF import *
from .a_WDBPFANTMol import *
from .a_WDBSystem import *

__all__ = ["WDBSystemPFANTMolFCF"]


class WDBSystemPFANTMolFCF(a99.WBase):
    """Master-slave widget to lodge System and FCF widgets"""

    # Emitted whenever the value of the 'id' property changes
    id_changed = pyqtSignal()

    @property
    def id(self):
        """System id or None"""
        return self.w_system._get_id()

    @property
    def f(self):
        """Object representing the file being edited (possibly a DataFile object)"""
        return self._f

    @f.setter
    def f(self, f):
        self.w_system.f = f
        self.w_fcf.f = f
        self.w_pfantmol.f = f

    def __init__(self, *args):
        a99.WBase.__init__(self, *args)

        # # Main layout & splitter
        lmain = self.keep_ref(QVBoxLayout(self))
        sp = self.keep_ref(QSplitter(Qt.Horizontal))


        # ## First widget of splitter
        w0 = self.keep_ref(QWidget())
        l0 = QVBoxLayout(w0)
        a99.set_margin(l0, 0)
        l0.setSpacing(2)

        a = self.title_mol = QLabel(a99.format_title1("Systems"))
        l0.addWidget(a)

        # ### label and edit with copiable system description
        a = self.label_sysdescr = QLabel("System descriptio&n:")
        b = self.lineedit_sysdescr = QLineEdit()
        b.setReadOnly(True)
        b.setFixedWidth(200)
        a.setBuddy(b)

        l = self.layout_sysdescr = QHBoxLayout()
        l.addWidget(a)
        l.addWidget(b)
        l.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        l0.addLayout(l)

        # ### Systems registry table
        w = self.w_system = WDBSystem(self.parent_form)
        w.id_changed.connect(self.id_system_changed)
        w.id_changed.connect(self.id_changed)
        w.changed.connect(self.changed)
        l0.addWidget(w)

        # ## Second widget of splitter
        sp1 = self.keep_ref(QSplitter(Qt.Vertical))

        # ### widget 1.1

        w10 = self.keep_ref(QWidget())
        l10 = QVBoxLayout(w10)
        a99.set_margin(l10, 0)
        l10.setSpacing(2)

        a = self.title_state = self.keep_ref(QLabel(a99.format_title1("PFANT molecules")))
        l10.addWidget(a)

        w = self.w_pfantmol = WDBPFANTMol(self.parent_form)
        w.changed.connect(self.changed)
        l10.addWidget(w)

        # ### widget 1.1

        w11 = self.keep_ref(QWidget())
        l11 = QVBoxLayout(w11)
        a99.set_margin(l11, 0)
        l11.setSpacing(2)

        a = self.title_state = self.keep_ref(QLabel(a99.format_title1("Franck-Condon Factors")))
        l11.addWidget(a)

        w = self.w_fcf = WDBFCF(self.parent_form)
        w.changed.connect(self.changed)
        l11.addWidget(w)


        # ## Adds widgets to splitters

        sp1.addWidget(w10)
        sp1.addWidget(w11)

        sp.addWidget(w0)
        sp.addWidget(sp1)

        lmain.addWidget(sp)

        # # Final adjustments
        a99.nerdify(self)

        self.w_system._move_to_first()


    def set_id_molecule(self, id_):
        """Propagates to self.w_system"""
        self.w_system.set_id_molecule(id_)
        # self._populate()

    def id_system_changed(self):
        import pyfant
        self.w_pfantmol.set_id_system(self.w_system.id)
        self.w_fcf.set_id_system(self.w_system.id)

        row = self.w_system.row
        descr = pyfant.molconsts_to_system_str(row, pyfant.SS_PLAIN) if row else ""

        wfilemoldb = self.parent().parent().parent().parent()
        molrow = wfilemoldb.w_mol.row

        descr_ = "" if not molrow else f"{molrow['formula']} [{descr}]"

        self.lineedit_sysdescr.setText(descr_)

