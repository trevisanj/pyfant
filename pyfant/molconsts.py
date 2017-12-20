from . import basic
import os
import inspect
import a99
import pyfant
import re

__all__ = ["MolConsts", "some_molconsts", "MolConstPopulateError",
]

class MolConsts(dict):
    """Dict subclass that will hold several molecular constants, e.g., a table join"""

    # dictionary keys already present (fallback to None) at __init__()
    _KEYS = ["fe", "bm", "te", "do", "ua", "am", "ub",
             "from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf",
             "statel_omega_e", "statel_B_e", "statel_beta_e", "statel_omega_ex_e", "statel_alpha_e",
             "statel_A", "statel_omega_ey_e", "statel_D_e",
             "state2l_omega_e", "state2l_B_e", "state2l_beta_e", "state2l_omega_ex_e",
             "state2l_alpha_e",
             "state2l_A", "state2l_omega_ey_e", "state2l_D_e", "name", "formula",
             "id_molecule", "id_pfantmol", "id_system", "id_statel", "id_state2l",
             "pfant_name", "pfant_notes"]

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

        for key in self._KEYS:
            self.setdefault(key, None)

    def __repr__(self):
        """Will generate sth like 'MolConsts({...})'"""
        _code = "{}({})".format(self.__class__.__name__, dict.__repr__(self))
        code = a99.make_code_readable(_code)
        return code

    def None_to_zero(self):
        """Replaces None values with zero"""

        for key in self:
            if self[key] is None:
                self[key] = 0.

    def get_str(self, style=basic.SS_PLAIN):
        """Returns string such as 'OH [A 2 SIGMA - X 2 PI]

        Args:
            style: SS_*
        """
        need = ("formula", "from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf")
        self._i_need(need)

        return "{} {}".format(self["formula"], basic.molconsts_to_system_str(self, style))

    def get_system_str(self, style=basic.SS_PLAIN):
        """Returns string such as 'A 2 SIGMA - X 2 PI

        Args:
            style: SS_*
        """
        need = ("from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf")
        self._i_need(need)

        return basic.molconsts_to_system_str(self, style)

    def get_S2l(self):
        """**Convention** returns S2l = (to_mult-1)/2"""
        self._i_need(("to_mult",))

        return float(self["to_mult"]-1)/2

    def get_deltak(self):
        """***Convention*** returns the Kronecker delta delta_K(0, Lambdal+Lambda2l)

        delta_K(0, Lambdal+Lambda2l) =

            1 if Lambda1+Lambda2 == 0 ([_ _ Sigma - _ _ Sigma ] transitions)

            0 otherwise

        This replaces using table pfantmol.cro field for the Honl-London factor normalization
        """
        return 1. if self["from_spdf"]+self["to_spdf"] == 0 else 0.

    def populate_parse_str(self, string):
        """
        Populates (from_*) and (to_*) taking PFANT molecule description string as input

        Args:
            string: str following convention below

        **Convention** formula-system string (FSS): "(formula) (ignored) [(system string)]".
                       Formula at start of string, followed by ignored characters until square
                       bracket.

        For the *system string* convention, see f311.filetypes.parse_system_str()

        FSS examples:

            "OH [A 2 Sigma - X 2 Pi]"

            "12C16O INFRARED [X 1 SIGMA+]"
        """

        fieldnames = ["from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf"]

        # Formula
        symbols = basic.description_to_symbols(string)
        if symbols is not None:
            self["formula"] = basic.symbols_to_formula(symbols)
        else:
            match = re.search("[A-Za-z]+", string)
            if match is not None:
                self["formula"] = match.group()

        if self["formula"] is None:
            raise RuntimeError("Cannot determine formula from '{}'".format(string))

        # System
        self.update(zip(fieldnames, basic.parse_system_str(string)))

        # PFANT name and notes
        name, _, notes = basic.split_molecules_description(string)
        self["pfant_name"] = name
        self["pfant_notes"] = notes


    def populate_all_using_system_row(self, db, row):
        print(row["id_molecule"])

        formula = db.get_conn().execute("select formula from molecule where id = ?",
                                        (row["id_molecule"],)).fetchone()["formula"]

        self.populate_all_using_str(db,
            "{} [{}]".format(formula, pyfant.molconsts_to_system_str(row, pyfant.SS_PLAIN)))

    def populate_all_using_str(self, db, string):
        assert isinstance(db, pyfant.FileMolDB)

        self.populate_parse_str(string)

        self.populate_ids(db)

        for key in self:
            if key.startswith("id_"):
                if self[key] is None:
                    raise RuntimeError("Cannot determine '{}'".format(key))

        self.populate_all_using_ids(db)

    def populate_all_using_ids(self, db, id_molecule=None, id_system=None, id_pfantmol=None,
                               id_statel=None, id_state2l=None):
        """
        Populates completely, given all necessary table ids

        Args:
            db: FileMolDB object
            id_molecule: id in table "molecule"
            id_system: id in table "system"
            id_pfantmol: id in table "pfantmol"
            id_statel: id in table "state" for the initial state
            id_state2l: id in table "state" for the final state

        Arguments id_* have a fallback, which is self[argument].


        """
        assert isinstance(db, pyfant.FileMolDB)

        if id_molecule is None: id_molecule = self["id_molecule"]
        if id_system is None: id_system = self["id_system"]
        if id_pfantmol is None: id_pfantmol = self["id_pfantmol"]
        if id_statel is None: id_statel = self["id_statel"]
        if id_state2l is None: id_state2l = self["id_state2l"]

        if id_molecule is None: raise ValueError("Both argument and dictionary value 'id_molecule' are None")
        if id_system is None: raise ValueError("Both argument and dictionary value 'id_system' are None")
        if id_pfantmol is None: raise ValueError("Both argument and dictionary value 'id_pfantmol' are None")
        if id_statel is None: raise ValueError("Both argument and dictionary value 'id_statel' are None")
        if id_state2l is None: raise ValueError("Both argument and dictionary value 'id_state2l' are None")


        # key name, id, table name, prefix for key in dictionary
        _map = [("id_molecule", id_molecule, "molecule", ""),
                ("id_system", id_system, "system", ""),
                ("id_pfantmol", id_pfantmol, "pfantmol", ""),
                ("id_statel", id_statel, "state", "statel_"),
                ("id_state2l", id_state2l, "state", "state2l_"),
                ]

        for keyname, id_, tablename, prefix in _map:
            if id_ is not None:
                ti = db.get_table_info(tablename)
                row = db.get_conn().execute("select * from {} where id = ?".format(tablename),
                                            (id_,)).fetchone()

                if row is None:
                    raise ValueError("Invalid {}: id {} does not exist in table '{}'".format(keyname, id_, tablename))

                for fieldname in ti:
                    if not fieldname.startswith("id"):
                        self[prefix + fieldname] = row[fieldname]

            self[keyname] = id_

    def populate_ids(self, db):
        """Populates (id_*) with values found using (molecule name) and (from_*) and (to_*)."""

        assert isinstance(db, pyfant.FileMolDB)

        ff = ("id_molecule", "id_system", "id_pfantmol", "id_statel", "id_state2l")
        methods = (self._populate_id_molecule, self._populate_id_system,
                   self._populate_id_pfantmol, self._populate_ids_state)

        for f in ff:
            self[f] = None

        for m in methods:
            try:
                m(db)
            except MolConstPopulateError:
                pass

    def _populate_id_molecule(self, db):
        self._i_need(("formula",))

        one = db.get_conn().execute("select id from molecule where formula = ?",
                                    (self["formula"],)).fetchone()
        self["id_molecule"] = one["id"] if one is not None else None

    def _populate_id_system(self, db):
        self._i_need(("id_molecule", "from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf"))

        self["id_system"] = db.find_id_system(self)

    def _populate_ids_state(self, db):
        """Populates id_statel and id_state2l using (from, to)X(label, mult, spdf)"""

        self._i_need(("id_molecule", "from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf"))

        _map = [("from", "id_statel"), ("to", "id_state2l")]
        for fromto, idfieldname in _map:
            fromto_ = (
            self["id_molecule"], self["{}_label".format(fromto)], self["{}_mult".format(fromto)],
            self["{}_spdf".format(fromto)])
            one = db.get_conn().execute(
                "select id from state where id_molecule = ? and label = ? and mult = ? and spdf = ?",
                fromto_).fetchone()

            self[idfieldname] = one["id"] if one is not None else None

    def _populate_id_pfantmol(self, db):
        """Populates id_pfantmol using formula, to_*, and from_*"""

        need = ("formula", "from_label", "from_mult", "from_spdf", "to_label", "to_mult", "to_spdf")
        if any((self[x] is None for x in need)):
            raise MolConstPopulateError("I need ({})".format(", ".join(need)))

        self["id_pfantmol"] = None

        # Will check match one by one. Will have to parse PFANT molecule descriptions.
        # **Note** currently not accounting for ambiguous match (always takes first match).
        #
        cursor = db.get_conn().execute("select * from pfantmol")
        for row in cursor:
            another = MolConsts()
            another.populate_parse_str(row["description"])

            found = True
            for field_name in need:
                if self[field_name] != another[field_name]:
                    found = False
                    break

            if found:
                self["id_pfantmol"] = row["id"]
                return



    def _i_need(self, need):
        if any((self[fieldname] is None for fieldname in need)):
            for fieldname in need:
                if self[fieldname] is None:
                    break

            method_name = inspect.stack()[1][3]
            raise MolConstPopulateError("Method {}() needs (), but at least '{}' is None".format(
                method_name, need, fieldname))


def some_molconsts(db=None, s="OH [A 2 SIGMA - X 2 PI]"):
    """
    Returns a MolConsts object completely populated

    Args:
        db: FileMolDB object.

            **Note** If None, this function will attempt to create 'moldb.xxxx.sqlite',
                     then attempt to delete it

        s: parseable formula-and-system (refer to
    """

    flag_newdb = False
    if db is None:
        flag_newdb = True
        db = pyfant.FileMolDB()
        db.init_default()

    ret = MolConsts()
    try:
        ret.populate_all_using_str(db, s)

    finally:
        db.get_conn().close()
        if flag_newdb:
            try:
                os.unlink(db.filename)
            except FileNotFoundError:
                pass

    ret.None_to_zero()

    return ret


class MolConstPopulateError(Exception):
    pass


