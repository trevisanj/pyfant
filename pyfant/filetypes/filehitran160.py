"""Parses Brooke 2014 molecular line list"""

__all__ = ["FileHITRAN160", "FileHITRANHITRAN", "FileHITRANLi2015"]

import a99, math
from f311 import DataFile
from dataclasses import dataclass

@dataclass
class HITRANLine:
    # HITRAN's molecule ID
    molid: int
    # HITRAN's isotopologue from website (e.g. https://hitran.org/lbl/2?13=on for OH)
    iso: int
    # wavenumber in cm**-1
    nu: float
    # Einstein's A value in hertz
    A: float
    # "upper state degeneracy"
    gp: float
    # "lower state degeneracy"
    gpp: float
    # HITRAN sees these fields as strings of length=15; contents vary
    global_upper_quanta: str
    global_lower_quanta: str
    local_upper_quanta: str
    local_lower_quanta: str

    # -- The following fields are calculated depending on specific case (FileHITRANHITRAN or FileLi2015)
    # None, "A", "X" etc.
    from_label: str = ""
    to_label: str = ""
    vl: int = 0
    v2l: int = 0
    J2l: float = 0.
    # branch may be 1 letter or 2 letters
    branch: str = ""

    Jl: float = None

@a99.froze_it
class FileHITRAN160(DataFile):
    """
    HITRAN 160-column format

    Note: there was the HAPI, but I stopped trusting it at some point
    """

    def __init__(self):
        DataFile.__init__(self)
        self.lines = []

    def __len__(self):
        return len(self.lines)

# Sample from HITRAN
# ^^^^^^^^^^^^^^^^^^
# 131 5848.223534 9.192E-34 6.055E+00.04000.300 6801.82000.660.000000       X1/2   2       X1/2   0                PP 18.5ff     342210 6 5 2 1 1 0    72.0   76.0
# 131 5848.489474 7.562E-48 4.351E-02.04000.30012357.09930.660.000000       X1/2   5       X3/2   3                QP 11.5ff     232210 6 5 2 1 1 0    44.0   48.0
# 131 5848.657485 4.335E-66 4.910E-03.04000.30020661.79410.660.000000       X1/2   7       X3/2   5                SR 17.5ff     232210 6 5 2 1 1 0    76.0   72.0
# 131 5848.692924 5.023E-71 4.508E+01.04000.30024671.80250.660.000000       X3/2  11       X3/2   8                PP  7.5ee     232210 6 5 2 1 1 0    28.0   32.0
# 131 5849.160116 3.465E-38 7.934E-02.04000.300 7741.97060.660.000000       X3/2   4       X1/2   2                OP  5.5ee     232210 6 5 2 1 1 0    20.0   24.0
# 0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
# 0         1         2         3         4         5         6         7         8         9        10        11        12        13        14        15

# Sample from Li 2015
# ^^^^^^^^^^^^^^^^^^
#  55    2.248764 2.700-164 8.704E-07.07970.08664763.01990.76-.000265             41             41                    R  0      457665 5 8 2 2 1 7     6.0    2.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
#  55    2.279785 6.503-162 8.685E-07.07970.08663631.47680.76-.000265             40             40                    R  0      457665 5 8 2 2 1 7     6.0    2.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
#  56    2.288013 3.667-166 9.362E-07.07970.08665317.82150.76-.000265             41             41                    R  0      457665 5 8 2 2 1 7    36.0   12.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
# 0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
# 0         1         2         3         4         5         6         7         8         9        10        11        12        13        14        15

    def _process_further(self, line):
        raise NotImplementedError()

    def _do_load(self, filename):
        def make_label(s):
            s = s.strip()
            if not s: return None
            return s

        with open(filename, "r") as h:
            for i, s in enumerate(h):
                try:
                    line = HITRANLine(molid=int(s[0:2]),
                                      iso=int(s[2]),
                                      nu=float(s[3:15]),
                                      A=float(s[25:35]),
                                      global_upper_quanta=s[67:82],
                                      global_lower_quanta=s[82:97],
                                      local_upper_quanta=s[97:112],
                                      local_lower_quanta=s[112:127],
                                      gp=float(s[145:153]),
                                      gpp=float(s[153:160]), )
                    self.lines.append(line)

                    self._process_further(line)

                except Exception as e:
                    raise RuntimeError("Error around %d%s row of file '%s': \"%s\""%
                                       (i+1, a99.ordinal_suffix(i+1), filename, a99.str_exc(e))) from e

class FileHITRANHITRAN(FileHITRAN160):
    """
    HITRAN main database file (not HITEMP)
    """

    def _process_further(self, line):
        # "       X3/2   4"      "       X1/2   2"      "               "      " OP  5.5ee     "
        #  012345678901234        012345678901234        012345678901234        012345678901234
        #  global_upper_quanta    global_lower_quanta    local_upper_quanta     local_lower_quanta
        q = line.global_upper_quanta
        line.from_label = q[7]
        line.vl = int(q[11:15])

        q = line.global_lower_quanta
        line.to_label = q[7]
        line.v2l = int(q[11:15])

        q = line.local_lower_quanta
        line.branch = q[1:3]
        line.J2l = float(q[3:8])

class FileHITRANLi2015(FileHITRAN160):
    def _process_further(self, line):
        # "             41"      "             41"      "               "      "     R  0      "
        #  012345678901234        012345678901234        012345678901234        012345678901234
        #  global_upper_quanta    global_lower_quanta    local_upper_quanta     local_lower_quanta
        q = line.global_upper_quanta
        line.vl = int(q[11:15])

        q = line.global_lower_quanta
        line.v2l = int(q[11:15])

        q = line.local_lower_quanta
        line.branch = q[5]




# === SAMPLE ===========================================================================================================
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
#  55    2.248764 2.700-164 8.704E-07.07970.08664763.01990.76-.000265             41             41                    R  0      457665 5 8 2 2 1 7     6.0    2.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
#  55    2.279785 6.503-162 8.685E-07.07970.08663631.47680.76-.000265             40             40                    R  0      457665 5 8 2 2 1 7     6.0    2.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
#  56    2.288013 3.667-166 9.362E-07.07970.08665317.82150.76-.000265             41             41                    R  0      457665 5 8 2 2 1 7    36.0   12.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
#  55    2.310683 1.737-159 8.638E-07.07970.08662478.03720.76-.000265             39             39                    R  0      457665 5 8 2 2 1 7     6.0    2.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
#  56    2.320259 8.961-164 9.357E-07.07970.08664183.55380.76-.000265             40             40                    R  0      457665 5 8 2 2 1 7    36.0   12.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
#  53    2.325385 1.473-164 1.002E-06.07970.08665843.01970.76-.000265             41             41                    R  0      457665 5 8 2 2 1 7     3.0    1.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
#  52    2.331616 5.471-164 1.014E-06.07970.08665930.07650.76-.000265             41             41                    R  0      457665 5 8 2 2 1 7     6.0    2.0 0.0778 0.671 0.000180 0.1037 0.780 -.000800
# 0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
# 0         1         2         3         4         5         6         7         8         9        10        11        12        13        14        15
