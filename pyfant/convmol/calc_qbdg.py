"""
Transition-specific calculations

References:
  [1] agrup.plez7.f
"""

from collections import OrderedDict
from . import moldb as db


def calc_transition_tio_like(mol_consts, v_lo):
    """
    Calculates qv, gv, bv, dv in TiO-like fashion

    Based on Fortran source 'agrup.plez7.f'

    Args:
        mol_consts -- dict-like object with keys:
            "omega_e"
            "omega_ex_e"
            "omega_ey_e"
            "B_e"
            "alpha_e"
            "D_e"
            "beta_e"

        v_lo -- (integer) low transition level

    Returns: qbdg, i.e., a dictionary with keys:
            "qv", "gv", "bv", "dv", "gzero"

    >>> state_row = db.StateRow(108)
    >>> state_row.None_to_zero()
    >>> calc_transition_tio_like(state_row, 10)
    OrderedDict([('qv', 1.0), ('bv', 0.5063099999999999), ('dv', 5900000.0), ('gv', 9664.0), ('gzero', 503.67499999999995)])
    """

    omega_e = mol_consts["omega_e"]
    omega_ex_e = mol_consts["omega_ex_e"]
    omega_ey_e = mol_consts["omega_ey_e"]
    B_e = mol_consts["B_e"]
    D_e = mol_consts["D_e"]
    alpha_e = mol_consts["alpha_e"]
    beta_e = mol_consts["beta_e"]

    if int(v_lo) != v_lo:
        raise ValueError("Argument 'v_lo' must be an integer")

    gzero = omega_e / 2.0 - omega_ex_e / 4.0 + omega_ey_e / 8.0
    v_lo5 = v_lo + 0.5

    # Franck-Condon factor
    # TODO: calculate the Franck-Condon factor
    qv = 1.
    # rotational constant "B_v"
    bv = B_e - alpha_e * v_lo5
    # rotational constant "D_v"
    dv = (D_e + beta_e * v_lo5) * 1.0e+06
    # rotational term " G_A"
    gv = omega_e * v_lo5 - omega_ex_e * v_lo5 ** 2 + omega_ey_e * v_lo5 ** 3 - gzero

    qbdg = OrderedDict((("qv", qv), ("gv", gv), ("bv", bv), ("dv", dv), ("gzero", gzero)))

    return qbdg

