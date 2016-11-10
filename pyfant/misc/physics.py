__all__ = ["symbols", "SYMBOLS", "Color", "rainbow_colors", "ncolors", "C", "H"]


import numpy as np
import collections
from scipy.interpolate import interp1d
from .parts import *


# All values in CGS
class LightSpeed(float):
    "Light speed in cm/s (CGS) units"

class Planck(float):
    """Planck's constant in cm**2*g/s"""

C = LightSpeed(299792458. * 100)
H = Planck(6.6261e-27)

# List of all atomic symbols
# obtained using elements.py from http://www.lfd.uci.edu/~gohlke/, then
# > import elements
# > [x.symbol for x in ELEMENTS]
symbols = [
'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si',
 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co',
 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr',
 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I',
 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy',
 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au',
 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U',
 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db',
 'Sg', 'Bh', 'Hs', 'Mt'
]
# List of all atomic symbols in UPPERCASE
SYMBOLS = [x.upper() for x in symbols]


###############################################################################
# # RAINBOW

class Color(AttrsPart):
    attrs = ["name", "rgb", "clambda", "l0", "lf"]
    def __init__(self, name, rgb, clambda):
        AttrsPart.__init__(self)
        self.name = name
        self.rgb = rgb
        self.clambda = clambda
        self.l0 = -1.  # initialized later
        self.lf = -1.
    def __repr__(self):
        return '"%s"' % self.one_liner_str()
        # return ", ".join(["%s: %s" % (name, self.__getattribute__(name)) for name in ["name", "rgb", "clambda", "l0", "lf"]])


rainbow_colors = [Color("Violet", [139, 0, 255], 4000),
                  Color("Indigo", [75, 0, 130], 4450),
                  Color("Blue", [0, 0, 255], 4750),
                  Color("Green(X11)", [0, 255, 0], 5100),
                  Color("Yellow", [255, 255, 0], 5700),
                  Color("Orange", [255, 127, 0], 5900),
                  Color("Red", [255, 0, 0], 6500),
                  ]

# Calculates l0, lf
# rainbow_colors[0].l0 = 0.
# rainbow_colors[-1].lf = float("inf")
for c in rainbow_colors:
    c.clambda = float(c.clambda)
ncolors = len(rainbow_colors)
for i in range(1, ncolors):
    cprev, cnow = rainbow_colors[i-1], rainbow_colors[i]
    avg = (cprev.clambda + cnow.clambda) / 2
    cprev.lf = avg
    cnow.l0 = avg

    if i == 1:
        cprev.l0 = 2*cprev.clambda-cprev.lf
    if i == ncolors-1:
        cnow.lf = 2*cnow.clambda-cnow.l0
# converts RGB from [0, 255] to [0, 1.] interval
for c in rainbow_colors:
    c.rgb = np.array([float(x)/255 for x in c.rgb])


