"""Widget to edit a FileMain object."""

__all__ = ["WFileMolConsts"]

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
from .a_WMolecularConstants import *
import pyfant


class WFileMolConsts(a99.WEditor):
    """FileMolConsts editor widget."""

    @property
    def fcfs(self):
        if self.w_molconsts is None:
            return None
        return self.w_molconsts.fcfs

    def __init__(self, *args, **kwargs):
        a99.WEditor.__init__(self, *args, **kwargs)

        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False

        # # Central layout
        l = self.layout_editor

        l.addLayout(self.keep_ref(self._get_layout_fn_moldb()))

        w = self.w_molconsts = WMolecularConstants(self.parent_form)
        w.changed.connect(self._on_w_molconsts_changed)
        l.addWidget(w)

        # ## Adds vertically expanding spacer at bottom
        l.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setEnabled(False)  # disabled until load() is called
        self.flag_process_changes = True

    def _get_layout_fn_moldb(self):
        help = "This is a file such as '{}', containing a list of diatomic molecules, their electronic systems, and constants for each electronic state.\n\n" \
               "To create a new such file, or make a copy of PyFANT default one in your local directory, run `moldbed.py` first.".format(pyfant.FileMolDB.default_filename)
        l = QHBoxLayout()
        a = self.keep_ref(QLabel("Molecular constants database file"))
        w = self.w_fn_moldb = a99.WSelectFile(self.parent_form)
        w.setToolTip(help)
        a.setBuddy(w)
        w.changed.connect(self._on_fn_moldb_changed)
        l.addWidget(a)
        l.addWidget(w)
        l.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        return l

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    # def set_moldb(self, fobj):
    #     self.w_molconsts.set_moldb(fobj)

    def _do_load(self, fobj):
        assert isinstance(fobj, pyfant.FileMolConsts)
        self._f = fobj
        self.w_fn_moldb.value = fobj.fn_moldb
        self._do_load_moldb()
        self.w_molconsts.molconsts = fobj.molconsts
        # The only thing that can go wrong (GUI bein invalid-wise) is the moldb filename missing
        self._flag_valid = self.w_fn_moldb.flag_valid

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        """Sets focus to first field. Note: reason is ignored."""
        self.w_molconsts.setFocus()


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def _on_w_molconsts_changed(self):
        if self.flag_process_changes:
            self._flag_valid = self.w_molconsts.flag_valid
            self.changed.emit()

    def _on_fn_moldb_changed(self):
        self._f.fn_moldb = self.w_fn_moldb.value
        self._do_load_moldb()
        self.changed.emit()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internals


    def _do_load_moldb(self):
        """Loads FileMolDB and updates part of GUI accordingly.

        This is an intermediate GUI updating stage."""
        moldb, flag_valid = pyfant.FileMolDB(), False
        fn_moldb = self.w_fn_moldb.value
        try:
            moldb.load(fn_moldb)
            flag_valid = True
        except Exception as e:
            self.add_log_error("Error loading file '{}'".format(fn_moldb), True, e)
        self.w_fn_moldb.flag_valid = flag_valid
        self.w_molconsts.set_moldb(moldb if flag_valid else None)