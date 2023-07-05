"""Molecular lines converter from HITRAN to PFANT format."""

__all__ = ["ConvHITRAN"]

import a99, airvacuumvald as avv, sys
from . import Conv

class ConvHITRAN(Conv):
    """Converts HITRAN molecular lines data to PFANT "sets of lines" using Einstein's coefficients

    Args:
        isowant: (=1) isotopologue ID according to HITRAN or literature e.g. [1]. Li et al. 2015 didn't follow
                 HITRAN's isotopologues codes for CO

    There is a working example conv_hitran_co.py in examples directory

    References:
        [1] Li, G., Gordon, I.E., Rothman, L.S., Tan, Y., Hu, S.M., Kassi, S., Campargue, A. and Medvedev, E.S., 2015.
        Rovibrational line lists for nine isotopologues of the CO molecule in the X1Σ+ ground electronic state.
        The Astrophysical Journal Supplement Series, 216(1), p.15.

        [2] Plez's conversor translate_molec_linelists_v16.1.f

        [3] Jorge Melendez's work on OH: extraehitran.f
    """

    def __init__(self, *args, isowant=1, **kwargs):
        super().__init__(*args, **kwargs)
        if not (1 <= isowant <= 9):
            raise ValueError(f"Invalid 'isowant': {isowant} (must be between 1 and 9)")
        self.isowant = isowant

    def _make_sols(self, f):
        """Sets-of-lines maker for ConvHITRAN class

        Args:
            f: FileHITRAN160 instance
        """
        import pyfant
        assert isinstance(f, pyfant.FileHITRAN160)

        log = self.log
        sols = self.sols

        n = log.n = len(f)
        if n == 0:
            raise RuntimeError("Zero lines found")

        deltak = self.molconsts.get_deltak()
        S2l = self.molconsts.get_S2l()

        has_label = bool(f.from_label[0])
        if self.flag_filter_labels and not has_label:
            raise RuntimeError(f"Cannot filter labels (flag_filter_labels==True), as labels (e.g. \"A\", \"X\") "
                               f"are not provided by input data")

        if self.flag_filter_labels:
            ref_from_label = self.molconsts["from_label"]
            ref_to_label = self.molconsts["to_label"]

        for i in range(n):
            try:
                if f.iso[i] != self.isowant:
                    log.skip_reasons[f"isotopologue {f.iso[i]}"] += 1
                    continue

                if self.flag_filter_labels:
                    if f.from_label[i] != ref_from_label or f.to_label[i] != ref_to_label:
                        log.skip_reasons[f"Wrong system: {f.from_label[i]}-{f.to_label[i]}"] += 1
                        continue

                vl = f.vl[i]
                v2l = f.v2l[i]
                A = f.A[i]
                nu = f.nu[i]
                J2l = f.J2l[i]


                branch = f.branch[i]  # two letters, e.g. "PP", "QP", "SR", "PP", "OP"

                # The following code was based on Jorge Melendez's extraehitran.f
                # HITRAN does not have Jl
                if branch == "PP":
                    Jl = J2l-1
                elif branch == "QQ":
                    Jl = J2l
                elif branch == "RR":
                    Jl = J2l+1
                else:
                    log.skip_reasons[f"Unhandled branch: {branch}"] += 1
                    continue

                lambda_ = avv.vacuum_to_air(1e8/f.nu[i])

                LLLLL = 15387.0527
                if abs(lambda_-LLLLL) < .01:
                    print(f"LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL {lambda_}!!!!!!!!!!!!!!!!!!!")
                    print(f"nu = {nu}; A={A}; Jl={Jl}; J2l={J2l}")
                    # sys.exit()

                SJ = self.get_sj_einstein(A, Jl, J2l, S2l, deltak, nu, self.strengthfactor)

                LLLLL = 15387.0527
                if abs(lambda_-LLLLL) < .01:
                    print(f"LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL {lambda_}!!!!!!!!!!!!!!!!!!!")
                    print(f"nu = {nu}; A={A}; Jl={Jl}; J2l={J2l}")
                    # sys.exit()

            except Exception as e:
                reason = a99.str_exc(e)
                log.skip_reasons[reason] += 1
                msg = "#{}{} line: {}".format(i+1, a99.ordinal_suffix(i+1), reason)
                log.errors.append(msg)
                if not self.flag_quiet:
                    a99.get_python_logger().exception(msg)
                continue
            else:
                # Note: skipping the branch altogether: PFANT does not care really
                sols.append_line2(vl, v2l, lambda_, SJ, J2l, branch)
                log.cnt_in += 1


        return sols, log


def parse_quanta(quanta):
    """Tries to extract 4 fields from strings in v

    Args:
        quanta: array of strings

    Returns:
        (label, v): (str, int) arrays
    """

    # Examples of strings to be parsed:
    # "             40"
    # "       X3/2  10"
    #         -   ----
    #         |      |
    #         label  v
    #  012345678901234
    label, mult, spds, v = [], [], [], []
    for s in quanta:
        _label, _v = s[7].strip(), int(s[11:])
        label.append(_label)
        v.append(_v)

    return label, v

def parse_iref(iref):
    """Tries to extract J2l from the "iref" field
a
ssdakfdshsfdkjhfds kjfhds k
    """

    # Example:
    # KDSAJHFDSKJHFSDKJHFDSKJ
    label, mult, spds, v = [], [], [], []
    for s in quanta:
        _label, _v = s[7].strip(), int(s[11:])
        label.append(_label)
        v.append(_v)

    return label, v






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
#   'molec_id': 'The HITRAN integer ID for this molecule in all its isotopologue forms',
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


