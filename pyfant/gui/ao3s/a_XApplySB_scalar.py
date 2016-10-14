__all__ = ["XApplySB_scalar"]


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pyfant.gui import *
from pyfant import *
import numpy as np
from .basewindows import *
from .a_XHelpDialog import *


_CLASS_PREFIX = "SB_scalar_"

class XApplySB_scalar(XHelpDialog):
    """
    Edit Parameters to apply SB_scalar blocks to a Spectrum List

    Relevant attributes:
      self.block -- None or SB_scalar instance, set before closing when one clicks on "OK"
      self.fieldname -- string
    """

    def __init__(self, *args):
        XHelpDialog.__init__(self, *args)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        self.block = None

        self.setWindowTitle("Extract Scalar")

        self.labelHelpTopics.setText("Functions available")

        self.help_data = collect_doc(blocks.sblocks, prefix=_CLASS_PREFIX, flag_exclude_prefix=True)
        self.comboBox.addItems([x[0] for x in self.help_data])
        ###
        label = QLabel(enc_name_descr("&Function", "See help below"))
        edit = self.editFunction = QLineEdit("SNR(0, 10000)")
        label.setBuddy(edit)
        self.grid.addWidget(label, 0, 0)
        self.grid.addWidget(edit, 0, 1)
        ###
        label = keep_ref(QLabel(enc_name_descr("&Target Field Name", "Leave blank to use Function Name")))
        edit = self.editFieldName = QLineEdit("")
        label.setBuddy(edit)
        self.grid.addWidget(label, 1, 0)
        self.grid.addWidget(edit, 1, 1)

        place_center(self, 800, 600)


    def accept(self):
        try:
            from pyfant.blocks.sblocks import *
            expr = str(self.editFunction.text())
            block = eval("SB_scalar_"+expr.strip())

            if not isinstance(block, SB_scalar):
                raise RuntimeError("Expression does not evaluate to a valid Scalar Block")

            self.block = block
            fieldname = str(self.editFieldName.text()).strip()
            self.fieldname = expr[:expr.index("(")].strip() if len(fieldname) == 0 else fieldname

            return 1
        except Exception as e:
            self.add_log_error(str_exc(e), True)
            return 0