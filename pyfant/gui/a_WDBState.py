from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from a99 import WDBRegistry
import a99
import pyfant

__all__ = ["WDBState"]


# Field names to leave out of table widget
_FIELDNAMES_OUT = ("id_molecule",)


class WDBState(WDBRegistry):
    """Registry for table 'state'"""

    def __init__(self, *args):
        WDBRegistry.__init__(self, *args)

        self._id_molecule = None

        # Adds button to download NIST data
        action = self.action_download = QAction(a99.get_icon("alien"), "&Download from NIST", self)
        action.triggered.connect(self._on_download)
        self.toolbar.addAction(action)


    def set_id_molecule(self, id_):
        """Sets molecule id and re-populates table"""
        self._id_molecule = id_
        self._populate()
        self._move_to_first()

    def find_formula(self, formula):
        """Moves to row where formula is (if found, otherwise does nothing)"""
        for i, row in enumerate(self._data):
            if row["formula"] == formula:
                self.tableWidget.setCurrentCell(i, 0)
                break

    def _on_download(self):
        if self._id_molecule is None:
            return

        formula = self._f.get_conn().execute("select formula from molecule where id = ?",
                                             (self._id_molecule,)).fetchone()["formula"]

        n = len(self._data)
        beware = "" if n == 0 else \
            "\n\n**Attention**: {} existing state{} for this molecule will be deleted!".\
                format(n, "" if n == 1 else "s")

        msg = "Molecular constants for '{}' will be downloaded " \
              "from NIST chemistry web book{}\n\nDo you wish to continue?".format(formula, beware)

        r = QMessageBox.question(self, "Download NIST data", msg,
                                 QMessageBox.Yes | QMessageBox.No,
                                 QMessageBox.Yes if n == 0 else QMessageBox.No)

        if r == QMessageBox.Yes:
            try:
                nist_data, _, _ = pyfant.get_nist_webbook_constants(formula, flag_parse_state=True)
            except Exception as e:
                self.add_log_error("Error getting NIST data (see log for more info)", True, e)
            else:
                pyfant.insert_states_from_nist(self._f, self._id_molecule, nist_data, flag_replace=True)
                self._populate()
                n = len(self._data)
                self.add_log("{} state{} successfully downloaded from NIST".
                             format(n, "" if n == 1 else "s"), True)

    def _populate(self, restore_mode=None):
        """
        Populates table widget

        Args:
            restore_mode: how to reposition cursor:
                - "index": tries to restore same row index
                - anything else: does not re-position
        """

        if self._f is None:
            return

        self._flag_populating = True
        try:
            curr_idx = self.tableWidget.currentRow()

            t = self.tableWidget
            rows = a99.cursor_to_rows(self._f.query_state(id_molecule=self._id_molecule))
            ti = self._f.get_table_info("state")
            fieldnames = [name for name in ti if name not in _FIELDNAMES_OUT]
            # unfortunately QTableWidget is not prepared to show HTML col_names = [row["caption"] or row["name"] for row in ti if not row["name"] in FIELDNAMES_OUT]
            col_names = fieldnames
            nr, nc = len(rows), len(fieldnames)

            a99.reset_table_widget(t, nr, nc)
            t.setHorizontalHeaderLabels(col_names)

            if nr > 0:
                for i, row in enumerate(rows):
                    for j, fieldname in enumerate(fieldnames):
                        cell = row[fieldname]
                        item = QTableWidgetItem("" if cell is None else str(cell))
                        t.setItem(i, j, item)
            t.resizeColumnsToContents()
            self._data = rows

            if restore_mode == "index":
                if -1 < curr_idx < t.rowCount():
                    t.setCurrentCell(curr_idx, 0)
        finally:
            self._flag_populating = False
            self._wanna_emit_id_changed()

    def _get_edit_params(self):
        """Returns a Parameters object containing information about the fields that may be edited"""
        ti = self._f.get_table_info("state")
        params = a99.table_info_to_parameters(ti)
        params = [p for p in params if not p.name.startswith("id")]
        return params

    def _get_edit_field_names(self):
        """Returns a list with the names of the fields that may be edited"""
        params = self._get_edit_params()
        ret = [p.name for p in params]
        return ret

    def _do_on_insert(self):
        params = self._get_edit_params()
        form = a99.XParametersEditor(specs=params, title="Insert Molecular State")
        r = form.exec_()
        if r == QDialog.Accepted:
            kwargs = form.get_kwargs()
            conn = self._f.get_conn()
            s = "insert into state (id_molecule, {}) values ({}, {})".\
                format(", ".join([p.name for p in params]),
                       self._id_molecule,
                       ", ".join(["?"]*len(params)))
            cursor = conn.execute(s, list(kwargs.values()))
            id_ = cursor.lastrowid
            conn.commit()
            self._populate(False)
            self._find_id(id_)
            return True

    def _do_on_edit(self):
        r, form = a99.show_edit_form(self.row, self._get_edit_field_names(), "Edit Molecular State")
        if r == QDialog.Accepted:
            kwargs = form.get_kwargs()
            id_ = self.row["id"]
            s = "update state set {} where id = {}".format(
                ", ".join(["{} = '{}'".format(a, b) for a, b in kwargs.items()]), id_)
            conn = self._f.get_conn()
            conn.execute(s)
            conn.commit()
            self._populate()
            self._find_id(id_)
            return True

    def _do_on_delete(self):
        r = QMessageBox.question(None, "Delete Molecular State",
                                 "Are you sure?",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r == QMessageBox.Yes:
            conn = self._f.get_conn()
            id_ = self.row["id"]
            conn.execute("delete from state where id = ?", [id_])
            conn.commit()
            self._populate("index")
            return True
