from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pyfant as pf
from a_WState import WState
import moldb as db


class WStateConst(pf.gui.WBase):
    """
    Widget for the user to select/modify state-specific constants. Has a embedded WDBState
    """

    @property
    def fieldnames(self):
        return self._fieldnames

    def __init__(self, *args):
        pf.gui.WBase.__init__(self, *args)

        self.flag_populating = False  # activated when populating table

        # # Internal state

        # Molecular constants of interest
        self._fieldnames = ["omega_e", "omega_ex_e", "omega_ey_e", "B_e", "alpha_e", "D_e", "beta_e",]

        # dictionary {(field name): (edit object), }
        # (will be populated later below together with edit widgets creation)
        self._edit_map = {}


        # # GUI design

        l = QVBoxLayout(self)
        l.setMargin(1)

        # ## State widget
        a = self.w_state = WState(self.parent_form)
        l.addWidget(a)
        a.id_changed.connect(self._w_state_id_changed)

        # ## Title label
        a = self.apa = self.keep_ref(QLabel("<h4>Values to be used in calculations</h4>"))
        l.addWidget(a)
        a.setToolTip("If you values below, this will affect the conversion calculation, but the information will not be written back to the database")

        # ## Molecular constants edit fields

        lg = QGridLayout()
        l.addLayout(lg)
        nr, nc, n = 3, 3, len(self._fieldnames)
        ti = db.get_table_info("state")
        for j in range(nc):
            # ### One grid layout for each column of fields
            ii = range(j, n, nc)
            for i in range(len(ii)):
                fieldname = self._fieldnames[ii[i]]
                info = ti.find(name=fieldname)
                caption = info["caption"] or fieldname
                a = QLabel(caption)
                e = QLineEdit("")
                tooltip = info["tooltip"]
                if tooltip:
                    a.setToolTip(tooltip)
                    e.setToolTip(tooltip)
                self._edit_map[fieldname] = e
                lg.addWidget(a, i, j*2)
                lg.addWidget(e, i, j*2+1)


    def __getitem__(self, fieldname):
        """Allows dict-like access of molecular constants of interest. Returns float value or None"""
        if fieldname in self._fieldnames:
            try:
                return float(self._edit_map[fieldname].text())
            except ValueError:
                return None


    def get_all_consts(self):
        """Returns a dictionary with all molecular constants"""
        ret = {}
        for fieldname in self._fieldnames:
            ret[fieldname] = self[fieldname]
        return ret


    def set_id_molecule(self, id_):
        """Calls WDBState.set_id_molecule"""
        self.w_state.set_id_molecule(id_)


    def validate(self):
        """Returns True if all edit fields can be converted to float, otherwise False"""
        ret = True
        for fieldname in self._fieldnames:
            try:
                _ = float(self[fieldname])
            except ValueError:
                self.add_log_error("Failed converting field '{}' to float".format(fieldname))
                ret = False
                break
        return ret


    def _w_state_id_changed(self):
        """Transfer values from self.data to edit fields below the table widget"""
        # id_ = print("State id changed to ", self.w_state.id)
        row = self.w_state.row
        # if not row:
        #     return
        for fieldname, edit in self._edit_map.items():
            value = "" if not row else row[fieldname]
            edit.setText(str(value) if value is not None else "")

