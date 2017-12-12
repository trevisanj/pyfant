import a99
import tabulate
import f311


__all__ = ["FileHitranDB", "populate_hitrandb"]

#
# __fileobj = None
# def get_conn():
#     return a99.get_conn(__ALIAS)


class FileHitranDB(f311.FileSQLiteDB):
    """HITRAN Molecules Catalogue"""

    default_filename = "hitrandb.sqlite"

    def _create_schema(self):
        conn = self.get_conn()
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

    def query_molecule(self, **kwargs):
        """Convenience function to query 'molecule' table

        Args:
            **kwargs: filter fieldname=value pairs to be passed to WHERE clause

        Returns: sqlite3 cursor
        """
        where = ""
        if len(kwargs) > 0:
            where = " where " + " and ".join([key + " = ?" for key in kwargs])
        conn = self.get_conn()
        sql = """select * from molecule{} order by ID""".format(where)
        r = conn.execute(sql, list(kwargs.values()))
        return r

    def query_isotopologue(self, **kwargs):
        """Convenience function to query 'isotopologue' table

        Args, Returns: see query_molecule

        Example:

        >>> f = FileHitranDB()
        >>> f.init_default()
        >>> _ = f.query_isotopologue(**{"molecule.formula": "OH"})
        """
        where = ""
        if len(kwargs) > 0:
            where = " where " + " and ".join([key + " = ?" for key in kwargs])
        conn = self.get_conn()
        sql = """select molecule.formula as m_formula, isotopologue.* from isotopologue
                 join molecule on isotopologue.id_molecule = molecule.id{}""".format(where)
        r = conn.execute(sql, list(kwargs.values()))
        return r

    def print_isotopologues(self, **kwargs):
        """
        Prints isotopologues table in console

        Args:
            **kwargs: arguments passed to query_state()

        Example:

        >>> f = FileHitranDB()
        >>> f.init_default()
        >>> f.print_isotopologues(**{"molecule.formula": "CO"})
        """
        r = self.query_isotopologue(**kwargs)
        data, header = a99.cursor_to_data_header(r)
        print(tabulate.tabulate(data, header))


def populate_hitrandb(db):
    """Populates database with HITRAN data

    Populates a sqlite3 database represented by a FileHitranDB object with information downloaded
    from the HITRAN website

    Args:
        db: FileHitranDB instance

    .. todo:: This routine is never used
    """

    import pyfant

    assert isinstance(db, pyfant.FileHitranDB)
    conn = db.get_conn()
    try:

        mols, _ = pyfant.get_hitran_molecules()

        conn.executemany("insert into molecule values (?,?,?)", mols)

        a99.get_python_logger().info("Inserted {} molecules".format(len(mols)))

        for mol in mols:
            isos, _ = pyfant.get_hitran_isotopologues(mol[0])

            for iso in isos:
                try:
                    conn.execute("insert into isotopologue values(?,?,?,?,?)",
                                 [iso[0], mol[0]] + iso[1:])
                except:
                    a99.get_python_logger().exception("Tried to insert this: {}".format(iso))
                    raise

            a99.get_python_logger().info("Inserted {} isotopologues for molecule '{}' ({})".
                                         format(len(isos), *mol[1:3]))
    finally:
        conn.commit()
        conn.close()

    conn.close()

