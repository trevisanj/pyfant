__all__ = ["XHelpDialog"]



from PyQt4.QtCore import *
from PyQt4.QtGui import *
from .basewindows import *
from ...constants import *

class XHelpDialog(XLogDialog):
    """
    Dialog with two areas: Fields Area and Help Area

    1. The Fields area contains a grid layout and the OK & Cancel buttons
    2. The Help Area contains a combo box and a text area

    Relevant properties:
      self.grid -- grid layout (initially empty)
      self.labelHelpTopics -- label with text "Help Topics", exposed in case you want to change this text
      self.comboBox -- combo box to add the help topics
    """

    def __init__(self, *args):
        XLogDialog.__init__(self, *args)


        def keep_ref(obj):
            self._refs.append(obj)
            return obj


        # # Central layout
        lymain = self.centralLayout = QVBoxLayout()
        lymain.setMargin(0)
        self.setLayout(lymain)

        # ## Title of Fields Area
        label = keep_ref(QLabel("<b>Setup</b>"))
        lymain.addWidget(label)

        # ## Fields Area
        lyfields = QHBoxLayout()
        lyfields.setMargin(0)
        lyfields.setSpacing(2)

        # ### Left area of Fields Area
        self.grid = QGridLayout()

        # ### Right area of Fields Area (button box)
        bb = keep_ref(QDialogButtonBox())
        bb.setOrientation(Qt.Vertical)
        bb.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        lyfields.addWidget(bb)
        bb.rejected.connect(self.reject)
        bb.accepted.connect(self.accept)

        # ## Title of Help Area
        label = keep_ref(QLabel("<b>Help</b>"))
        lymain.addWidget(label)

        # ## Help Area

        # ### Panel containing a combobox to choose among help topics
        ly = QHBoxLayout()
        lymain.addLayout(ly)
        ly.setMargin(0)
        ly.setSpacing(2)

        label = self.labelHelpTopics = QLabel("Help Topics")
        ly.addWidget(self.labelHelpTopics)

        cb = self.comboBox = QComboBox()
        ly.addWidget(cb)
        label.setBuddy(cb)

        x = self.textEdit = QTextEdit()
        x.setReadOnly(True)
        x.setStyleSheet("QTextEdit {color: %s}" % COLOR_DESCR)
        lymain.addWidget(x)
