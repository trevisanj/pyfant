# ABANDONED, CRASHING FORM ON PLOT, decided to obtain histogram programatically only

# __all__ = ["XFileMoleculeHistogram"]
#
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *
# from PyQt5.QtWidgets import *
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT # as NavigationToolbar2QT
# import matplotlib.pyplot as plt
# from ._shared import *
# import a99
#
#
# MAX_NUM_BINS = 500
#
# class XFileMoleculeHistogram(QMainWindow):
#     """
#     Interactive window that plots a histogram of selected field of a FileAtoms
#     object.
#
#     Args:
#       mol: pyfant.Molecule
#     """
#
#     def __init__(self, mol):
#         import pyfant
#
#         QMainWindow.__init__(self)
#
#         # self.setWindowModality(Qt.ApplicationModal)
#
#         assert isinstance(mol, pyfant.Molecule)
#         self.mol = mol
#
#         # # Central widget containing toolbar and plot area
#
#         # ## Toolbar
#
#         l = self.labelDataField = QLabel("&Data field")
#         c = self.comboBoxDataField = QComboBox()
#         c.addItems(["lmbdam", "sj", "jj"])
#         l.setBuddy(c)
#         l2 = self.labelSpinBox = QLabel("&Bins")
#         sb = self.spinBox = QSpinBox()
#         sb.setMaximum(MAX_NUM_BINS)
#         sb.setValue(50)
#         l2.setBuddy(sb)
#         b = self.puishButtonPlot = QPushButton("&Plot")
#         b.clicked.connect(self.on_plot)
#
#         s = self.spacer0 = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
#
#         bb = [l, c, l2, sb, b]
#
#         l0 = self.layoutToolbar = QHBoxLayout()
#         for b in bb:
#             l0.addWidget(b)
#         l0.addItem(s)
#         a = self.widgetPlotToolbar = QWidget()
#         a.setLayout(l0)
#         a.setFixedHeight(40)
#
#         # ## Plot widget
#         # http://stackoverflow.com/questions/12459811
#         self.figure = plt.figure()
#         self.canvas = FigureCanvas(self.figure)
#         self.toolbar = NavigationToolbar2QT(self.canvas, self)
#         l1 = self.layoutPlot = QVBoxLayout()
#         l1.addWidget(self.toolbar)
#         l1.addWidget(self.canvas)
#         a99.set_margin(l1, 0)
#         # a = self.widgetPlot = QWidget()
#         # a.setLayout(l1)
#
#         # ## Mounts central widget
#         l2 = self.layoutCentral = QVBoxLayout()
#         l2.addWidget(self.widgetPlotToolbar)
#         l2.addLayout(l1)
#         # l2.addWidget(self.widgetPlot)
#         a99.set_margin(l2, 0)
#         a = self.centralWidget = QWidget()
#         a.setLayout(l2)
#         a.setFont(a99.MONO_FONT)
#         self.setCentralWidget(self.centralWidget)
#
#         # # Final adjustments
#         self.setWindowTitle("Histogram")
#         a99.place_center(self)
#
#
#     # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
#     # Slots
#
#     def on_plot(self, _):
#         self._plot()
#
#     # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
#     # Gear
#
#     def _plot(self):
#         attr_name = str(self.comboBoxDataField.currentText())
#         num_bins = int(self.spinBox.value())
#         v = self.mol.__getattribute__(attr_name)
#
#         self.figure.clear()
#         plt.figure(self.figure)
#         ax = self.figure.add_subplot(111)
#         ax.hist(v, num_bins)
#         ax.set_xlabel(attr_name)
#         ax.set_ylabel("counts")
#         plt.tight_layout()
#         a99.format_BLB()
#         self.canvas.draw()
