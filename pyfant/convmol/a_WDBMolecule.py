from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pyfant as pf
import moldb as db
from collections import OrderedDict
from a_WRegistry import WRegistry
from pyfant.gui import guiaux


class WDBMolecule(WRegistry):
    """Registry for table 'molecule'"""


    def __init__(self, *args):
        WRegistry.__init__(self, *args)


    def _find_formula(self, formula):
        """Moves to row where formula is (if found, otherwise does nothing)"""
        for i, row in enumerate(self._data):
            if row["formula"] == formula:
                self.tableWidget.setCurrentCell(i, 0)
                break


    def _populate(self, restore_mode=None):
        """
        Populates table widget

        Args:
            restore_mode: how to reposition cursor:
                "formula": tries to re-position at same formula as before
                "index": tries to restore same row index
                anything else: does not re-position
        """
        self._flag_populating = True
        try:
            curr_idx = self.tableWidget.currentRow()
            curr_row = self.row

            t = self.tableWidget
            fieldnames = [row["name"] for row in db.get_table_info("molecule")]
            # fieldnames = ["id", "formula", "name"]
            rows = db.cursor_to_rows(db.query_molecules())
            nr, nc = len(rows), len(fieldnames)
            pf.gui.ResetTableWidget(t, nr, nc)
            t.setHorizontalHeaderLabels(fieldnames)
            if nr > 0:
                for i, row in enumerate(rows):
                    for j, fieldname in enumerate(fieldnames):
                        cell = row[fieldname]
                        item = QTableWidgetItem("" if cell is None else str(cell))
                        t.setItem(i, j, item)
            t.resizeColumnsToContents()
            self._data = rows

            if restore_mode == "formula":
                if curr_row:
                    self._find_formula(curr_row["formula"])
            elif restore_mode == "index":
                if -1 < curr_idx < t.rowCount():
                    t.setCurrentCell(curr_idx, 0)
        finally:
            self._flag_populating = False
            self._wanna_emit_id_changed()


    def _get_edit_params(self):
        """Returns a Parameters object containing information about the fields that may be edited"""
        ti = db.get_table_info("molecule")
        params = guiaux.table_info_to_parameters(ti)
        params = [p for p in params if not p.name.startswith("id")]
        return params


    def _get_edit_field_names(self):
        """Returns a list with the names of the fields that may be edited"""
        params = self._get_edit_params()
        ret = [p.name for p in params]
        return ret


    def _do_on_insert(self):
        params = self._get_edit_params()
        form = pf.gui.XParametersEditor(specs=params, title="Insert molecule")
        r = form.exec_()
        if r == QDialog.Accepted:
            kwargs = form.get_kwargs()
            conn = db.get_conn()
            s = "insert into molecule({}) values ({})".format(", ".join([p.name for p in params]),
                                                              ", ".join(["?"*len(params)]))
            conn.execute(s, list(kwargs.values()))
            conn.commit()
            self._populate(False)
            self._find_formula(kwargs["formula"])


    def _do_on_edit(self):
        r, form = pf.gui.show_edit_form(self.row, self._get_edit_field_names(), "Edit molecule")
        if r == QDialog.Accepted:
            kwargs = form.get_kwargs()
            s = "update molecule set {} where id = {}".format(
                ", ".join(["{} = '{}'".format(a, b) for a, b in kwargs.items()]), self.row["id"])
            conn = db.get_conn()
            conn.execute(s)
            conn.commit()
            self._populate()
            self._find_formula(kwargs["formula"])


    def _do_on_delete(self):
        r = QMessageBox.question(None, "Delete molecule",
                                 "This will also delete all States associated to this molecule!\n\nAre you sure?",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r == QMessageBox.Yes:
            conn = db.get_conn()
            id_ = self.row["id"]
            conn.execute("delete from molecule where id = ?", [id_])
            conn.execute("delete from state where id_molecule = ?", [id_])
            conn.commit()

            self._populate("index")