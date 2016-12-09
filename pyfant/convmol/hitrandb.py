"""
HITRAN Molecules and Isotopologues list

This database is parsed from HITRAN web pages. It is not one's intention to add entries to it.

In the case of new data on HITRAN, the whole database should be re-created
"""

import astroapi as aa
import pyfant as pf
import sqlite3
import tabulate


__ALIAS = "hitrandb"


def get_conn():
    return aa.get_conn(__ALIAS)


def _setup_db_metadata():
    aa.add_database(__ALIAS, aa.get_path("data", "{}.sqlite".format(__ALIAS), module=pf), {})


def create_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""create table molecule (ID integer unique, Formula text unique, Name text)""")
    # **Note** isotopologue.ID is not unique, it starts over for each molecule
    c.execute("""create table isotopologue (ID integer,
                                            ID_molecule integer,
                                            Formula text unique,
                                            AFGL_Code integer,
                                            Abundance real
                                           )""")
    conn.commit()
    conn.close()


def populate_db():
    conn = get_conn()
    try:

        mols, _ = pf.get_hitran_molecules()

        conn.executemany("insert into molecule values (?,?,?)", mols)

        aa.get_python_logger().info("Inserted {} molecules".format(len(mols)))

        for mol in mols:
            isos, _ = pf.get_hitran_isotopologues(mol[0])

            for iso in isos:
                try:
                    conn.execute("insert into isotopologue values(?,?,?,?,?)", [iso[0], mol[0], *iso[1:]])
                except:
                    aa.get_python_logger().exception("Tried to insert this: {}".format(iso))
                    raise

            aa.get_python_logger().info("Inserted {} isotopologues for molecule '{}' ({})".
                                    format(len(isos), *mol[1:3]))

    finally:
        conn.commit()
        conn.close()


def query_molecule(**kwargs):
    """Convenience function to query 'molecule' table

    Args:
        **kwargs: filter fieldname=value pairs to be passed to WHERE clause

    Returns: sqlite3 cursor
    """
    where = ""
    if len(kwargs) > 0:
        where = " where " + " and ".join([key + " = ?" for key in kwargs])
    conn = get_conn()
    sql = """select * from molecule{} order by ID""".format(where)
    r = conn.execute(sql, list(kwargs.values()))
    return r


def query_isotopologue(**kwargs):
    """Convenience function to query 'isotopologue' table

    Args, Returns: see query_molecule

    Example:
    >>> _ = query_isotopologue(**{"molecule.formula": "OH"})
    """
    where = ""
    if len(kwargs) > 0:
        where = " where " + " and ".join([key + " = ?" for key in kwargs])
    conn = get_conn()
    sql = """select molecule.formula as m_formula, isotopologue.* from isotopologue
             join molecule on isotopologue.id_molecule = molecule.id{}""".format(where)
    r = conn.execute(sql, list(kwargs.values()))
    return r


def print_isotopologues(**kwargs):
    """
    Prints isotopologues table in console

    Args:
        **kwargs: arguments passed to query_state()

    >>> print_isotopologues(**{"molecule.formula": "CO"})
    """
    r = query_isotopologue(**kwargs)
    data, header = aa.cursor_to_data_header(r)
    print(tabulate.tabulate(data, header))
