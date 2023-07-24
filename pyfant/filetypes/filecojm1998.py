"""CO linelist found in Jorge Melendez's 1998 work."""

__all__ = ["FileCOJM1998"]

import a99, math
from f311 import DataFile
from dataclasses import dataclass

@dataclass
class COJM1998Line:
    # wavenumber in cm**-1
    nu: float
    # R2 measured in Debyes**2
    D2: float
    # Einstein's A value in hertz
    A: float

    vl: int
    v2l: int
    # P/Q/R
    branch: str
    J2l: float

    # AFGL isotopologue code
    iso: int


@a99.froze_it
class FileCOJM1998(DataFile):
    """
    Linelist used in Jorge Melendez's 1998 work on CO (filename: "COdv1.dat")
    """

    def __init__(self):
        DataFile.__init__(self)
        self.lines = []

    def __len__(self):
        return len(self.lines)

# Sample from COdv1.dat
# ^^^^^^^^^^^^^^^^^^^^^
#  849.8039 2.928E-01 2.827E+01 69999.5215 1.743E-02 7.914E-33 21 20 P 149 26
#  856.6729 2.918E-01 2.886E+01 69612.2062 1.739E-02 9.572E-33 21 20 P 148 26
#  857.0984 2.876E-01 2.849E+01 68948.3033 1.727E-02 1.265E-32 21 20 P 149 27
#  862.2408 2.837E-01 2.862E+01 68159.3991 1.714E-02 1.796E-32 21 20 P 149 36
# 012345678901234567890123456789012345678901234567890123456789012345678901234
# 0         1         2         3         4         5         6         7
# nu       D2                                                  vl v2 r J2l iso

    def _do_load(self, filename):
        with open(filename, "r") as h:
            for i, s in enumerate(h):
                try:
                    line = COJM1998Line(nu=float(s[0:9]),
                                        D2=float(s[9:19]),
                                        A=float(s[19:29]),
                                        vl=int(s[60:63]),
                                        v2l=int(s[63:66]),
                                        branch=s[67],
                                        J2l=float(s[68:72]),
                                        iso=int(s[72:75]),
                                       )
                    self.lines.append(line)

                except Exception as e:
                    raise RuntimeError("Error around %d%s row of file '%s': \"%s\""%
                                       (i+1, a99.ordinal_suffix(i+1), filename, a99.str_exc(e))) from e
