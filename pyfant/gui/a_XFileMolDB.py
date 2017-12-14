from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
import f311
import pyfant

__all__ = ["XFileMolDB"]


class XFileMolDB(f311.XFileMainWindow):
    def _add_stuff(self):

        me = self.w_moldb = pyfant.WFileMolDB(self)
        me.changed.connect(self._on_changed)

        # # Synchronized sequences
        self.pages.append(f311.MyPage(
         text_tab=pyfant.FileMolDB.description,
         cls_save=pyfant.FileMolDB, clss_load=(pyfant.FileMolDB,), wild="*.sqlite",
         editor=me, flag_autosave=True
        ))

        self.setWindowTitle("Molecular information database editor")

    def wants_auto(self):
        idx = self.w_source.index
        filename = None
        if idx == 0:
            lines = self.w_hitran.data
            if lines:
                filename = "{}.dat".format(lines["header"]["table_name"])

        if filename is None:
            # Default
            filename = a99.new_filename("mol", "dat")

        self.w_out.value = filename
