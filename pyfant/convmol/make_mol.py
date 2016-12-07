import pyfant as pf
from . import moldb as db


def make_molecule(formula, mol_const, sol):
    """Assembles a Molecule object taking all necessary information

    Args:
        formula: formula as in field 'molecules.formula' of SQLite database
        mol_const: dict-like object with keys "fe", "do", "am", "bm", "ua", "ub", "te"
        sol: pyfant.SetOfLines object

    **Note** Doesn't take take "fe", "do", etc. directly from the 'molecule' table because these
             values may have been customized by the user in widget WMolConst
    """

    row = db.query_molecules(formula=formula)

    mol = pf.Molecule()
    mol.description = "{name} ({formula})".format(**row)
    mol.symbols = [row["symbol_a", "symbol_b"]]
    mol.fe = mol_const["fe"]
    mol.do = mol_const["do"]
    mol.mm = mol_const["mm"]
    mol.am = mol_const["am"]
    mol.bm = mol_const["bm"]
    mol.ua = mol_const["ua"]
    mol.ub = mol_const["ub"]
    mol.te = mol_const["te"]
    mol.cro = row["cro"]
    mol.s = row["s"]

    mol.sol = [sol]

    return mol