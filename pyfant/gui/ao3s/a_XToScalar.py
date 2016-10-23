__all__ = ["XToScalar"]


from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pyfant.gui import *
from pyfant import *
import numpy as np
from .basewindows import *
from .a_XHelpDialog import *


_CLASS_PREFIX = ""

class XToScalar(XHelpDialog):
    """
    Edit Parameters to apply ToScalar blocks to a Spectrum List

    Relevant attributes:
      self.block -- None or ToScalar instance, set before closing when one clicks on "OK"
      self.fieldname -- string
    """

    def __init__(self, *args):
        XHelpDialog.__init__(self, *args)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        self.block = None

        self.setWindowTitle("Extract Scalar")

        self.labelHelpTopics.setText("&Available operations")

        # self.help_data = collect_doc(blocks.sp2scalar, base_class=blocks.baseblocks.ToScalar)
        self.help_data = collect_doc(blocks.toscalar, base_class=blocks.base.ToScalar)
        self.comboBox.addItems([x[0] for x in self.help_data])
        ###
        label = QLabel(enc_name_descr("O&peration", "See help below"))
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
            # from pyfant.blocks.sp2scalar import *
            expr = str(self.editFunction.text())
            block = eval(expr.strip(), {}, module_to_dict(blocks.toscalar))

            if not isinstance(block, blocks.base.ToScalar):
                raise RuntimeError("Expression does not evaluate to a valid Scalar Block")

            self.block = block
            fieldname = str(self.editFieldName.text()).strip()
            fieldname = expr[:expr.index("(")].strip() if len(fieldname) == 0 else fieldname
            self.fieldname = valid_fits_key(fieldname)

            return QDialog.accept(self)
        except Exception as e:
            self.add_log_error(self.str_exc(e), True)
            return False