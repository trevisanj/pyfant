__all__ = ["XUseSpectrumBlock"]


from PyQt4.QtGui import *
from pyfant.gui import *
from pyfant import blocks, collect_doc, module_to_dict
from .a_XHelpDialog import *


class XUseSpectrumBlock(XHelpDialog):
    """
    Edit Parameters to apply a SpectrumBlock to each spectrum in a Spectrum List

    Relevant attributes (set on close):
      self.block -- None or SpectrumBlock instance
    """

    def __init__(self, *args):
        XHelpDialog.__init__(self, *args)

        self.block = None

        self.setWindowTitle("Transform")

        self.labelHelpTopics.setText("&Available operations")

        self.help_data = collect_doc(blocks.sb, base_class=blocks.base.SpectrumBlock)
        self.comboBox.addItems([x[0] for x in self.help_data])
        ###
        label = QLabel(enc_name_descr("O&peration", "See help below"))
        edit = self.editFunction = QLineEdit("Cut(3000, 7000)")
        label.setBuddy(edit)
        self.grid.addWidget(label, 0, 0)
        self.grid.addWidget(edit, 0, 1)

        place_center(self, 800, 600)


    def accept(self):
        try:
            expr = str(self.editFunction.text())
            block = eval(expr.strip(), {}, module_to_dict(blocks.sb))

            if not isinstance(block, blocks.base.SpectrumBlock):
                raise RuntimeError("Expression does not evaluate to a valid Spectrum Block")

            self.block = block

            return QDialog.accept(self)
        except Exception as e:
            self.add_log_error(str_exc(e), True)
            return False