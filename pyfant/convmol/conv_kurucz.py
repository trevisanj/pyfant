"""
VALD3-specific conversion
"""


import pyfant as pf
import astroapi as aa
from .calc_qgbd import calc_qgbd_tio_like
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

    sols = {}  # one item per (vl, v2l) pair

    if not isinstance(fileobj, pf.FileKuruczMolecule):
        raise TypeError("Invalid type for argument 'fileobj': {}".format(type(fileobj).__name__))

    lines = fileobj.lines
    n = len(lines)

    # TODO: ask BLB about this S
    S = 0.5   # dubleto: X2 PI
    DELTAK = 0  # TODO ask BLB ?doc?

    log = MolConversionLog(n)

    for i, line in enumerate(lines):
        assert isinstance(line, pf.KuruczMolLine)
        try:
            wl = line.lambda_
            Normaliza = 1/((2.0*line.J2l+1)*(2.0*S+1)*(2.0-DELTAK))
            gf_pfant = Normaliza*10**line.loggf

            J2l_pfant = int(line.J2l)  # ojo, estamos colocando J2L-0.5! TODO ask BLB: we write J2l or J2l-.5?
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
