__all__ = ["XFileOptions"]

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os.path
import a99
import f311
import pyfant


class XFileOptions(f311.XFileMainWindow):
    """Window to edit a FileOptions"""
    def _add_stuff(self):
        e0 = self.w = pyfant.WOptionsEditor(self)
        e0.changed.connect(self._on_w_changed)
        e0.loaded.connect(self._on_w_loaded)
        self.tabWidget.addTab(e0, "")
        # self.setCentralWidget(self.w)

        CLS_FILE = pyfant.FileOptions
        WILD = "*.py" if CLS_FILE.default_filename is None else "*"+os.path.splitext(CLS_FILE.default_filename)[1]
        self.pages.append(f311.MyPage(text_tab="File",
                                    cls_save=CLS_FILE, clss_load=(CLS_FILE,), wild=WILD, editor=e0))
        self.setWindowTitle("{} Editor".format(a99.get_obj_doc0(CLS_FILE)))

    def _on_w_loaded(self):
        pass

    def _on_w_changed(self):
        pass
