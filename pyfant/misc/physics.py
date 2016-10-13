__all__ = ["symbols", "SYMBOLS", "Color", "rainbow_colors", "ncolors", "MAGNITUDE_BASE",
           "ufunc_gauss", "Band", "Bands"]


import numpy as np
import collections
from scipy.interpolate import interp1d
from .meta import *


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





########################################################################################################################
# PHOTOMETRY

MAGNITUDE_BASE = 100. ** (1. / 5)  # approx. 2.512


def ufunc_gauss(x0, fwhm):
    """Returns a Gaussian function given the x at maximum value and the fwhm. Works as a numpy ufunc

    **Note** the maximum value is 1. at x=x0

    Reference: https://en.wikipedia.org/wiki/Gaussian_function

    Test code:

      >> from pymos import *
      >> import matplotlib.pyplot as plt
      >> import numpy as np
      >> f = ufunc_gauss(0, 5.)
      >> x = np.linspace(-10, 10, 200)
      >> y = f(x)
      >> plt.plot(x, y)
      >> plt.show()
    """

    # K = 1/(2*c**2)
    # c = fwhm/(2*sqrt(2*ln(2)))
    K = 4 * np.log(2) / fwhm ** 2
    def f(x):
        return np.exp(-(x - x0) ** 2 * K)

    return f


class Band(object):
    """
    Wavelength filter band, with class tools

    This class is kept clean whereas Bands has examples and deeper documentation on parameters

    Arguments:
        tabular -- ((wl, y), ...), 0 <= y <= 1
        parametric -- ((wl, fwhm), ...)
        ref_mean_flux -- reference mean flux passing through filter at magnitude 0 in Jy units
    """
    def __init__(self, name, tabular=None, parametric=None, ref_mean_flux=None):
        self.name = name
        self.tabular = tabular
        self.parametric = parametric
        self.ref_mean_flux = ref_mean_flux

    def ufunc_band(self, flag_force_parametric):
        """Uses tabular data if available and not flag_force_parametric"""
        flag_parametric = flag_force_parametric
        if not flag_force_parametric and self.tabular:
            x, y = zip(*self.tabular)
            f = interp1d(x, y, kind='linear', bounds_error=False, fill_value=0)
        else:
            flag_parametric = True

        if flag_parametric:
            x0, fwhm = self.parametric
            f = ufunc_gauss(x0, fwhm)
        return f

    def range(self, flag_force_parametric=False, no_stds=3):
        """Returns [wl0, wl1], using edges of tabular data or given number of standard deviations"""
        flag_parametric = flag_force_parametric

        if not flag_force_parametric and self.tabular:
            points = self.tabular
            p0, pf = points[0], points[-1]
            # The following is assumed for the code to work
            assert p0[1] == 0 and pf[1] == 0, "Bands.TABULAR tables must start and end with a zero"
            ret = [p0[0], pf[0]]
        else:
            flag_parametric = True

        if flag_parametric:
            x0, fwhm = self.parametric
            std = fwhm * (1. / np.sqrt(8 * np.log(2)))
            ret = [x0 - no_stds * std, x0 + no_stds * std]
        return ret


class Bands(object):
    # Michael Bessel 1990
    # Taken from http://spiff.rit.edu/classes/phys440/lectures/filters/filters.html
    #
    # The following code should get a plot of these tabulated bands:
    #
    #   >> from pymos import *
    #   >> import matplotlib.pyplot as plt
    #   >> import numpy as np
    #   >> band_names = "UBVRI"
    #   >> colors = np.array([[139., 0, 255], [0, 0, 255], [0, 196, 0], [255, 0, 0], [128, 0, 0]], dtype=float)/255
    #   >> plt.figure()
    #   >> for color, band_name in zip(colors, band_names):
    #   >>     x, y = zip(*UBVRI[band_name])
    #   >>     plt.plot(x, y, label=band_name, c=color)
    #   >> plt.legend()
    #   >> plt.show()
    TABULAR = collections.OrderedDict((
    ("U", ((3000, 0.00),  (3050, 0.016), (3100, 0.068), (3150, 0.167), (3200, 0.287), (3250, 0.423), (3300, 0.560),
           (3350, 0.673), (3400, 0.772), (3450, 0.841), (3500, 0.905), (3550, 0.943), (3600, 0.981), (3650, 0.993),
           (3700, 1.000), (3750, 0.989), (3800, 0.916), (3850, 0.804), (3900, 0.625), (3950, 0.423), (4000, 0.238),
           (4050, 0.114), (4100, 0.051), (4150, 0.019), (4200, 0.000))),
    ("B", ((3600, 0.0), (3700, 0.030), (3800, 0.134), (3900, 0.567), (4000, 0.920), (4100, 0.978), (4200, 1.000),
           (4300, 0.978), (4400, 0.935), (4500, 0.853), (4600, 0.740), (4700, 0.640), (4800, 0.536), (4900, 0.424),
           (5000, 0.325), (5100, 0.235), (5200, 0.150), (5300, 0.095), (5400, 0.043), (5500, 0.009), (5600, 0.0))),
    ("V", ((4700, 0.000), (4800, 0.030), (4900, 0.163), (5000, 0.458), (5100, 0.780), (5200, 0.967), (5300, 1.000),
          (5400, 0.973), (5500, 0.898), (5600, 0.792), (5700, 0.684), (5800, 0.574), (5900, 0.461), (6000, 0.359),
          (6100, 0.270), (6200, 0.197), (6300, 0.135), (6400, 0.081), (6500, 0.045), (6600, 0.025), (6700, 0.017),
          (6800, 0.013), (6900, 0.009), (7000, 0.000))),
    ("R", ((5500, 0.0), (5600, 0.23), (5700, 0.74), (5800, 0.91), (5900, 0.98), (6000, 1.000), (6100, 0.98),
           (6200, 0.96), (6300, 0.93), (6400, 0.90), (6500, 0.86), (6600, 0.81), (6700, 0.78), (6800, 0.72),
           (6900, 0.67), (7000, 0.61), (7100, 0.56), (7200, 0.51), (7300, 0.46), (7400, 0.40), (7500, 0.35),
           (8000, 0.14), (8500, 0.03), (9000, 0.00))),
    ("I", ((7000, 0.000), (7100, 0.024), (7200, 0.232), (7300, 0.555), (7400, 0.785), (7500, 0.910), (7600, 0.965),
           (7700, 0.985), (7800, 0.990), (7900, 0.995), (8000, 1.000), (8100, 1.000), (8200, 0.990), (8300, 0.980),
           (8400, 0.950), (8500, 0.910), (8600, 0.860), (8700, 0.750), (8800, 0.560), (8900, 0.330), (9000, 0.150),
           (9100, 0.030), (9200, 0.000)))
    ))


    # Values taken from https://en.wikipedia.org/wiki/Photometric_system
    PARAMETRIC = collections.OrderedDict((
    ("U", (3650., 660.)),
    ("B", (4450., 940.)),
    ("V", (5510., 880.)),
    ("R", (6580., 1380.)),
    ("I", (8060., 1490.)),
    ("Y", (10200., 1200.)),
    ("J", (12200., 2130.)),
    ("H", (16300., 3070.)),
    ("K", (21900., 3900.)),
    ("L", (34500., 4720.)),
    ("M", (47500., 4600.)),
    ("N", (105000., 25000.)),
    ("Q", (210000., 58000.))
    ))

    # values taken from https://en.wikipedia.org/wiki/Apparent_magnitude, but I- and J-band values agree with
    # Evans, C.J., et al., A&A 527(2011): A50.
    REF_JY = collections.OrderedDict((
    ("U", 1810),
    ("B", 4260),
    ("V", 3640),
    ("R", 3080),
    ("I", 2550),
    ("Y", None),
    ("J", 1600),
    ("H", 1080),
    ("K", 670),
    ("L", None),
    ("M", None),
    ("N", None),
    ("Q", None),

    ))

    bands = collections.OrderedDict()
    for k in PARAMETRIC:
        bands[k] = Band(k, TABULAR.get(k), PARAMETRIC.get(k), REF_JY.get(k))

    @classmethod
    def names(cls):
        """Returns string containing all band names"""
        return "".join([x[0] for x in cls.PARAMETRIC])

    @classmethod
    def ufunc_band(cls, band_name, flag_force_parametric=False):
        """Returns a function(wavelength) for the transmission filter given the band name. Works as a numpy ufunc

        Arguments:
            band_name -- e.g. "U", "J"
            flag_force_parametric -- if set, will use parametric data even for the tabulated bands UBVRI


        Test code:
          >> from pymos import *
          >> import matplotlib.pyplot as plt
          >> import numpy as np
          >> l0, lf = 3000, 250000
          >> x =  np.logspace(np.log10(l0), np.log10(lf), 1000, base=10.)
          >> for band_name, (x0, fwhm) in Bands.PARAMETRIC.iteritems():
          >>     plt.subplot(211)
          >>     plt.semilogx(x, ufunc_band(band_name)(x), label=band_name)
          >>     plt.subplot(212)
          >>     plt.semilogx(x, ufunc_band(band_name, True)(x), label=band_name)
          >> plt.subplot(211)
          >> plt.title("Tabulated UBVRI")
          >> plt.xlim([l0, lf])
          >> plt.subplot(212)
          >> plt.title("Parametric UBVRI")
          >> plt.xlabel("Wavelength (angstrom)")
          >> plt.xlim([l0, lf])
          >> l = plt.legend(loc='lower right')
          >> plt.tight_layout()
          >> plt.show()
        """
        return cls.bands[band_name].ufunc_band(flag_force_parametric)

    @classmethod
    def range(cls, band_name, flag_force_parametric=False, no_stds=3):
        """Returns wavelength range beyond which the transmission function value is zero or negligible

        **Note**

        Arguments:
            band_name -- e.g. "U", "J"
            flag_force_parametric -- if set, will use parametric data even for the tabulated bands UBVRI
            no_stds -- number of standard deviations away from center to consider the range limit (parametric cases only).
                       At 3 standard deviations from the center the value drops to approximately 1.1% of the maximum
        """

        return cls.bands[band_name].range(flag_force_parametric, no_stds)
