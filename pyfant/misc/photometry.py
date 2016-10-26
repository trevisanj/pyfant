"""

>>> import matplotlib.pyplot as plt
>>> import numpy as np
>>> l0, lf = 3000, 250000
>>> x =  np.logspace(np.log10(l0), np.log10(lf), 1000, base=10.)
>>> for name in bands_standard:
>>>     band = bands_standard[name]
>>>     plt.subplot(211)
>>>     plt.semilogx(x, band.ufunc()(x), label=band.name)
>>>     plt.subplot(212)
>>>     plt.semilogx(x, band.ufunc(True)(x), label=band.name)
>>> plt.subplot(211)
>>> plt.title("Tabulated UBVRI")
>>> plt.xlim([l0, lf])
>>> plt.subplot(212)
>>> plt.title("Parametric UBVRI")
>>> plt.xlabel("Wavelength ($\AA$)")
>>> plt.xlim([l0, lf])
>>> l = plt.legend(loc='lower right')
>>> plt.tight_layout()
>>> plt.show()

"""


__all__ = ["Bandpass", "bands_standard"]


import numpy as np
import collections
from scipy.interpolate import interp1d
from pyfant import Spectrum


MAGNITUDE_BASE = 100. ** (1. / 5)  # approx. 2.512
REF_NUM_POINTS = 2000   # number of evaluation points over entire band range



def calculate_magnitude(x, y, band, system="stdref", zeropoint=0.):
    """
    Calculates magnitude

    Arguments:
        x -- wavelength vector (angstrom)
        y -- flux vector erg/cm**2/s/Hz aka "Fnu"
        band -- string (standard band name such as U/B/V/R/I), or Bandpass object
        system -- reference magnitude system. Choices:
            "stdref" -- literature reference values for bands U,B,V,R,I,J,H,K only
            "vega" -- uses the Vega star spectrum as a reference
            "ab" -- AB[solute] magnitude system
        zeropoint -- subtracts this value from the calculated magnitude to implement some desired
                     correction.
    """


class Bandpass(object):
    """
    Wavelength filter band, with class tools

    This class is kept clean whereas UBVRIBands has examples and deeper documentation on parameters

    Arguments:
        tabular -- ((wl, y), ...), 0 <= y <= 1
        parametric -- ((wl, fwhm), ...)
        ref_mean_flux -- reference mean flux passing through filter at magnitude 0 in Jy units
    """

    @property
    def l0(self):
        return self._get_l0()

    @property
    def lf(self):
        return self._get_lf()

    def __init__(self, name, tabular=None, parametric=None, ref_mean_flux=None):
        self.name = name
        self.tabular = tabular
        self.parametric = parametric
        self.ref_mean_flux = ref_mean_flux


    def __repr__(self):
        return "Bandpass('%s', %s, %s, %s)" % (self.name, self.tabular, self.parametric, self.ref_mean_flux)


    def __mul__(self, other):
        raise TypeError("Bandpass left multiplication not defined")


    def __rmul__(self, other):
        """Multiplies with Spectrum object. Returns new Spectrum"""
        if not isinstance(other, Spectrum):
            try:
                descr = other.__class__.__name__
            except:
                descr = str(other)
            raise TypeError("Multiplication by a Bandpass is online defined by left argument of "
                            "class Spectrum, but a %s was found" % descr)


        out = copy.deepcopy(other)

        l0, lf = max(self.l0, out.l0), min(self.lf, out.lf)
        mask = np.logical_and(out.x >= l0, out.x <= lf)
        out.y[mask] =
        band_f = self.ufunc()

            outspc.cut(band_l0, band_lf)
        else:
            spc = self
        band_f_spc_x = band_f(spc.x)
        out_y = spc.y * band_f_spc_x

        # Calculates the area under the band filter
        band_area = self.area(*([band_l0, band_lf]
                              if flag_always_full_band else [spc.x[0], spc.x[-1]]),
                              flag_force_parametric=flag_force_parametric)

        ref_mean_flux = None

        # Calculates apparent magnitude and filtered flux area
        cmag, weighted_mean_flux, out_area = None, 0, 0
        if self.ref_mean_flux:
            if len(spc) > 0:
                if flag_always_full_band:
                    ref_mean_flux = self.ref_mean_flux
                else:
                    ref_mean_flux = self.ref_mean_flux*band_area/\
                                    self.area(band_l0, band_lf, flag_force_parametric)

                out_area = np.trapz(out_y, spc.x)
                weighted_mean_flux = out_area / band_area
                cmag = -2.5 * np.log10(weighted_mean_flux / ref_mean_flux)

                # cosmetic manipulation
                cmag = np.round(cmag, 3)
                if cmag == 0.0:
                    cmag = 0.0  # get rid of "-0.0"



























    def ufunc(self, flag_force_parametric=False):
        """
        Returns a function of wavelength for the transmission filter given the band name. Works as a numpy ufunc

        Arguments:
            band_name -- e.g. "U", "J"
            flag_force_parametric -- if set, will use parametric data even for the tabulated bands UBVRI
        """
        flag_parametric = flag_force_parametric
        if not flag_force_parametric and self.tabular:
            x, y = list(zip(*self.tabular))
            f = interp1d(x, y, kind='linear', bounds_error=False, fill_value=0)
        else:
            flag_parametric = True

        if flag_parametric:
            x0, fwhm = self.parametric
            f = ufunc_gauss(x0, fwhm)
        return f


    def range(self, flag_force_parametric=False, no_stds=3):
        """
        Returns [wl0, wl1] (angstrom) beyond which the transmission function value is zero or negligible

        Arguments:
            flag_force_parametric -- if set, will use parametric data even for the tabulated bands UBVRI
            no_stds -- number of standard deviations away from center to consider the range limit (parametric cases only).
                       At 3 standard deviations from the center the value drops to approximately 1.1% of the maximum
        """
        flag_parametric = flag_force_parametric

        if not flag_force_parametric and self.tabular:
            points = self.tabular
            p0, pf = points[0], points[-1]
            # The following is assumed for the code to work
            assert p0[1] == 0 and pf[1] == 0, "UBVRIBands.TABULAR tables must start and end with a zero"
            ret = [p0[0], pf[0]]
        else:
            flag_parametric = True

        if flag_parametric:
            x0, fwhm = self.parametric
            # FWHM-to-(standard deviation) convertion
            std = fwhm * (1. / np.sqrt(8 * np.log(2)))
            ret = [x0 - no_stds * std, x0 + no_stds * std]
        return ret


    def area(self, l0, lf, flag_force_parametric=False):
        """
        Calculates area (unit: a.u.*angstrom) under given range [l0, lf]

        Arguments:
            l0 -- lower edge of range
            lf -- upper edge of range
            flag_force_parametric=False -- TODO see ?
        """
        # Calculates number of points as a fraction of REF_NUM_POINTS
        ref_range = self.range(flag_force_parametric)
        num_points = int((lf-l0)/(ref_range[1]-ref_range[0])*REF_NUM_POINTS)
        x = np.linspace(l0, lf, num_points)
        func = self.ufunc(flag_force_parametric)
        y = func(x)
        # Has to include x in the integration because it may not be evenly spaced with the tabulated data
        area = np.trapz(y, x)  # integration
        return area



# # Mounts dictionary bands_standard: standard band set
# Michael Bessel 1990
# Taken from http://spiff.rit.edu/classes/phys440/lectures/filters/filters.html
BANDS_STANDARD_TABULAR = collections.OrderedDict((
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


# (midpoint, FWHM) (angstrom)
# Values taken from https://en.wikipedia.org/wiki/Photometric_system
BANDS_STANDARD_PARAMETRIC = collections.OrderedDict((
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


# Standard flux, according to several references
#
# TODO get references: Bessel etc
#
# values taken from https://en.wikipedia.org/wiki/Apparent_magnitude
# I- and J-band values agree with Evans, C.J., et al., A&A 527(2011): A50.
#
# Unit is erg/cm**2/s/Hz
BANDS_STANDARD_REF_FLUX = collections.OrderedDict((
("U", 1.81e-20),
("B", 4.26e-20),
("V", 3.64e-20),
("R", 3.08e-20),
("I", 2.55e-20),
("Y", None),
("J", 1.60e-20),
("H", 1.08e-20),
("K", 0.67e-20),
("L", None),
("M", None),
("N", None),
("Q", None),
))


bands_standard = collections.OrderedDict()

for k in BANDS_STANDARD_PARAMETRIC:
    bands_standard[k] = Bandpass(k, BANDS_STANDARD_TABULAR.get(k),
                                    BANDS_STANDARD_PARAMETRIC.get(k),
                                    BANDS_STANDARD_REF_FLUX.get(k))


def ufunc_gauss(x0, fwhm):
    """
    Returns Gaussian function (callable) that works as a numpy ufunc

    Arguments:
        x0 -- maximum value, where the function evaluates to 1.
        fwhm -- "Full-Width at Half-Maximum"

    Reference: https://en.wikipedia.org/wiki/Gaussian_function
    """
    K = 4 * np.log(2) / fwhm ** 2
    def f(x):
        return np.exp(-(x - x0) ** 2 * K)
    return f


