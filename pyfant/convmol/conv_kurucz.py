"""
VALD3-specific conversion
"""


import pyfant as pf
import astroapi as aa
from .convlog import *
from .branch import *
from collections import OrderedDict


__all__ = ["kurucz_to_sols"]



def kurucz_to_sols(mol_row, state_row, fileobj, qgbd_calculator):
    """
    Converts Kurucz molecular lines data to PFANT "sets of lines"

    Args:
        mol_row: dict-like,
                 molecule-wide constants,
                 keys: same as as field names in 'moldb:molecule' table
        state_row: dict-like,
                   state-wide constants,
                   keys: same as field names in 'moldb:state' table
        fileobj: FileVald3 instance with only one species
        qgbd_calculator: callable that can calculate "qv", "gv", "bv", "dv",
                         e.g., calc_qbdg_tio_like()

    Returns: (a list of pyfant.SetOfLines objects, a MolConversionLog object)
    """

    def append_error(msg):
        log.errors.append("#{}{} line: {}".format(i + 1, aa.ordinal_suffix(i + 1), str(msg)))

    # C     BAND (v',v'')=(VL,V2L)
    # C     WN: vacuum wavenumber   WL : air wavelength
    # C     J2L: lower state angular momentum number
    # C     iso: isotope/ 26: 12C16O, 36: 13C16O, 27: 12C17O, 28: 12C18O
    # C     ramo: branch, for P: ID=1, for R: ID=2
    # C     name: file name/ coisovLv2L
    # C     HL: Honl-London factor
    # C     FR: oscillator strength


    if not isinstance(fileobj, pf.FileKuruczMolecule):
        raise TypeError("Invalid type for argument 'fileobj': {}".format(type(fileobj).__name__))

    lines = fileobj.lines
    n = len(lines)

    S = mol_row["s"]
    DELTAK = mol_row["cro"]

    sols = OrderedDict()  # one item per (vl, v2l) pair
    log = MolConversionLog(n)


    # This factor allows to reproduce the Hônl-London factors in `moleculagrade.dat` for OH blue,
    # first set-of-lines
    scale_factor = 730.485807466

    for i, line in enumerate(lines):
        assert isinstance(line, pf.KuruczMolLine)
        try:
            wl = line.lambda_

            # s_now = line.spin2l
            s_now = S

#            Normaliza = 1/((2.0*line.J2l+1)*(2.0*S+1)*(2.0-DELTAK))
            Normaliza = scale_factor * 1 / ((2.0*line.J2l+1)*(2.0*s_now+1)*(2.0-DELTAK))
            gf_pfant = Normaliza*10**line.loggf

            J2l_pfant = line.J2l
        except Exception as e:
            log.errors.append("#{}{} line: {}".format(i+1, aa.ordinal_suffix(i+1), str(e)))
            continue

        sol_key = "%3d%3d" % (line.vl, line.v2l)  # (v', v'') transition (v_sup, v_inf)
        if sol_key not in sols:
            qgbd = qgbd_calculator(state_row, line.v2l)
            qqv = qgbd["qv"]
            ggv = qgbd["gv"]
            bbv = qgbd["bv"]
            ddv = qgbd["dv"]
            sols[sol_key] = pf.SetOfLines(line.vl, line.v2l, qqv, ggv, bbv, ddv, 1.)

        sol = sols[sol_key]
        sol.append_line(wl, gf_pfant, J2l_pfant, global_quanta_to_branch(line.Jl, line.J2l))

    return (list(sols.values()), log)
