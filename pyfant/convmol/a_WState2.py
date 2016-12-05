# from PyQt4.QtCore import *
# from PyQt4.QtGui import *
# import pyfant as pf
#
#
# class WState(pf.gui.WBase):
#     """
#     Widget that lists molecule states for the user to select one
#     """
#
#     @property
#     def B_e(self):
#         return self._B_e
#
#     @B_e.setter
#     def B_e(self, x):
#         self._B_e = x
#
#     @property
#     def D_e(self):
#         return self._D_e
#
#     @D_e.setter
#     def D_e(self, x):
#         self._D_e = x
#
#     @property
#     def beta_e(self):
#         return self._beta_e
#
#     @beta_e.setter
#     def beta_e(self, x):
#         self._beta_e = x
#
#     @property
#     def omega_e(self):
#         return self._omega_e
#
#     @omega_e.setter
#     def omega_e(self, x):
#         self._omega_e = x
#
#     @property
#     def omega_ex_e(self):
#         return self._omega_ex_e
#
#     @omega_ex_e.setter
#     def omega_ex_e(self, x):
#         self._omega_ex_e = x
#
#     @property
#     def omega_ey_e(self):
#         return self._omega_ey_e
#
#     @omega_ey_e.setter
#     def omega_ey_e(self, x):
#         self._omega_ey_e = x
#
#     def __init__(self, *args):
#         pf.gui.WBase.__init__(self, *args)
#
#         self.flag_populating = False  # activated when populating table
#
#         # Data
#         self.data = []
#
#         # Molecular constants of interest
#         self._B_e = 0.
#         self._D_e = 0.
#         self._beta_e = 0.
#         self._omega_e = 0.
#         self._omega_ex_e = 0.
#         self._omega_ey_e = 0.
#
#         a = self.tableWidget = QTableWidget()
#         a.setSelectionMode(QAbstractItemView.SingleSelection)
#         a.setEditTriggers(QTableWidget.NoEditTriggers)
#         a.setFont(pf.gui.MONO_FONT)
#         a.currentCellChanged.connect(self.on_tableWidget_currentCellChanged)
#
#         l = QVBoxLayout(self)
#         l.setMargin(1)
#         l.addWidget(a)
#
#         f_map = self.f_map = [
#             ["B_e", self.B_e, None],
#             ["D_e", self.D_e, None],
#             ["beta_e", self.beta_e, None],
#             ["omega_e", self.omega_e, None],
#             ["omega_ex_e", self.omega_ex_e, None],
#             ["omega_ey_e", self.omega_ey_e, None],
#         ]
#
#         lh = QHBoxLayout()
#         l.addLayout(lh)
#         nr, nc, n = 2, 3, len(f_map)
#         for j in range(nc):
#             lv = QFormLayout()
#             lh.addLayout(lv)
#             ii = range(j, n, nc)
#             for i in range(nr):
#                 row = f_map[ii[i]]
#                 e = QLineEdit()
#                 row[2] = e
#                 lv.addRow(row[0], e)
#
#     def on_tableWidget_currentCellChanged(self, currentRow, currentColumn, previousRow,
#                                           previousColumn):
#         """Transfer values from self.data to edit fields below the table widget"""
#         row = self.data[currentRow]
#         for map_row in self.f_map:
#             value = self.data[currentRow][map_row[0]]
#             map_row[2].setText(str(value) if value is not None else "")
#
#     def set_data(self, rows):
#         """
#         Populates table widget excluding headers "formula" and "id_molecule"
#
#         Args:
#             data: list of lists
#             header: list containing headers
#
#         Returns:
#
#         """
#         self.flag_populating = True
#         try:
#             header, nr, nc = [], len(rows), 0
#             if nr > 0:
#                 header = list(rows[0].keys())
#                 to_leave_out = ("formula", "id_molecule")
#                 leave_out = []
#                 for name in to_leave_out:
#                     try:
#                         leave_out.append(header.index(name))
#                     except ValueError:
#                         pass
#                 nc = len(header) - len(leave_out)
#
#             t = self.tableWidget
#             pf.gui.ResetTableWidget(t, nr, nc)
#
#             if nr > 0:
#                 t.setHorizontalHeaderLabels([name for name in header if name not in to_leave_out])
#                 for i, row in enumerate(rows):
#                     j = 0
#                     for k, cell in enumerate(row.values()):
#                         if k in leave_out:
#                             continue
#                         item = QTableWidgetItem("" if cell is None else str(cell))
#                         t.setItem(i, j, item)
#                         j += 1
#
#             t.resizeColumnsToContents()
#
#             self.data = rows
#
#         finally:
#             self.flag_populating = False
#
