"""
HITRAN-specific conversion

References:
  [1] Rothman, Laurence S., et al. "The HITRAN 2004 molecular spectroscopic database."
      Journal of Quantitative Spectroscopy and Radiative Transfer 96.2 (2005): 139-204.
  [2] extraehitran.f (First version: Jorge Melendez-Moreno, January 1999)
"""


import pyfant as pf
import astroapi as aa
from .calc_qgbd import calc_qgbd_tio_like

__all__ = ["hitran_to_sols"]


_OH_BRANCH_MAP = {"QQ": "Q", "PP": "P", "RR": "R"}
_J2L_MAP = {"P": -1, "Q": 0, "R": 1}


def translate_local_lower_quanta(Q2l):
    """
    Translates the "Lower-state 'local' quanta" information to a dictionary
    Args:
        Q2l: 15-character string containing the lower-state 'local' quanta information of molecular
        line. Example: " PP 12.5ff     "

    Returns: dictionary with some of the following keys:
        "Br": branch (P/Q/R/None)
        "J2l": quantum number associated with the total angular momentum excluding nuclear spin [1]
        "Jl": J2l + (-1 (P), 0 (Q), +1 (R), or None) depending on the branch
    """

    if not isinstance(Q2l, str):
        raise TypeError("Q2l must be a string")
    if len(Q2l) != 15:
        raise ValueError("len(Q2l) must be 15")

    # At the moment, does it for OH only

    ret = {}
    if True:
        ret["Br"] = _OH_BRANCH_MAP.get(Q2l[1:3])
        if ret["Br"] is None:
            print("VAI DA MERDA")
        ret["J2l"] = float(Q2l[3:8])
        ret["Jl"] = ret["J2l"]+_J2L_MAP.get(ret["Br"])
    else:
        raise RuntimeError("TODO: implement other molecular groups as in [1] (Rothman et al. 2005), Table 4")

    return ret


def translate_global_quanta(V):
    """
    Translates the [upper/lower] "'global' quanta" information to a dictionary
    Args:
        V: 15-character string containing the 'global' quanta information of molecular
        line. Example: "       X3/2   8"

    Returns: dictionary with some of the following keys:
        "v1": quantum number associated with the first normal mode of vibration
    """

    if not isinstance(V, str):
        raise TypeError("V must be a string")
    if len(V) != 15:
        raise ValueError("len(V) must be 15")

    # At the moment, does it for OH only

    ret = {}
    if True:
        ret["v1"] = int(V[13:15])
    else:
        raise RuntimeError("TODO: implement other molecular classes as in [1] (Rothman et al. 2005), Table 3")

    return ret


def hitran_to_sols(state_consts, lines, qgbd_calculator):
    """
    Converts HITRAN molecular lines data to PFANT "sets of lines"

    Args:
        state_consts: state-wide constants, i.e., dict-like with keys "omega_e", etc.
                      (see calc_qbdg_tio_like())
        lines: item from rom hapi.LOCAL_TABLE_CACHE (a dictionary)
        qgbd_calculator: callable that can calculate "qv", "gv", "bv", "dv",
                         e.g., calc_qbdg_tio_like()

    Returns: a list of pyfant.SetOfLines objects
    """

    # C     BAND (v',v'')=(VL,V2L)
    # C     WN: vacuum wavenumber   WL : air wavelength
    # C     J2L: lower state angular momentum number
    # C     iso: isotope/ 26: 12C16O, 36: 13C16O, 27: 12C17O, 28: 12C18O
    # C     ramo: branch, for P: ID=1, for R: ID=2
    # C     name: file name/ coisovLv2L
    # C     HL: Honl-London factor
    # C     FR: oscillator strength

    sols = {}  # one item per (vl, v2l) pair

    header = lines["header"]
    data = lines["data"]

    # TODO: find this S
    S = 0.5   # dubleto: X2 PI
    DELTAK = 0  # TODO ask BLB ?doc?


    for i in range(header["number_of_rows"]):
        nu = data["nu"][i]
        wl = aa.vacuum_to_air(1e8/nu)
        Q_ = translate_local_lower_quanta(data["local_lower_quanta"][i])
        V = translate_global_quanta(data["global_upper_quanta"][i])
        V_ = translate_global_quanta(data["global_lower_quanta"][i])
        A = data["a"][i]
        Jl = Q_["Jl"]
        J2l = Q_["J2l"]

        # A seguir normalizacion de factor de Honl-london (HLN)
        # TODO ask BLB: is this formula always like this?
        Normaliza = 1/((2.0*J2l+1)*(2.0*S+1)*(2.0-DELTAK))

        # A seguir teremos a forca de oscilador
        # mas q sera normalizada segundo o programa da Beatriz
        # TODO ask BLB: what we call the Honl-London factor, he calls the "forca de oscilador"
        gf = Normaliza*1.499*(2*Jl+1)*A/(nu**2)

        J2l_pfant = int(J2l)  # ojo, estamos colocando J2L-0.5! TODO ask BLB: we write J2l or J2l-.5?

        sol_key = (V["v1"], V_["v1"])  # (v', v'') transition (v_sup, v_inf)
        if sol_key not in sols:
            qgbd = qgbd_calculator(state_consts, sol_key[1])
            qqv = qgbd["qv"]
            ggv = qgbd["gv"]
            bbv = qgbd["bv"]
            ddv = qgbd["dv"]

            sols[sol_key] = pf.SetOfLines(V["v1"], V_["v1"], qqv, ggv, bbv, ddv, 1.)
        sol = sols[sol_key]
        sol.append_line(wl, gf, J2l_pfant, Q_["Br"])

    return list(sols.values())
