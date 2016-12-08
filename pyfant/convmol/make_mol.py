import pyfant as pf
import datetime

__all__ = ["make_file_molecules"]


def make_file_molecules(mol_row, mol_consts, state_consts, lines, qgbd_calculator, sols_calculator):
    """

    Args:
        mol_row: MyDBRow object representing row from 'molecules' table
        mol_consts: dict-like object with keys "fe", "do", "am", "bm", "ua", "ub", "te"
        state_consts: dict-like object with keys "omega_e", etc.
        lines: molecular lines data; type/format varies depending on type of data
        qgbd_calculator: callable(state_consts, v_lo) that can calculate "qv", "gv", "bv", "dv",
                         e.g., calc_qbdg_tio_like()
        sols_calculator: callable(state_consts, lines, qgbd_calculator) that returns a list of
                         SetOfLines, e.g., hitran_to_sols()

    Returns: a FileMolecules object
    """

    sols = sols_calculator(state_consts, lines, qgbd_calculator)
    mol = _make_molecule(mol_row, mol_consts, sols)
    f = pf.FileMolecules()
    f.titm = "Created by pyfant.make_file_molecules() @ {}".format(datetime.datetime.now().isoformat())
    f.molecules = [mol]

    return f


def _make_molecule(mol_row, mol_consts, sols):
    """Assembles a Molecule object taking all necessary information

    Args:
        mol_row: MyDBRow object representing row from 'molecules' table
        mol_consts: dict-like object with keys "fe", "do", "am", "bm", "ua", "ub", "te"
        sol: pyfant.SetOfLines object

    **Note** Doesn't take take "fe", "do", etc. directly from the 'molecule' table because these
             values may have been customized by the user in widget WMolConst
    """

    mol = pf.Molecule()
    mol.description = "{name} ({formula})".format(**mol_row)
    mol.symbols = [mol_row["symbol_a"], mol_row["symbol_b"]]
    mol.fe = mol_consts["fe"]
    mol.do = mol_consts["do"]
    mol.mm = mol_consts["am"] + mol_consts["bm"]
    mol.am = mol_consts["am"]
    mol.bm = mol_consts["bm"]
    mol.ua = mol_consts["ua"]
    mol.ub = mol_consts["ub"]
    mol.te = mol_consts["te"]
    mol.cro = mol_consts["cro"]
    mol.s = mol_consts["s"]

    mol.sol = sols

    return mol