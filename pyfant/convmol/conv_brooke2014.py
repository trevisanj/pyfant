"""Molecular lines converter from Brooke2014 to PFANT format."""

__all__ = ["ConvBrooke2014"]

import a99, math
import airvacuumvald as avv
from .conv import *


class ConvBrooke2014(Conv):
    """Converts Brooke2014 [1] molecular lines data to PFANT "sets of lines"

    There is a working example conv_brooke2014_cn.py in examples directory

    References:
        [1] Brooke, James SA, et al. "Einstein a coefficients and oscillator strengths for the A2Π–X2Σ+(red)
            and B2Σ+–X2Σ+(violet) systems and rovibrational transitions in the X2Σ+ State of CN."
            The Astrophysical Journal Supplement Series 210.2 (2014): 23.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _make_sols(self, f):
        """Sets-of-lines maker for ConvBrooke2014 class

        Args:
            f: FileBrooke2014 instance
        """
        import pyfant
        assert isinstance(f, pyfant.FileBrooke2014)

        log = self.log

        log.n = len(f)
        if log.n == 0:
            raise RuntimeError("Zero lines found")

        if self.mode != ConvMode.HLF:
            deltak = self.molconsts.get_deltak()
            S2l = self.molconsts.get_S2l()

        STATEL = self.molconsts["from_label"]
        STATE2L = self.molconsts["to_label"]

        for i, line in enumerate(f.lines):
            try:
                if self.flag_filter_labels and not (line.eSl == STATEL and line.eS2l == STATE2L):
                    log.skip_reasons[f"Wrong system: {line.eSl}-{line.eS2l}"] += 1
                    continue

                vl = line.vl
                v2l = line.v2l
                Jl = line.Jl
                J2l = line.J2l
                branch = line.branch
                nu = f.nu_obs_or_calc(i)
                lambda_ = avv.vacuum_to_air(1e8/nu)

                if nu < 0:
                    log.skip_reasons["Negative wavenumber"] += 1
                    continue

                if self.mode == ConvMode.HLF:
                    sj = self.get_hlf(vl, v2l, J2l, branch)
                else:
                    A = line.A
                    sj = self.get_sj_einstein(A, Jl, J2l, S2l, deltak, nu)

                self.append_line2(vl, v2l, lambda_, sj, J2l, branch)

            except Exception as e:
                reason = a99.str_exc(e)
                log.skip_reasons[reason] += 1
                msg = "#{}{} line: {}".format(i+1, a99.ordinal_suffix(i+1), reason)
                log.errors.append(msg)
                if not self.flag_quiet:
                    a99.get_python_logger().exception(msg)


# === SAMPLES ==========================================================================================================
# hapidata["header"]
# ==============
# {'table_type': 'column-fixed',
#  'size_in_bytes': -1,
#  'table_name': '###',
#  'number_of_rows': 253695,
#  'order': ['molec_id',
#   'local_iso_id',
#   'nu',
#   'sw',
#   'a',
#   'gamma_air',
#   'gamma_self',
#   'elower',
#   'n_air',
#   'delta_air',
#   'global_upper_quanta',
#   'global_lower_quanta',
#   'local_upper_quanta',
#   'local_lower_quanta',
#   'ierr',
#   'iref',
#   'line_mixing_flag',
#   'gp',
#   'gpp'],
#  'format': {'a': '%10.3E',
#   'gamma_air': '%5.4f',
#   'gp': '%7.1f',
#   'local_iso_id': '%1d',
#   'molec_id': '%2d',
#   'sw': '%10.3E',
#   'local_lower_quanta': '%15s',
#   'local_upper_quanta': '%15s',
#   'gpp': '%7.1f',
#   'elower': '%10.4f',
#   'n_air': '%4.2f',
#   'delta_air': '%8.6f',
#   'global_upper_quanta': '%15s',
#   'iref': '%12s',
#   'line_mixing_flag': '%1s',
#   'ierr': '%6s',
#   'nu': '%12.6f',
#   'gamma_self': '%5.3f',
#   'global_lower_quanta': '%15s'},
#  'default': {'a': 0.0,
#   'gamma_air': 0.0,
#   'gp': 'FFF',
#   'local_iso_id': 0,
#   'molec_id': 0,
#   'sw': 0.0,
#   'local_lower_quanta': '000',
#   'local_upper_quanta': '000',
#   'gpp': 'FFF',
#   'elower': 0.0,
#   'n_air': 0.0,
#   'delta_air': 0.0,
#   'global_upper_quanta': '000',
#   'iref': 'EEE',
#   'line_mixing_flag': 'EEE',
#   'ierr': 'EEE',
#   'nu': 0.0,
#   'gamma_self': 0.0,
#   'global_lower_quanta': '000'},
#  'description': {'a': 'Einstein A-coefficient in s-1',
#   'gamma_air': 'Air-broadened Lorentzian half-width at half-maximum at p = 1 atm and T = 296 K',
#   'gp': 'Upper state degeneracy',
#   'local_iso_id': 'Integer ID of a particular Isotopologue, unique only to a given molecule, in order or abundance (1 = most abundant)',
#   'molec_id': 'The Brooke2014 integer ID for this molecule in all its isotopologue forms',
#   'sw': 'Line intensity, multiplied by isotopologue abundance, at T = 296 K',
#   'local_lower_quanta': 'Rotational, hyperfine and other quantum numbers and labels for the lower state of a transition',
#   'local_upper_quanta': 'Rotational, hyperfine and other quantum numbers and labels for the upper state of a transition',
#   'gpp': 'Lower state degeneracy',
#   'elower': 'Lower-state energy',
#   'n_air': 'Temperature exponent for the air-broadened HWHM',
#   'delta_air': 'Pressure shift induced by air, referred to p=1 atm',
#   'global_upper_quanta': 'Electronic and vibrational quantum numbers and labels for the upper state of a transition',
#   'iref': 'Ordered list of reference identifiers for transition parameters',
#   'line_mixing_flag': 'A flag indicating the presence of additional data and code relating to line-mixing',
#   'ierr': 'Ordered list of indices corresponding to uncertainty estimates of transition parameters',
#   'nu': 'Transition wavenumber',
#   'gamma_self': 'Self-broadened HWHM at 1 atm pressure and 296 K',
#   'global_lower_quanta': 'Electronic and vibrational quantum numbers and labels for the lower state of a transition'}}

# Sample lines, although I won't have to parse them because hapi does that
# ========================================================================
# 55    2.248764 2.700-164 8.704E-07.07970.08664763.01990.76-.000265             41             41                    R  0      457665 5 8 2 2 1 7     6.0    2.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
# 55    2.279785 6.503-162 8.685E-07.07970.08663631.47680.76-.000265             40             40                    R  0      457665 5 8 2 2 1 7     6.0    2.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
# 56    2.288013 3.667-166 9.362E-07.07970.08665317.82150.76-.000265             41             41                    R  0      457665 5 8 2 2 1 7    36.0   12.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
# 55    2.310683 1.737-159 8.638E-07.07970.08662478.03720.76-.000265             39             39                    R  0      457665 5 8 2 2 1 7     6.0    2.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
# 56    2.320259 8.961-164 9.357E-07.07970.08664183.55380.76-.000265             40             40                    R  0      457665 5 8 2 2 1 7    36.0   12.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
# 53    2.325385 1.473-164 1.002E-06.07970.08665843.01970.76-.000265             41             41                    R  0      457665 5 8 2 2 1 7     3.0    1.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
# 52    2.331616 5.471-164 1.014E-06.07970.08665930.07650.76-.000265             41             41                    R  0      457665 5 8 2 2 1 7     6.0    2.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800


#=======================================================================================================================
# (20230503) Old code from 2017, didn't delete yet, maybe todo cleanup
# """
# Brooke2014-specific conversion
#
# References:
#   [1] Rothman, Laurence S., et al. "The Brooke2014 2004 molecular spectroscopic database."
#       Journal of Quantitative Spectroscopy and Radiative Transfer 96.2 (2005): 139-204.
#   [2] extraeBrooke2014.f (First version: Jorge Melendez-Moreno, January 1999)
# """
#
# # TODO not working
#
#
# from .convlog import *
# from collections import OrderedDict
# import airvacuumvald as avv
# import pyfant
#
#
# __all__ = ["Brooke2014_to_sols"]
#
#
# _OH_BRANCH_MAP_OH = {"QQ": "Q", "PP": "P", "RR": "R"}
#
#
#
# def _parse_local_lower_quanta_OH(Q2l):
#     """
#     Parses the "Lower-state 'local' quanta" for 'OH' (see [1], Table 4, group 2, observation 'b')
#
#     Args:
#         Q2l: 15-character string containing the lower-state 'local' quanta information of molecular
#         line. Example: " PP 12.5ff     "
#
#     Returns: (Br, J2l), where
#         Br: branch ("P"/"Q"/"R")
#         J2l: inferior "quantum number associated with the total angular momentum excluding nuclear
#              spin" [1]
#
#     **Note** will raise if cannot determine Br (branch)
#     """
#     brinfo = Q2l[1:3]
#     Br = _OH_BRANCH_MAP_OH.get(brinfo)
#     if Br is None:
#         raise ValueError("Cannot derive branch from '{}' ((local lower quanta) = '{}')".
#                          format(brinfo, Q2l))
#     J2l = float(Q2l[3:8])
#     return Br, J2l
#
# def _parse_local_lower_quanta_group2(Q2l):
#     """
#     Parses the "lower-state 'local' quanta" for molecules in [1], Table 4, group 2
#
#     Args, Returns: see _parse_local_lower_quanta_OH()
#     """
#
#     Br = Q2l[5:6]
#     J2l = float(Q2l[6:9])
#     return Br, J2l
#
#
# def _parse_local_lower_quanta_group6(Q2l):
#     """[...] [1], Table 4, group 6"""
#
#     Br = Q2l[3:4]
#     J2l = float(Q2l[4:9])
#     return Br, J2l
#
#
# def _parse_global_quanta_class1(V):
#     """
#     Parses the [upper/lower] "global quanta" ([1], Table 3, class 1
#
#     Args:
#         V: 15-character string containing the 'global' quanta information of molecular
#            line. Example: "       X3/2   8"
#
#     Returns: v1: "quantum number associated with the first normal mode of vibration" [1]
#     """
#     return int(V[13:15])
#
#
# def _parse_global_quanta_class2(V):
#     """[...] [1], Table 3, class 2"""
#     return int(V[13:15])
#
# def _parse_global_quanta_class3(V):
#     return int(V[13:15])
#
#
# __GROUP_MAP = (
#     (("OH",),
#      _parse_local_lower_quanta_OH),
#     (("CO2", "N2O", "CO", "HF", "HCl", "HBr", "HI", "OCS", "N2", "HCN", "C2H2", "NO+"),
#      _parse_local_lower_quanta_group2),
#     (("NO", "ClO"),
#      _parse_local_lower_quanta_group6),
# )
# _GROUP_DICT = dict(sum([[(mol, callable_) for mol in mols] for mols, callable_ in __GROUP_MAP], []))
#
# __CLASS_MAP = (
#     (("CO", "HF", "HCl", "HBr", "HI", "N2", "NO+"), _parse_global_quanta_class1),
#     (("O2",), _parse_global_quanta_class2),
#     (("NO", "OH", "ClO"), _parse_global_quanta_class3),
# )
# _CLASS_DICT = dict(sum([[(mol, callable_) for mol in mols] for mols, callable_ in __CLASS_MAP], []))
#
#
# def Brooke2014_to_sols(molconsts, lines, qgbd_calculator):
#     """
#     Converts Brooke2014 molecular lines data to PFANT "sets of lines"
#
#     Args:
#         molconsts: a dict-like object combining field values from tables 'molecule', 'state',
#                     'pfantmol', and 'system' from a FileMolDB database
#         lines: item from rom hapi.LOCAL_TABLE_CACHE (a dictionary)
#         qgbd_calculator: callable that can calculate "qv", "gv", "bv", "dv",
#                          e.g., calc_qbdg_tio_like()
#
#     Returns: (a list of ftpyfant.SetOfLines objects, a MolConversionLog object)
#     """
#
#     def append_error(msg):
#         log.errors.append("#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), str(msg)))
#
#     # C     BAND (v',v'')=(VL,V2L)
#     # C     WN: vacuum wavenumber   WL : air wavelength
#     # C     J2L: lower state angular momentum number
#     # C     iso: isotope/ 26: 12C16O, 36: 13C16O, 27: 12C17O, 28: 12C18O
#     # C     ramo: branch, for P: ID=1, for R: ID=2
#     # C     name: file name/ coisovLv2L
#     # C     HL: Honl-London factor
#     # C     FR: oscillator strength
#
#     header = lines["header"]
#     data = lines["data"]
#
#     S = molconsts.get_S2l()
#     DELTAK = molconsts.get_deltak()
#     print(f"DELTAK = {DELTAK}")
#     sys.exit()
#     formula = molconsts["formula"]
#
#     n = header["number_of_rows"]
#     log = MolConversionLog(n)
#     sols = OrderedDict()  # one item per (vl, v2l) pair
#
#     try:
#         f_class = _CLASS_DICT[formula]
#     except KeyError:
#         log.errors.append("Cannot determine Table 3 'class' (Rothman et al. 2005) for formula '{}'".
#                           format(formula))
#         log.flag_ok = False
#
#     try:
#         f_group = _GROUP_DICT[formula]
#     except KeyError:
#         log.errors.append("Cannot determine Table 4 'group' (Rothman et al. 2005) for formula '{}'".
#                           format(formula))
#         log.flag_ok = False
#
#     if not log.flag_ok:
#         return [], log
#
#     for i in range(n):
#
#         try:
#             nu = data["nu"][i]
#             wl = avv.vacuum_to_air(1e8/nu)
#             Br, J2l = f_group(data["local_lower_quanta"][i])
#             #  ASSUMING SINGLET!!!
#             Jl = ph.singlet.quanta_to_branch(Br, J2l)
#             V = f_class(data["global_upper_quanta"][i])
#             V_ = f_class(data["global_lower_quanta"][i])
#             A = data["a"][i]
#
#             # A seguir normalizacion de factor de Honl-london (HLN)
#             Normaliza = 1/((2.0*J2l+1)*(2.0*S+1)*(2.0-DELTAK))
#
#             # A seguir teremos a forca de oscilador
#             # mas q sera normalizada segundo o programa da Beatriz
#             gf = Normaliza*1.499*(2*Jl+1)*A/(nu**2)
#
#             J2l_pfant = int(J2l)  # ojo, estamos colocando J2L-0.5! TODO ask BLB: we write J2l or J2l-.5? (20171114 I think this is wrong, molecules.dat has decimal values)
#         except Exception as e:
#             log.errors.append("#{}{} line: {}".format(i+1, a99.ordinal_suffix(i+1), a99.str_exc(e)))
#             continue
#
#         sol_key = (V, V_)  # (v', v'') transition (v_sup, v_inf)
#         if sol_key not in sols:
#             qgbd = qgbd_calculator(molconsts, sol_key[1])
#             qqv = qgbd["qv"]
#             ggv = qgbd["gv"]
#             bbv = qgbd["bv"]
#             ddv = qgbd["dv"]
#
#             sols[sol_key] = pyfant.SetOfLines(V, V_, qqv, ggv, bbv, ddv, 1.)
#         sol = sols[sol_key]
#         sol.append_line(wl, gf, J2l_pfant, Br)
#
#     return (list(sols.values()), log)
