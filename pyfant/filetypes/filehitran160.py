"""Parses Brooke 2014 molecular line list"""

__all__ = ["FileHITRAN160"]

import a99, math
from f311 import DataFile


@a99.froze_it
class FileHITRAN160(DataFile):
    """
    HITRAN 160-column format

    Note: there was the HAPI, but I stopped trusting it at some point
    """

    def __init__(self):
        DataFile.__init__(self)

        self.molid = []  # (int) HITRAN's molecule ID
        self.iso = []  # (int) HITRAN's isotopologue from website (e.g. https://hitran.org/lbl/2?13=on for OH)
        self.from_label = []  # None, "A", "X" etc.
        self.to_label = []  # "
        self.nu = []  # (float) wavenumber in cm**-1
        self.vl = []  # (int)
        self.v2l = []  # (int)
        self.J2l = []  # (float)
        self.A = []  # (float) Einstein's A value
        self.branch = []  # two letters, e.g. "PP", "QP", "SR", "PP", "OP"

    def __len__(self):
        return len(self.molid)

# 131 5848.223534 9.192E-34 6.055E+00.04000.300 6801.82000.660.000000       X1/2   2       X1/2   0                PP 18.5ff     342210 6 5 2 1 1 0    72.0   76.0
# 131 5848.489474 7.562E-48 4.351E-02.04000.30012357.09930.660.000000       X1/2   5       X3/2   3                QP 11.5ff     232210 6 5 2 1 1 0    44.0   48.0
# 131 5848.657485 4.335E-66 4.910E-03.04000.30020661.79410.660.000000       X1/2   7       X3/2   5                SR 17.5ff     232210 6 5 2 1 1 0    76.0   72.0
# 131 5848.692924 5.023E-71 4.508E+01.04000.30024671.80250.660.000000       X3/2  11       X3/2   8                PP  7.5ee     232210 6 5 2 1 1 0    28.0   32.0
# 131 5849.160116 3.465E-38 7.934E-02.04000.300 7741.97060.660.000000       X3/2   4       X1/2   2                OP  5.5ee     232210 6 5 2 1 1 0    20.0   24.0
# 0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789
# 0         1         2         3         4         5         6         7         8         9        10        11        12        13        14        15


    def _do_load(self, filename):
        def make_label(s):
            s = s.strip()
            if not s: return None
            return s

        with open(filename, "r") as h:
            for i, line in enumerate(h):
                try:
                    self.molid.append(int(line[0:2]))
                    self.iso.append(int(line[2]))
                    self.from_label.append(make_label(line[67:75]))
                    self.to_label.append(make_label(line[82:90]))
                    self.nu.append(float(line[3:15]))
                    self.vl.append(int(line[78:82]))
                    self.v2l.append(int(line[93:97]))
                    self.J2l.append(float(line[115:120]))
                    self.A.append(float(line[25:35]))
                    self.branch.append(line[113:115])


                except Exception as e:
                    raise RuntimeError("Error around %d%s row of file '%s': \"%s\""%
                                       (i+1, a99.ordinal_suffix(i+1), filename, a99.str_exc(e))) from e

