from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
import pyfant
import f311

__all__ = ["XFileMolConsts"]


class XFileMolConsts(f311.XFileMainWindowBase):
    def __init__(self, *args, moldb=None, **kwargs):
        f311.XFileMainWindowBase.__init__(self, *args, **kwargs)
        if moldb is not None:
            self.me.set_moldb(moldb)

    def set_moldb(self, moldb):
        self.me.set_moldb(moldb)

    def _add_stuff(self):
        me = self.me = pyfant.WFileMolConsts(self)
        self.tabWidget.addTab(me, "")

        _VVV = pyfant.FileMolConsts.description
        self.pages.append(f311.MyPage(
         text_tab="{}".format(_VVV),
         text_saveas="Save %s as..." % _VVV,
         text_load="Load %s" % _VVV,
         cls_save=pyfant.FileMolConsts, clss_load=(pyfant.FileMolConsts,), wild="*.py",
         editor=me
        ))

        self.setWindowTitle("Molecular constants editor")

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


    # # # Override
    # #   ========
    #
    # def _on_me_changed(self):
    #     """Overriden to commit automatically. "(changed)" will not appear
    #
    #     Changes should be committed by the method that executed queries, but it is so easy to
    #     reinforce this... just in case.
    #     """
    #     index = self._get_tab_index()
    #     if index == 0:
    #         self.me.f.get_conn().commit()  # Just in case
    #     else:
    #         self.flags_changed[index] = True
    #         self._update_tab_texts()
