__all__ = ["XGroupSpectra"]


from PyQt4.QtGui import *
from pyfant.gui import *
from pyfant import blocks, collect_doc, module_to_dict
from .a_XHelpDialog import *


class XGroupSpectra(XHelpDialog):
    """
    Edit Parameters group.py a SpectrumList

    Relevant attributes (set on close):
      self.block -- None or GroupBlock instance
      self.group_by -- sequence of
          (field names) = (FITS header keys) = (keys in Spectrum.more_headers)
    """

    def __init__(self, *args):
        XHelpDialog.__init__(self, *args)

        self.block = None
        self.group_by = None


        self.setWindowTitle("Group Spectra")

        self.labelHelpTopics.setText("Functions available")

        self.help_data = collect_doc(blocks.group, base_class=blocks.base.GroupBlock)
        self.comboBox.addItems([x[0] for x in self.help_data])
        ###
        label = QLabel(enc_name_descr("&Function", "See help below"))
        edit = self.editFunction = QLineEdit("UseNumPyFunc(np.mean)")
        label.setBuddy(edit)
        self.grid.addWidget(label, 0, 0)
        self.grid.addWidget(edit, 0, 1)
        ###
        label = QLabel(enc_name_descr("&Group fieldnames", "Comma-separated without quotes"))
        edit = self.editGroupBy = QLineEdit("")
        label.setBuddy(edit)
        self.grid.addWidget(label, 1, 0)
        self.grid.addWidget(edit, 1, 1)

        place_center(self, 800, 600)

    def accept(self):
        try:
            expr = str(self.editFunction.text())
            symbols_available = module_to_dict(blocks.group)
            import numpy
            symbols_available["np"] = numpy
            block = eval(expr.strip(), {}, symbols_available)

            if not isinstance(block, blocks.base.GroupBlock):
                raise RuntimeError("Expression does not evaluate to a valid Grouping Block")

            s_group_by = str(self.editGroupBy.text())
            group_by = [str(y).upper() for y in [x.strip() for x in s_group_by.split(",")] if len(y) > 0]

            self.block = block
            self.group_by = group_by

            return QDialog.accept(self)
        except Exception as e:
            self.add_log_error(self.str_exc(e), True)
            return False

