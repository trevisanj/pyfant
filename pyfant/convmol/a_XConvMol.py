from PyQt4.QtCore import *
from PyQt4.QtGui import *
import astroapi as aa
# import pyfant as pf
# from a_WState import WState
# import moldb as db
from . import WStateConst, WMolConst



class _DataSource(aa.AttrsPart):
    """Represents a data source for molecular lines"""

    def __init__(self, name):
        aa.AttrsPart.__init__(self)
        self.name = name

    def __repr__(self):
        return "{}('{}')".format(self.__class__.__name__, self.name)


_SOURCES = [_DataSource("HITRAN"),
            _DataSource("TurboSpectrum"),
            _DataSource("Kurucz")]


class _WSource(aa.WBase):
    """Lists sources for molecular lines data"""


    @property
    def index(self):
        return self._get_index()

    @property
    def source(self):
        """Returns _DataSource object or None"""
        i = self._get_index()
        if i < 0:
            return None
        return _SOURCES[i]

    index_changed = pyqtSignal()

    def __init__(self, *args):
        aa.WBase.__init__(self, *args)

        self._buttons = []
        self._last_index = -1

        lw = QVBoxLayout()
        self.setLayout(lw)

        for ds in _SOURCES:
            b = self.keep_ref(QRadioButton(ds.name))
            b.clicked.connect(self._button_clicked)
            self._buttons.append(b)
            lw.addWidget(b)

    def _button_clicked(self):
        i = self._get_index()
        if i != self._last_index:
            self._last_index = i
            self.index_changed.emit()


    def _get_index(self):
        for i, b in enumerate(self._buttons):
            assert isinstance(b, QRadioButton)
            if b.isChecked():
                return i
        return -1


class _WHitranPanel(aa.WBase):
    def __init__(self, *args):
        aa.WBase.__init__(self, *args)

        lw = QVBoxLayout()
        self.setLayout(lw)

        for ds in _SOURCES:
            b = self.keep_ref(QRadioButton(ds.name))
            b.clicked.connect(self._button_clicked)
            self._buttons.append(b)
            lw.addWidget(b)


class XConvMol(aa.XLogMainWindow):
    def __init__(self, *args):
        aa.XLogMainWindow.__init__(self, *args)

        tw = self.keep_ref(QTabWidget())
        self.setCentralWidget(tw)

        # # First tab: polluted!!

        sp = self.keep_ref(QSplitter(Qt.Vertical))
        tw.addTab(sp, "Molecular constants (Alt+&1)")

        # ## First widget of splitter
        w0 = self.keep_ref(QWidget())
        l0 = QVBoxLayout(w0)
        l0.setMargin(2)
        l0.setSpacing(2)

        a = self.title_mol = QLabel(aa.format_title0("Select a molecule:"))
        l0.addWidget(a)

        w = self.w_mol = WMolConst(self)
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

        w = self.w_state = WStateConst(self)
        w.layout().setContentsMargins(15, 1, 1, 1)
        l1.addWidget(w)

        sp.addWidget(w0)
        sp.addWidget(w1)


        # # Second tab: files

        w = self.keep_ref(QWidget())
        tw.addTab(w, "Conversion (Alt+&2)")


        # ## Vertical layout: source and destination stacked
        lsd = self.keep_ref(QVBoxLayout(w))

        # ### Horizontal layout: sources radio buttons, source-specific setup area

        # #### Vertical layout: source radio group box

        lss = QVBoxLayout()
        lsd.addLayout(lss)

        lss.addWidget(self.keep_ref(QLabel("<b>Source</b>")))
        w = self.w_source = _WSource(self)
        w.index_changed.connect(self.source_changed)
        lss.addWidget(w)
        lss.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # ## Testing my new select widgets

        w0 = self.keep_ref(aa.WSelectFile(self))
        lss.addWidget(w0)

        w1 = self.keep_ref(aa.WSelectDir(self))
        lss.addWidget(w1)

        aa.nerdify(self)

    def source_changed(self):
        print("SOURCE IS NOW ", _SOURCES[self.w_source.index])

    def mol_id_changed(self):
        id_ = self.w_mol.w_mol.id
        row = self.w_mol.w_mol.row
        self.w_state.set_id_molecule(id_)
        s = "States (no molecule selected)" if not row else "Select a State for molecule '{}'".format(row["formula"])
        self.title_state.setText(aa.format_title0(s))

    def get_all_consts(self):
        ret = self.w_mol.get_all_consts()
        ret.update(self.w_state.get_all_consts())
        return ret

    def fn_in_clicked(self):
        try:
            # d = self.sp.filename if self.sp and self.sp.filename is not None else FileSpectrumPfant.default_filename
            d = "./aababababababababa.hitran.aparanego"
            new_filename = QFileDialog.getOpenFileName(self, "Input filename", d, "*.*")
            if new_filename:
                print("MAKING PROGRESS")

        except Exception as e:
            self.add_log_error(str(e), True)
            raise
