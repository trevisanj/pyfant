__all__ = ["WSpectrumCollection"]

import collections
import copy
import matplotlib.pyplot as plt
from pylab import MaxNLocator
import numbers
import numpy as np
import os
import os.path
from itertools import product, combinations, cycle
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pyfant import *
from pyfant.datatypes.filesplist import *
from pyfant.gui import *
from .basewindows import *
from .a_WChooseSpectrum import *
from .a_XScaleSpectrum import *
from ..a_WCollapsiblePanel import *


class WSpectrumCollection(WBase):
    """Editor for SpectrumCollection objects"""

    # argument0 -- flag_changed_header
    edited = pyqtSignal(bool)

    def __init__(self, parent):
        WBase.__init__(self, parent)

        def keep_ref(obj):
            self._refs.append(obj)
            return obj

        # Whether all the values in the fields are valid or not
        self.flag_valid = False
        # Internal flag to prevent taking action when some field is updated programatically
        self.flag_process_changes = False
        self.collection = None # SpectrumCollection

        # # Central layout
        # Will have a toolbox and a table. When the toolbox contracts, there is more space for the table
        lwmain = self.centralLayout = QVBoxLayout()
        lwmain.setMargin(0)
        self.setLayout(lwmain)


        # ## Toolbox
        # The toolbox will have only one widget whose layout is a grid with two columns:
        #   - The first column contains labels
        #   - The second column contains panels of buttons layed horizontally
        # tb = keep_ref(QToolBox())
        # # tb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # lwmain.addWidget(tb)
        wgrid = keep_ref(WCollapsiblePanel())
        wgrid.label.setText("<b>Tools</b>")
        wgrid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lwmain.addWidget(wgrid)
        lg = QGridLayout(wgrid.widget)
        lg.setMargin(2)
        lg.setSpacing(4)
        # tb.addItem(wgrid, "Actions")
        # First column of the grid layout is sorted
        label = keep_ref(QLabel('<b>File:</b>'))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lg.addWidget(label, 0, 0)
        label = keep_ref(QLabel('<b>With all:</b>'))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lg.addWidget(label, 1, 0)
        label = keep_ref(QLabel('<b>With selected:</b>'))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lg.addWidget(label, 2, 0)
        label = keep_ref(QLabel('<b>With current:</b>'))
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lg.addWidget(label, 3, 0)


        # ### Panel #0: operations independent of the table widget selection state
        ###
        lh = QHBoxLayout()
        lh.setMargin(0)
        lh.setSpacing(2)
        lg.addLayout(lh, 0, 1)
        lwmain.addLayout(lh)
        ###
        b = keep_ref(QPushButton("Add spectra..."))
        b.setToolTip("Opens a 'Open File' window where multiple files can be selected.\n"
                     "Accepts any supported spectral type, and also other Spectrum Collection files.\n"
                     "Files are added in alphabetical order.")
        b.clicked.connect(self.on_add_spectra)
        lh.addWidget(b)
        ###
        lh.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))



        # ### Panel #1: operations independent of the table widget selection state
        ###
        lh = QHBoxLayout()
        lh.setMargin(0)
        lh.setSpacing(2)
        lg.addLayout(lh, 1, 1)
        ###
        b = keep_ref(QPushButton("Export CSV..."))
        b.clicked.connect(self.on_export_csv)
        lh.addWidget(b)
        ###
        b = self.button_query = QPushButton("Query")
        b.clicked.connect(self.on_query)
        lh.addWidget(b)
        ###
        lh.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))


        # ### Panel #2: operations affecting only the spectra which are selected
        ###
        lh = QHBoxLayout()
        lh.setMargin(0)
        lh.setSpacing(2)
        lg.addLayout(lh, 2, 1)
        ###
        b = keep_ref(QPushButton("Plot &stacked"))
        b.clicked.connect(self.plot_stacked_clicked)
        lh.addWidget(b)
        ###
        b = keep_ref(QPushButton("Plot &overlapped"))
        b.clicked.connect(self.plot_overlapped_clicked)
        lh.addWidget(b)
        ###
        # b = keep_ref(QPushButton("Calc.Mag."))
        # b.clicked.connect(self.calc_mag_clicked)
        # lh.addWidget(b)
        # ###
        b = keep_ref(QPushButton("&Extract Scalar..."))
        b.clicked.connect(self.extract_scalar_clicked)
        lh.addWidget(b)
        # ###
        b = keep_ref(QPushButton("Open in new window"))
        b.clicked.connect(self.open_in_new_clicked)
        lh.addWidget(b)
        ###
        b = keep_ref(QPushButton("Delete"))
        b.clicked.connect(self.delete_selected)
        lh.addWidget(b)
        ###
        lh.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))


        # ### Panel #3: operations affecting only the current spectrum
        ###
        lh = QHBoxLayout()
        lh.setMargin(0)
        lh.setSpacing(2)
        lg.addLayout(lh, 3, 1)
        ###
        b = keep_ref(QPushButton("Scale..."))
        b.clicked.connect(self.scale_clicked)
        lh.addWidget(b)
        ###
        lh.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        a = self.twSpectra = QTableWidget()
        # lwmain.addWidget(a)
        a.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        a.setSelectionMode(QAbstractItemView.MultiSelection)
        a.setSelectionBehavior(QAbstractItemView.SelectRows)
        a.setAlternatingRowColors(True)
        a.cellChanged.connect(self.on_twSpectra_cellChanged)
        a.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        a.setFont(MONO_FONT)
        a.installEventFilter(self)
        a.setContextMenuPolicy(Qt.CustomContextMenu)
        a.customContextMenuRequested.connect(self.on_twSpectra_customContextMenuRequested)
        a.setSortingEnabled(True)
        ah = a.horizontalHeader()
        ah.setMovable(True)
        ah.sectionMoved.connect(self.section_moved)
        ah.setContextMenuPolicy(Qt.CustomContextMenu)
        ah.customContextMenuRequested.connect(self.show_header_context_menu)
        ah.setSelectionMode(QAbstractItemView.SingleSelection)
        # tb.addItem(a, "Spectra")

        lwmain.addWidget(a)


        self.setEnabled(False)  # disabled until load() is called
        style_checkboxes(self)
        self.flag_process_changes = True
        self.add_log("Welcome from %s.__init__()" % (self.__class__.__name__))


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Interface

    def set_collection(self, x):
        assert isinstance(x, SpectrumCollection)
        self.collection = x
        self.__update_gui()
        self.setEnabled(True)
        self.button_query.setEnabled(isinstance(self.collection, SpectrumList))

    def get_selected_spectra(self):
        return [self.collection.spectra[i] for i in self.get_selected_spectrum_indexes()]

    def get_selected_row_indexes(self):
        ii = list(set([index.row() for index in self.twSpectra.selectedIndexes()]))
        return ii

    def get_selected_spectrum_indexes(self):
        items = self.twSpectra.selectedItems()
        ii = []
        for item in items:
            obj = item.data(1).toPyObject()
            if isinstance(obj, int):
                ii.append(obj)
        ii.sort()
        return ii

    def row_index_to_spectrum_index(self, row_index):
        """
        Converts table row index within self.collection.spectra

        This is necessary because the table may be sorted
        """

        item = self.twSpectra.item(row_index, self.twSpectra.columnCount()-1)
        ret = item.data(1).toPyObject()
        return ret

    def get_current_spectrum_index(self):
        return self.row_index_to_spectrum_index(self.twSpectra.currentRow())

    def get_current_spectrum(self):
        """Returns spectrum on which the table cursor (movable with the keyboar arrows) is currently"""
        if self.twSpectra.rowCount() < 1:
            return None
        return self.collection.spectra[self.get_current_spectrum_index()]

    def update(self):
        """Refreshes the GUI to reflect what is in self.collection"""
        self.__update_gui()

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Qt override

    def setFocus(self, reason=None):
        """Sets focus to first field. Note: reason is ignored."""
        self.twSpectra.setFocus()

    def eventFilter(self, source, event):
        if event.type() == QEvent.FocusIn:
            # text = random_name()
            # self.__add_log(text)
            pass

        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Delete:
                if source == self.twSpectra:
                    n_deleted = self.__delete_spectra()
                    if n_deleted > 0:
                        self.edited.emit(False)
        return False

    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Slots

    def section_moved(self, idx_logical, idx_vis_old, idx_vis_new):
        obj = self.collection
        l = self.collection.fieldnames_visible
        fieldname_current = l[idx_vis_old]
        del l[idx_vis_old]
        l.insert(idx_vis_new, fieldname_current)

    def show_header_context_menu(self, position):
        obj = self.collection

        ah = self.twSpectra.horizontalHeader()
        # col_idx = ah.logicalIndexAt(position)
        col_idx = ah.visualIndex(ah.logicalIndexAt(position))

        menu = QMenu()
        act_hide_current = None

        if col_idx < len(obj.fieldnames_visible):
            fieldname_current = obj.fieldnames_visible[col_idx]
            act_hide_current = menu.addAction("&Hide field '%s'" % fieldname_current)
            menu.addSeparator()

        act_show_all = menu.addAction("&Show all fields")
        act_hide_all = menu.addAction("&Hide all fields")
        act_restore_order = menu.addAction("&Restore order")
        menu.addSeparator()

        aa_visible = []
        for fieldname in obj.fieldnames:
            act = menu.addAction(fieldname)
            act.setCheckable(True)
            act.setChecked(fieldname in obj.fieldnames_visible)
            aa_visible.append(act)

        action = menu.exec_(self.twSpectra.mapToGlobal(position))
        flag_update = False
        if action == act_hide_current:
            obj.fieldnames_visible.remove(fieldname_current)
            flag_update = True

        elif action == act_show_all:
            for fieldname in reversed(obj.fieldnames):
                if not fieldname in obj.fieldnames_visible:
                    obj.fieldnames_visible.insert(0, fieldname)
                    flag_update = True

        elif action == act_hide_all:
            obj.fieldnames_visible = []
            flag_update = True

        elif action == act_restore_order:
            curr_visible = copy.copy(obj.fieldnames_visible)
            obj.fieldnames_visible = []
            for fieldname in obj.fieldnames:
                if fieldname in curr_visible:
                    obj.fieldnames_visible.append(fieldname)
            flag_update = not (curr_visible == obj.fieldnames_visible)

        elif action in aa_visible:
            idx = aa_visible.index(action)
            if not aa_visible[idx].isChecked():
                obj.fieldnames_visible.remove(obj.fieldnames[idx])
            else:
                obj.fieldnames_visible.insert(0, obj.fieldnames[idx])
            flag_update = True

        if flag_update:
            self.__update_gui()
            self.edited.emit(False)

    def on_twSpectra_customContextMenuRequested(self, position):
        """Mounts, shows popupmenu for the tableWidget control, and takes action."""
        obj = self.collection
        menu = QMenu()
        act_del = menu.addAction("&Delete selected (Del)")

        action = menu.exec_(self.twSpectra.mapToGlobal(position))
        flag_update = False
        if action == act_del:
            n_deleted = self.__delete_spectra()
            if n_deleted > 0:
                self.edited.emit(False)

        if flag_update:
            self.edited.emit(False)
            self.__update_gui()

    def plot_stacked_clicked(self):
        sspp = self.get_selected_spectra()
        if len(sspp) > 0:
            plot_spectra(sspp)

    def plot_overlapped_clicked(self):
        sspp = self.get_selected_spectra()
        if len(sspp) > 0:
            plot_spectra_overlapped(sspp)


    def extract_scalar_clicked(self):
        sspp = self.get_selected_spectra()
        flag_emit, flag_changed_header = False, False
        if len(sspp) > 0:
            from .a_XApplySB_scalar import XApplySB_scalar

            form = self.keep_ref(XApplySB_scalar())
            if not form.exec_():
                return

            # It sth fails, will restore original
            save = copy.deepcopy(self.collection)

            try:
                for sp in sspp:
                    sp.more_headers[form.fieldname] = form.block.use(sp)

                self.__update_gui()
                flag_emit = True

            except Exception as E:
                self.add_log_error("Failed to extract scalar: %s" % str(E), True)
                raise

        if flag_emit:
            self.edited.emit(True)




    # def calc_mag_clicked(self):
    #     sspp = self.get_selected_spectra()
    #     flag_emit, flag_changed_header = False, False
    #     if len(sspp) > 0:
    #
    #         try:
    #             specs = (("band_name", {"value": "V", "labelText": "Band name (%s)" % ("/".join(Bands.bands.keys()),)}),
    #                      ("flag_force_parametric", {"value": False, "labelText": "Always use parametric band form?",
    #                                                 "toolTip": "Use (center, FWHM) to calculate the band even if tabular data is available"}),
    #                     )
    #             form = XParametersEditor(specs=specs, title="Calculate magnitudee")
    #             while True:
    #                 r = form.exec_()
    #                 if not r:
    #                     break
    #                 kk = form.get_kwargs()
    #                 band_name = kk["band_name"].upper()
    #
    #                 if not band_name in Bands.bands.keys():
    #                     show_error("Invalid band name")
    #                     continue
    #
    #                 for sp in sspp:
    #                     dict_ = sp.calculate_magnitude(band_name, kk["flag_force_parametric"])
    #
    #                 # appends field names so that newly calculated magnitude will appear in the table
    #                 for fn in dict_["fieldnames"]:
    #                     if fn not in self.collection.fieldnames:
    #                         self.collection.fieldnames.append(fn)
    #                         flag_changed_header = True
    #                     if fn not in self.collection.fieldnames_visible:
    #                         self.collection.fieldnames_visible.append(fn)
    #                         flag_changed_header = True
    #
    #                 self.__update_gui()
    #                 flag_emit = True
    #                 break
    #
    #         except Exception as E:
    #             self.add_log_error("Magnitude calculation: %s" % str(E), True)
    #             raise
    #
    #     if flag_emit:
    #         self.edited.emit(flag_changed_header)
    #
    def open_in_new_clicked(self):
        from .a_XFileSpectrumList import XFileSpectrumList
        ii = self.get_selected_spectrum_indexes()
        if len(ii) > 0:
            other = copy.deepcopy(self.collection)
            other.spectra = [other.spectra[i] for i in ii]
            f = FileSpectrumList()
            f.splist = other

            form = self.keep_ref(XFileSpectrumList())
            form.load(f)
            form.show()

    def delete_selected(self):
        n = self.__delete_spectra()
        if n > 0:
            self.edited.emit(False)

    def scale_clicked(self):
        """Performs a scaling operation on the current spectrum"""
        sp = self.get_current_spectrum()

        if sp is None:
            return

        form = XScaleSpectrum()
        form.set_spectrum(sp)
        if form.exec_():
            k = form.factor()
            if k != 1:
                sp.y *= k
                self.__update_gui()
                self.edited.emit(False)

    def on_twSpectra_cellChanged(self, row, column):
        if self.flag_process_changes:
            flag_emit = False
            text = None
            item = self.twSpectra.item(row, column)
            name = self.__get_tw_header(column)
            try:
                value = str(item.text())
                # Tries to convert to float, otherwise stores as string
                try:
                    value = float(value)
                except:
                    pass

                # Certain fields must evaluate to integer because they are pixel positions
                if name in ("PIXEL-X", "PIXEL-Y", "Z-START"):
                    value = int(value)

                self.collection.spectra[row].more_headers[name] = value

                flag_emit = True
                # replaces edited text with eventually cleaner version, e.g. decimals from integers are discarded
                item.setText(str(value))

            except Exception as E:
                # restores original value
                item.setText(str(self.collection.spectra[row].more_headers.get(name)))
                self.add_log_error(str_exc(E), True)
                raise

            if flag_emit:
                self.edited.emit(False)

    def on_export_csv(self):
        new_filename = QFileDialog.getSaveFileName(self, "Export text file (CSV format)", "export.csv", "*.csv")
        if new_filename:
            # self.save_dir, _ = os.path.split(str(new_filename))
            try:
                lines = self.collection.to_csv()
                with open(str(new_filename), "w") as file:
                    file.writelines(lines)
            except Exception as E:
                msg = str("Error exporting text file: %s" % str_exc(E))
                self.add_log_error(msg, True)
                raise

    def on_query(self):
        # Import here to circumvent cyclic dependency
        from .a_XQuery import XQuery
        form = self.keep_ref(XQuery())
        form.set_splist(copy.deepcopy(self.collection))
        form.show()

    def on_add_spectra(self):
        flag_emit = False
        filenames = QFileDialog.getOpenFileNames(self, "Add Spectra", "",
         "All files(*.*);;Spectrum List files (*.splist);;Sparse Cube files (*.sparsecube)")
        if not filenames:
            return

        classes = classes_sp+[FileSpectrumList, FileSparseCube]
        report, successful, failed = ["<b>Results</b>"], [], []
        for filename in filenames:
            filename = str(filename)
            basename = os.path.basename(filename)
            file = load_with_classes(filename, classes)
            try:
                if file is None:
                    raise RuntimeError("Could not load file")
                if isinstance(file, FileSpectrum):
                    self.collection.add_spectrum(file.spectrum)
                elif isinstance(file, FileSpectrumList):
                    self.collection.merge_with(file.splist)
                elif isinstance(file, FileSparseCube):
                    self.collection.merge_with(file.sparsecube)
                successful.append("  - %s" % basename)
            except Exception as e:
                failed.append('&nbsp;&nbsp;- %s: %s' % (basename, str(e)))
                self.add_log_error("Error adding file '%s': %s" % (basename, str_exc(e)))

        if len(successful) > 0:
            report.extend(["", "Successful:"])
            report.extend(successful)

            self.__update_gui()
            flag_emit = True

        if len(failed) > 0:
            report.extend(["", "Failed:"])
            report.extend(failed)

        if flag_emit:
            self.edited.emit(False)

        show_message("<br>".join(report))


    # def on_merge_with(self):
    #     flag_emit = False
    #     try:
    #         # TODO another SpectrumCollection, not SpectrumList
    #         new_filename = QFileDialog.getOpenFileName(self, "Merge with another Spectrum List file", "", "*.splist")
    #         if new_filename:
    #             new_filename = str(new_filename)
    #             f = FileSpectrumList()
    #             f.load(new_filename)
    #             self.collection.merge_with(f.splist)
    #             self.__update_gui()
    #             flag_emit = True
    #     except Exception as E:
    #         msg = "Error merging: %s" % str_exc(E)
    #         self.add_log_error(msg, True)
    #         raise
    #
    #     if flag_emit:
    #         self.edited.emit(False)
    #


    # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * # * #
    # # Internal gear


    def __get_tw_header(self, column):
        return str(self.twSpectra.horizontalHeaderItem(column).text())

    def __update_gui(self):
        self.flag_process_changes = False
        try:
            # Builds table widget contents
            spectra = self.collection.spectra
            t = self.twSpectra
            n = len(spectra)
            FIXED = ["Spectrum summary report"]
            fieldnames_visible = self.collection.fieldnames_visible
            all_headers = fieldnames_visible+FIXED
            nc = len(all_headers)
            ResetTableWidget(t, n, nc)
            t.setHorizontalHeaderLabels(all_headers)
            i = 0
            for sp in spectra:
                j = 0

                # Spectrum.more_headers columns
                for h in fieldnames_visible:
                    twi = QTableWidgetItem(str(sp.more_headers.get(h)))
                    if h in "Z-START":  # fields that should be made read-only
                        twi.setFlags(twi.flags() & ~Qt.ItemIsEditable)
                    t.setItem(i, j, twi)
                    j += 1

                # Spectrum self-generated report
                twi = QTableWidgetItem(sp.one_liner_str())
                twi.setFlags(twi.flags() & ~Qt.ItemIsEditable)
                # stores spectrum index not to lose track in case the table is sorted by column
                twi.setData(1, QVariant(i))
                t.setItem(i, j, twi)
                j += 1

                i += 1

            t.resizeColumnsToContents()

        finally:
            self.flag_process_changes = True

    def __delete_spectra(self):
        ii = self.get_selected_spectrum_indexes()
        if len(ii) > 0:
            self.collection.delete_spectra(ii)
            self.__update_gui()

        return len(ii)
