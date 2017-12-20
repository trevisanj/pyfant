from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from a99 import WDBRegistry
import a99
import pyfant
from .a_WDBSystem import *

__all__ = ["WDBFCF"]


# Field names to leave out of table widget
_FIELDNAMES_OUT = ("id", "id_system",)

# TRAPRB input parameters to be edited before TRAPRB is run
_TRAPRB_ATTRS = ["rmin", "rmax", "delr", "maxv"]

class WDBFCF(WDBRegistry):
    """Registry for table 'fcf'"""

    def __init__(self, *args):
        WDBRegistry.__init__(self, *args)

        self._id_system = None

        # Adds button to download NIST data
        action = self.action_download = QAction(a99.get_icon("alien"),
            "Run &TRAPRB to get Franck-Condon Factors...\n\n"
            "For more information on TRAPRB input variables, visit URL:\n\n"
            "https://github.com/trevisanj/pyfant/blob/master/docs/art/traprb-input.pdf", self)
        # action.setToolTip("")
        action.triggered.connect(self._on_run_traprb)
        self.toolbar.addAction(action)

    def set_id_system(self, id_):
        """Sets molecule id and re-populates table"""
        self._id_system = id_
        self._populate()
        self._move_to_first()

    def _on_run_traprb(self):
        if self._id_system is None:
            return

        row = self._f.get_conn().execute("select * from system where id = ?",
                                         (self._id_system,)).fetchone()

        string = pyfant.molconsts_to_system_str(row, SYSTEMSTYLE)



        n = len(self._data)
        beware = "" if n == 0 else \
            "\n\n**Attention**: {} existing FCF{} for this system will be deleted!".\
                format(n, "" if n == 1 else "s")

        msg = "TRAPRB will be executed to calculate the Franck-Condon factors for system '{}'." \
              "{}\n\nDo you wish to continue?".format(string, beware)

        r = QMessageBox.question(self, "Calculate FCFs", msg,
                                 QMessageBox.Yes | QMessageBox.No,
                                 QMessageBox.Yes if n == 0 else QMessageBox.No)

        if r == QMessageBox.Yes:
            r, form = self._show_traprb_parameters_form(r)

            if r == QDialog.Accepted:
                kwargs = form.get_kwargs()

                mc = pyfant.MolConsts()

                try:
                    mc.populate_all_using_system_row(self._f, row)

                    # TODO maybe intermediate review stage, i.e., allow the user to see the FCFs before inserting

                    traprb = pyfant.run_traprb(mc, None, None, **kwargs)

                    traprb.load_result()
                    output = traprb.result["output"]

                    pyfant.insert_fcfs(self._f, self._id_system, output.fcfs, flag_replace=True)

                    self._populate()

                    n = len(output.fcfs)
                    self.add_log("{} FCF{} successfully inserted".
                                 format(n, "" if n == 1 else "s"), True)
                except Exception as e:
                    self.add_log_error("Error calculating FCFs: '{}'".format(a99.str_exc(e)),
                                       True, e)

    def _show_traprb_parameters_form(self, r):
        # **Note** creates TRAPRBInputState() instance to get default input parameter values

        r, form = a99.show_edit_form(
            pyfant.TRAPRBInputState(),
            attrs=_TRAPRB_ATTRS,
            title="Modify selected TRAPRB input parameters",
            toolTips=[
                "minimum radius for calculation of wavefunctions (0.75 in most cases; 0.6 for OH A-X)",
                "maximum radius for calculation of wavefunctions",
                "radial interval for calculation of wavefunctions",
                "maximum quantum number for calculation of results"],
        )
        return r, form

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
            rows = a99.cursor_to_rows(self._f.query_fcf(id_system=self._id_system))
            ti = self._f.get_table_info("fcf")
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
        ti = self._f.get_table_info("fcf")
        params = a99.table_info_to_parameters(ti)
        params = [p for p in params if not p.name.startswith("id")]
        return params

    def _get_edit_field_names(self):
        """Returns a list with the names of the fields that may be edited"""
        params = self._get_edit_params()
        ret = [p.name for p in params]
        return ret

    def _do_on_insert(self):
        if self._id_system is None:
            return
        params = self._get_edit_params()
        form = a99.XParametersEditor(specs=params, title="Insert Franck-Condon Factor")
        r = form.exec_()
        if r == QDialog.Accepted:
            kwargs = form.get_kwargs()
            conn = self._f.get_conn()
            s = "insert into fcf (id_system, {}) values ({}, {})".\
                format(", ".join([p.name for p in params]),
                       self._id_system,
                       ", ".join(["?"]*len(params)))
            cursor = conn.execute(s, list(kwargs.values()))
            id_ = cursor.lastrowid
            conn.commit()
            self._populate(False)
            self._find_id(id_)
            return True

    def _do_on_edit(self):
        r, form = a99.show_edit_form(self.row, self._get_edit_field_names(), "Edit Franck-Condon Factor")
        if r == QDialog.Accepted:
            kwargs = form.get_kwargs()
            id_ = self.row["id"]
            s = "update fcf set {} where id = {}".format(
                ", ".join(["{} = '{}'".format(a, b) for a, b in kwargs.items()]), id_)
            conn = self._f.get_conn()
            conn.execute(s)
            conn.commit()
            self._populate()
            self._find_id(id_)
            return True

    def _do_on_delete(self):
        r = QMessageBox.question(None, "Delete Franck-Condon Factor",
                                 "Are you sure?",
                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if r == QMessageBox.Yes:
            conn = self._f.get_conn()
            id_ = self.row["id"]
            conn.execute("delete from fcf where id = ?", [id_])
            conn.commit()

            self._populate("index")
            return True
