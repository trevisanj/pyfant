#!/usr/bin/env python
# coding: utf8
"""
Script to put together the file moldb.sqlite

**Note** This script is protected, but is very important to put to put together a lot of information
needed for molecular lines conversion (``convmol.py``)
"""

import pyfant
import a99
from collections import OrderedDict
import sqlite3
import os
import sys

FORMULAS = ["MgH", "C2", "CN", "CH", "NH", "CO", "OH", "FeH", "TiO", ]

# Electronic systems containing Franck-Condon factors in this directory
SYSTEMS_MAP = (
("CH", "cha.out", "A", 2, 2, "X", 2, 1, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),  # A2Delta - X2Pi
("CH", "chb.out", "B", 2, 0, "X", 2, 1, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),
("CH", "chc.out", "C", 2, 0, "X", 2, 1, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),
("CN", "cnb.out", "B", 2, 0, "X", 2, 0, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),
("NH", "nha.out", "A", 3, 1, "X", 3, 0, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),
("OH", "oha.out", "A", 2, 0, "X", 2, 1, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),
("MgH", "mgha.out", "A", 2, 1, "X", 2, 0, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),
("MgH", "mghb.out", "B", 2, 0, "X", 2, 0, "Source: 'ATMOS/wrk4/bruno/Mole/Fc'"),
("C2", "c2swan.out", "d", 3, 1, "a", 3, 1, "Source: 'new calculations'"),
)


# FileMolecules
filemol = None
moldb = None
conn = None


def my_info(s):
    a99.get_python_logger().info("[build-moldb] {}".format(s))


def insert_molecules(moldb):
    """Inserts data into the 'molecule' table"""

    for formula in FORMULAS:
        my_info("Inserting '{}' + its NIST states ...".format(formula))
        pyfant.insert_molecule_from_nist(moldb, formula, flag_do_what_i_can=True, flag_replace=True)

    # # Molecules present in PFANT molecules.dat
    # MOLECULES = [("MgH", "Magnesium monohydride"),
    #              ("C2", "Dicarbon"),
    #              ("CN", "Cyano radical"),
    #              ("CH", "Methylidyne"),
    #              ("NH", "Imidogen"),
    #              ("CO", "Carbon monoxide"),
    #              ("OH", "Hydroxyl radical"),
    #              ("FeH", "Iron hydride"),
    #              ("TiO", "Titanium oxide")]
    #
    # conn.executemany("insert into molecule (formula, name) values (?,?)", MOLECULES)
    # conn.commit()


def insert_systems():
    """Parses the systems out of the molecules descriptions in the PFANT molecular lines file"""

    # Collects PFANT systems
    # Iterates through the PFANT molecules to retrieve its systems.
    # Information is stored as MolConsts objects in which only the formula and system information are set
    rows = []
    for molecule in filemol:
        row = pyfant.MolConsts()
        row.populate_parse_str(molecule.description)

        my_info("{} [{}]".format(row["formula"], pyfant.molconsts_to_system_str(row)))

        id_molecule = conn.execute("select id from molecule where formula = ?",
                                   (row["formula"],)).fetchone()["id"]

        row["id_molecule"] = id_molecule

        # Inserts data into the 'system' table
        id_system = moldb.insert_system_if_does_not_exist(row, "by _build-moldb.insert_systems()")

        # Inserts data into the 'pfantmol' table
        # TODO "s" is redundand, make sure I am not using it
        conn.execute("insert into pfantmol "
                     "(id_system, description, fe, do, am, bm, ua, ub, te, cro) "
                     "values (?,?,?,?,?,?,?,?,?,?)",
                     (id_system, molecule.description, molecule.fe, molecule.do, molecule.am,
                      molecule.bm, molecule.ua, molecule.ub, molecule.te,
                      molecule.cro))

    conn.commit()

#
# def insert_nist_data():
#     """Tries to download data from NIST Web Book online"""
#
#     for row in conn.execute("select id, formula from molecule order by id").fetchall():
#         id_molecule, formula = row["id"], row["formula"]
#         a99.get_python_logger().info("Molecule '{}'...".format(formula))
#         try:
#             data, _, _ = pyfant.get_nist_webbook_constants(formula)
#
#             for state in data:
#                 # **Note** assumes that the columns in data match the
#                 # (number of columns in the state table - 2) and their order
#                 conn.execute("insert into state values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
#                              [None, id_molecule] + state + [""])
#
#             conn.commit()
#
#         except:
#             a99.get_python_logger().exception("Failed for molecule '{}'".format(formula))
#     conn.commit()


def load_list_file(filename):
    """Loads a file containing (vl, v2l, FranckCondonFactor)

    ===begin exert===
    00 00 sj0000.dat .8638228E+00
    00 01 sj0001.dat .8712862E-01
    00 02 sj0002.dat .3144656E-01
    ===end exert===
    """

    fcfs = OrderedDict()
    with open(filename, "r") as h:
        for line in h:
            vl, v2l, _, fcf = line.strip().split(" ")
            vl = int(vl)
            v2l = int(v2l)
            fcf = float(fcf)
            fcfs[(vl, v2l)] = fcf
    return fcfs


def insert_franck_condon_factors():
    for formula, filename, from_label, from_mult, from_spdf, to_label, to_mult, to_spdf, notes in SYSTEMS_MAP:
        my_info("FCFs for system ({}, {}, {}, {}, {}, {}, {})".
                format(formula, from_label, from_mult, from_spdf, to_label, to_mult, to_spdf))

        id_molecule = conn.execute("select id from molecule where formula = ?",
                                   (formula,)).fetchone()["id"]


        molconsts = pyfant.MolConsts()
        molconsts.update(id_molecule = id_molecule, from_label = from_label,
         from_mult = from_mult, from_spdf = from_spdf, to_label = to_label,
         to_mult = to_mult, to_spdf = to_spdf)

        id_system = moldb.insert_system_if_does_not_exist(molconsts,
         notes="by _build-moldb.insert_franck_condon_factors()")

        if filename is not None:
            # Can handle two different file formats
            try:
                a = pyfant.FileTRAPRBOutput()
                a.load(filename)
                fcf_dict = a.fcfs
            except:
                fcf_dict = load_list_file(filename)
            for (vl, v2l), fcf in fcf_dict.items():
                conn.execute("insert into fcf (id_system, vl, v2l, value) values (?,?,?,?)",
                             (id_system, vl, v2l, fcf))
    conn.commit()


if __name__ == "__main__":
    filename = pyfant.FileMolDB.default_filename

    if os.path.isfile(filename):
        if a99.yesno("File '{}' already exists, get rid of it and continue".format(filename), True):
            os.unlink(filename)
        else:
            sys.exit()

    yn = a99.yesno("Will now create file '{}'. Continue".format(filename), True)

    if not yn:
        sys.exit()


    moldb = pyfant.FileMolDB()
    moldb.filename = filename
    my_info("Creating schema...")
    moldb.create_schema()

    filemol = pyfant.FileMolecules()
    filemol.load(pyfant.get_pfant_data_path("common", "molecules.dat"))


    conn = moldb.get_conn()
    assert isinstance(conn, sqlite3.Connection)


    my_info("New filename: '{}'".format(moldb.filename))
    my_info("Inserting molecules & NIST states...")
    insert_molecules(moldb)
    my_info("Inserting systems...")
    insert_systems()
    my_info("Inserting Franck-Condon Factors from Bruno Castilho's work...")
    insert_franck_condon_factors()

    # my_info("Inserting data from NIST Chemistry Web Book ({})...".format(pyfant.NIST_URL))
    # insert_nist_data()
