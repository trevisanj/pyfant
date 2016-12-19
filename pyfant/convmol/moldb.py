# import astroapi as aa
# import pyfant as pf
# import sqlite3
# import tabulate
#
#
# __ALIAS = "moldb"
#
#
# def get_conn():
#     return aa.get_conn(__ALIAS)
#
#
# class MoleculeRow(aa.MyDBRow):
#     pass
#
#
# class StateRow(aa.MyDBRow):
#     """
#     Represents a row from the 'state' table
#
#     Arguments:
#         id_ -- if passed, will fetch row from table
#
#     >>> StateRow(108)
#     StateRow([('id', 108), ('id_molecule', 8), ('State', 'a ⁱDelta'), ('T_e', 'a'), ('omega_e', 1009.3), ('omega_ex_e', 3.9), ('omega_ey_e', None), ('B_e', 0.5376), ('alpha_e', 0.00298), ('gamma_e', None), ('D_e', 5.9), ('beta_e', None), ('r_e', 1.6169), ('Trans', None), ('nu_00', None)])
#     >>> StateRow([('id', 108), ('id_molecule', 8), ('State', 'a ⁱDelta'), ('T_e', 'a'), ('omega_e', 1009.3), ('omega_ex_e', 3.9), ('omega_ey_e', None), ('B_e', 0.5376), ('alpha_e', 0.00298), ('gamma_e', None), ('D_e', 5.9), ('beta_e', None), ('r_e', 1.6169), ('Trans', None), ('nu_00', None)])
#     StateRow([('id', 108), ('id_molecule', 8), ('State', 'a ⁱDelta'), ('T_e', 'a'), ('omega_e', 1009.3), ('omega_ex_e', 3.9), ('omega_ey_e', None), ('B_e', 0.5376), ('alpha_e', 0.00298), ('gamma_e', None), ('D_e', 5.9), ('beta_e', None), ('r_e', 1.6169), ('Trans', None), ('nu_00', None)])
#     """
#     def __init__(self, sth=None):
#         aa.MyDBRow.__init__(self)
#         if isinstance(sth, int):
#             self.update(get_conn().execute("select * from state where id = 108").fetchone())
#         elif sth is not None:
#             self.update(sth)
#
#
# def _setup_db_metadata():
#     """
#     Invervenes in module astroapi.litedb locals. Called from pyfant.__init__
#     """
#
#     # TODO maybe save it as ~/.molecular-constants.sqlite when convmol.py is executed first time,
#     # TODO not nice to maintain a file that is inside tha package
#     aa.add_database(__ALIAS, aa.get_path("data", "molecular-constants.sqlite", module=pf), {
#         "molecule": {
#             "name": [None, "name of molecule, <i>e.g.</i>, 'OH'"],
#             "symbol_a": ["Symbol A", "symbol of first element"],
#             "symbol_b": ["Symbol B", "symbol of second element"],
#             "fe": [None, "oscillator strength"],
#             "do": [None, "dissociation constant (eV)"],
#             "am": [None, "mass of first element"],
#             "bm": [None, "mass of second element"],
#             "ua": [None, "value of partition function for first element"],
#             "ub": [None, "value of partition function for second element"],
#             "te": [None, "electronic term"],
#             "cro": [None, "delta Kronecker (0: sigma transitions; 1: non-Sigma transitions)"],
#             "s": [None, "?doc?"]
#       },
#         "state": {
#     "omega_e": ["ω<sub>e</sub>", "vibrational constant – first term (cm<sup>-1</sup>)"],
#     "omega_ex_e": ["ω<sub>e</sub>x<sub>e</sub>", "vibrational constant – second term (cm<sup>-1</sup>)"],
#     "omega_ey_e": ["ω<sub>e</sub>y<sub>e</sub>", " vibrational constant – third term (cm<sup>-1</sup>)"],
#     "B_e": ["B<sub>e</sub>", "rotational constant in equilibrium position (cm<sup>-1</sup>)"],
#     "alpha_e": ["α<sub>e</sub>", "rotational constant – first term (cm<sup>-1</sup>)"],
#     "D_e": ["D<sub>e</sub>", "centrifugal distortion constant (cm<sup>-1</sup>)"],
#     "beta_e": ["β<sub>e</sub>", "rotational constant – first term, centrifugal force (cm<sup>-1</sup>)"],
#       }
#     })
#
#
#
# def create_db():
#     conn = get_conn()
#     c = conn.cursor()
#     c.execute("""create table molecule (id integer primary key,
#                                         formula text unique,
#                                         name text,
#                                         symbol_a text,
#                                         symbol_b text,
#                                         fe real,
#                                         do real,
#                                         am real,
#                                         bm real,
#                                         ua real,
#                                         ub real,
#                                         te real,
#                                         cro real,
#                                         s real
#                                        )""")
#     # Note that it has no primary key
#     c.execute("""create table state (id integer primary key,
#                                      id_molecule integer,
#                                      State text,
#                                      T_e real,
#                                      omega_e real,
#                                      omega_ex_e real,
#                                      omega_ey_e real,
#                                      B_e real,
#                                      alpha_e real,
#                                      gamma_e real,
#                                      D_e real,
#                                      beta_e real,
#                                      r_e real,
#                                      Trans text,
#                                      nu_00 real
#                                     )""")
#
#     conn.commit()
#     conn.close()
#
#
# def populate_db():
#     conn = get_conn()
#     # TODO gather more formulae
#     formulae = ["MgH", "C2", "CN", "CH", "NH", "CO", "OH", "FeH", "TiO"]
#
#     # Uses PFANT/data/common/molecules.dat to retrieve "fe", "do", "am", etc.
#     filemol = pf.FileMolecules()
#     filemol.load(pf.get_pfant_data_path("common", "molecules.dat"))
#     bysym = dict([(tuple(m.symbols), m) for m in filemol])
#
#
#     for formula in formulae:
#         try:
#             data, _, name = pf.get_nist_webbook_constants(formula)
#
#             fe, do, am, bm, ua, ub, te, cro, s = None, None, None, None, None, None, None, None, \
#                                                  None
#
#             # Tries to retrieve "fe", "do" etc from molecules.dat
#             symbols = pf.description_to_symbols(formula)
#             if not symbols:
#                 aa.get_python_logger().warning("Formula '{}' not in internal BUILTIN_FORMULAS, "
#                     "and probably this molecule is also not in PFANT/data/common/molecules.dat".
#                     format(formula))
#
#                 symbols = ["", ""]
#             else:
#                 m = bysym.get(tuple(symbols))
#                 if m:
#                     fe = m.fe
#                     do = m.do
#                     am = m.am
#                     bm = m.bm
#                     ua = m.ua
#                     ub = m.ub
#                     te = m.te
#                     cro = m.cro
#                     s = m.s
#
#             symbols = [x.strip() for x in symbols]
#             conn.execute("insert into molecule "
#                          "(formula, name, symbol_a, symbol_b, fe, do, am, bm, ua, ub, te, cro, s) "
#                          "values (?,?,?,?,?,?,?,?,?,?,?,?,?)",
#                          (formula, name, symbols[0], symbols[1], fe, do, am, bm, ua, ub, te, cro, s))
#
#             id_molecule = conn.execute("select last_insert_rowid() as id").fetchone()["id"]
#             for state in data:
#                 # **Note** assumes that the columns in data match the
#                 # (number of columns in the state table - 2) and their order
#                 conn.execute("insert into state values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
#                              [None, id_molecule]+state)
#
#             conn.commit()
#
#         except:
#             aa.get_python_logger().exception("Failed for molecule '{}'".format(formula))
#
#     conn.close()
#
#
# def query_molecule(**kwargs):
#     """Convenience function to query 'molecule' table
#
#     Args:
#         **kwargs: filter fieldname=value pairs to be passed to WHERE clause
#
#     Returns: sqlite3 cursor
#     """
#     where = ""
#     if len(kwargs) > 0:
#         where = " where " + " and ".join([key + " = ?" for key in kwargs])
#     conn = get_conn()
#     sql = """select * from molecule{} order by formula""".format(where)
#     r = conn.execute(sql, list(kwargs.values()))
#     return r
#
#
# def query_state(**kwargs):
#     """Convenience function to query 'state' table
#
#     Args, Returns: see query_molecule
#     """
#     where = ""
#     if len(kwargs) > 0:
#         where = " where " + " and ".join([key + " = ?" for key in kwargs])
#     conn = get_conn()
#     sql = """select molecule.formula, state.* from state
#              join molecule on state.id_molecule = molecule.id{}""".format(where)
#     r = conn.execute(sql, list(kwargs.values()))
#     return r
#
#
# def test_query_state():
#     """
#     Test function
#
#     >>> conn = get_conn()
#     >>> cursor = conn.execute("select * from state where id = 10")
#     >>> row = cursor.fetchone()
#     >>> print(row)
#     MyDBRow([('id', 10), ('id_molecule', 2), ('State', 'F ⁱPi_u'), ('T_e', 75456.9), ('omega_e', 1557.5), ('omega_ex_e', None), ('omega_ey_e', None), ('B_e', 1.645), ('alpha_e', 0.019), ('gamma_e', None), ('D_e', 6e-06), ('beta_e', None), ('r_e', 1.307), ('Trans', 'F ← X R'), ('nu_00', 74532.9)])
#     """
#
#
# def print_states(**kwargs):
#     """
#     Prints states table in console
#
#     Args:
#         **kwargs: arguments passed to query_state()
#
#     >>> print_states(formula="OH")
#     """
#     r = query_state(**kwargs)
#     data, header0 = aa.cursor_to_data_header(r)
#
#     # ti = aa.get_table_info(_ALIAS, "state")
#     # header = [(ti[name]["caption"] or name) if ti.get(name) else name for name in header0]
#
#     header = header0
#
#     print(tabulate.tabulate(data, header))
