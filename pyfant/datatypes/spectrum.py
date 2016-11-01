__all__ = ["Spectrum"]


from ..misc import *
from astropy.io import fits
from astropy import units as u
from scipy import interp


fnu = u.erg/u.cm**2/u.s/u.Hz
flambda = u.erg/u.cm**2/u.s/u.angstrom


class Spectrum(object):
    """
    Spectrum with several *in-place* operations, conversion utilities etc.

    Routines that have the term *in place*: it means that the spectrum
    itself is changed and nothing is returned
    """

    @property
    def xunit(self):
        return self.more_headers.get("X-UNIT")

    @xunit.setter
    def xunit(self, value):
        self.more_headers["X-UNIT"] = value

    @property
    def yunit(self):
        return self.more_headers.get("Y-UNIT")

    @yunit.setter
    def yunit(self, value):
        self.more_headers["Y-UNIT"] = value

    @property
    def title(self):
        """Calculated, read-only property"""
        ret = None
        if ret is None:
            ret = self.filename
        if ret is None:
            ret = self.more_headers.get("ORIGIN")
        return ret

    @property
    def wavelength(self):
        return self.x

    @wavelength.setter
    def wavelength(self, x):
        self.x = x

    @property
    def l0(self):
        return self.x[0]

    @property
    def lf(self):
        return self.x[-1]

    @property
    def flux(self):
        return self.y

    @flux.setter
    def flux(self, y):
        self.y = y

    @property
    def delta_lambda(self):
        """Returns delta lambda or NaN if found not to be constant"""
        ret = self.x[1]-self.x[0]
        if abs(self.x[-1]-self.x[-2]-ret) > 1e-5:
            return float("nan")
        return ret

    @property
    def pixel_x(self):
        return self.more_headers.get("PIXEL-X")

    @pixel_x.setter
    def pixel_x(self, value):
        self.more_headers["PIXEL-X"] = value

    @property
    def pixel_y(self):
        return self.more_headers.get("PIXEL-Y")
        
    @pixel_y.setter
    def pixel_y(self, value):
        self.more_headers["PIXEL-Y"] = value

    @property
    def z_start(self):
        return self.more_headers.get("Z-START")

    @z_start.setter
    def z_start(self, value):
        self.more_headers["Z-START"] = value

    @property
    def ylabel(self):
        return self.more_headers.get("YLABEL")

    @ylabel.setter
    def ylabel(self, value):
        self.more_headers["YLABEL"] = value

    #*****************
    def __init__(self):
        self._flag_created_by_block = False  # assertion
        self.more_headers = {}
        self.x = None  # x-values
        self.y = None  # y-values
        # Default units
        self.xunit = u.angstrom
        self.yunit = fnu
        self.filename = None

    def __len__(self):
        """Corresponds to nulbad "ktot"."""
        return len(self.x) if self.x is not None else 0

    def one_liner_str(self):
        if self.x is not None and len(self.x) > 0:
            # s = ", ".join(["%g <= lambda <= %g" % (self.x[0], self.x[-1]),
            #                "delta_lambda = %g" % self.delta_lambda,
            #                "no. points: %d" % len(self.x)])

            info = ["%g \u2264 \u03BB \u2264 %g" % (self.x[0], self.x[-1])]
            try:
                dl = self.delta_lambda
                info.append("\u0394\u03BB = %g" % dl)
            except:
                pass

            info.append("%g \u2264 flux \u2264 %g" % (np.min(self.y), np.max(self.y)))
            info.append("length: %d" % len(self.x))

            s = " | ".join(info)
        else:
            s = "(empty)"
        return s

    def __str__(self):
        return self.one_liner_str()
        # s = ", ".join(["ikeytot = ", str(self.ikeytot), "\n",
        #                "tit = ", str(self.tit), "\n",
        #                "tetaef = ", str(self.tetaef), "\n",
        #                "glog = ", str(self.glog), "\n",
        #                "asalog = ", str(self.asalog), "\n",
        #                "modeles_nhe = ", str(self.modeles_nhe), "\n",
        #                "amg = ", str(self.amg), "\n",
        #                "l0 = ", str(self.l0), "\n",
        #                "lf = ", str(self.lf), "\n",
        #                "pas = ", str(self.pas), "\n",
        #                "echx = ", str(self.echx), "\n",
        #                "echy = ", str(self.echy), "\n",
        #                "fwhm = ", str(self.fwhm), "\n",
        #                "============\n"
        #                "Size of Spectrum: ", str(len(self)), "\n"])
        # return s

    def get_rgb(self, visible_range=None, method=0):
        """Takes weighted average of rainbow colors RGB's

        Arguments:
            visible_range=None -- if passed, affine-transforms the rainbow colors
            method --
              0: rainbow colors
              1: RGB
        """

        if len(visible_range) < 2:
            raise RuntimeError("Invalid visible range: %s" % (visible_range,))
        if visible_range[1] <= visible_range[0]:
            raise RuntimeError("Second element of visible range (%s) must be greater than first element" % (visible_range,))

        if method == 1:
            # new color system splitting visible range in three
            dl = float(visible_range[1]-visible_range[0])/3
            ranges = np.array([[visible_range[0]+i*dl, visible_range[0]+(i+1)*dl] for i in range(3)])
            colors = np.array([(0., 0., 1.), (0., 1., 0.), (1., 0., 0.)])  # blue, green, red

            tot_area, tot_sum = 0., np.zeros(3)
            for color, range_ in zip(colors, ranges):
                b = np.logical_and(self.x >= range_[0], self.x <= range_[1])
                area = np.sum(self.y[b])
                tot_area += area
                tot_sum += color*area
            if tot_area == 0.:
                tot_area = 1.
            ret = tot_sum/tot_area
            return ret

        elif method == 0:
            tot_area, tot_sum = 0., np.zeros(3)
            ftrans = lambda x: x
            if visible_range:
                ll0 = rainbow_colors[0].l0
                llf = rainbow_colors[-1].lf
                ftrans = lambda lold: visible_range[0] + (visible_range[1] - visible_range[0]) / (llf - ll0) * (lold - ll0)

            for color in rainbow_colors:
                b = np.logical_and(self.x >= ftrans(color.l0), self.x <= ftrans(color.lf))
                area = np.sum(self.y[b])
                tot_area += area
                tot_sum += color.rgb*area
            if tot_area == 0.:
                tot_area = 1.
            ret = tot_sum/tot_area
            return ret
        else:
            raise RuntimeError("Unknown method: %s" % method)



    # header parameters *not* to be put automatically in self.more_headers
    #                  saved separately  dealt with automatically by the FITS module
    #                  ----------------  ------------------------------------------------
    _IGNORE_HEADERS = ("CRVAL", "CDELT", "NAXIS", "PCOUNT", "BITPIX", "GCOUNT", "XTENSION",
                       "XUNIT", "BUNIT")
    def from_hdu(self, hdu):
        # x/wavelength and y/flux
        n = hdu.data.shape[0]
        lambda0 = hdu.header["CRVAL1"]
        try:
            delta_lambda = hdu.header["CDELT1"]
        except Exception as E:  # todo figure out the type of exception (KeyError?)
            delta_lambda = hdu.header['CD1_1']
            print("Alternative delta lambda in FITS header: CD1_1")
            print("Please narrow the Exception specification in the code")
            print(("Exception is: " + str(E) + " " + E.__class__.__name__))
            print(delta_lambda)
        self.x = np.linspace(lambda0, lambda0 + delta_lambda * (n - 1), n)
        self.y = hdu.data

        _xunit = hdu.header.get("X-UNIT")
        if _xunit:
            self.xunit = u.Unit(_xunit)
        else:
            _xunit = hdu.header.get("XUNIT")
            if _xunit == "nm":
                self.xunit = u.nm
            elif _xunit == "A":
                self.xunit = u.angstrom

        _yunit = hdu.header.get("Y-UNIT")
        if _yunit:
            self.yunit = u.Unit(_yunit)
        else:
            _yunit = hdu.header.get("BUNIT")
            if _yunit == "erg/s/cm2/Hz":
                self.xunit = fnu
            elif _yunit == "erg/s/cm2/A":
                self.xunit = flambda

        # Additional header fields
        for name in hdu.header:
            if not name.startswith(self._IGNORE_HEADERS):
                # **Note** that it eliminates "#" comments from FITS header
                value = hdu.header[name]
                if isinstance(value, str):
                    value = value.split("#")[0].strip()
                self.more_headers[name] = value

    def to_hdu(self):
        """Converts to FITS HDU. delta_lambda must be a constant"""

        if np.isnan(self.delta_lambda):
            raise RuntimeError("Cannot encode HDU in spec '{}' because delta_lambda is not constant".format(spec))

        hdu = fits.PrimaryHDU()
        # hdu.header[
        #     "telescop"] = "PFANT synthetic spectrum"  # "suggested" by https://python4astronomers.github.io/astropy/fits.html
        hdu.header["CRVAL1"] = self.x[0]
        hdu.header["CDELT1"] = self.delta_lambda


        _xunit = str(self.xunit)
        _yunit = str(self.yunit)
        hdu.header["X-UNIT"] = _xunit
        hdu.header["Y-UNIT"] = _yunit

        # AOSS expectations
        _xunit = "(not supported)"
        _yunit = "(not supported)"
        if self.xunit == u.angstrom:
            _xunit = "A"
        elif self.xunit == u.nm:
            _xunit = "nm"
        if self.yunit == fnu:
            _yunit = "erg/s/cm2/Hz"
        elif self.yunit == flambda:
            _yunit = "erg/s/cm2/A"
        hdu.header["XUNIT"] = _xunit
        hdu.header["BUNIT"] = _yunit

        for key, value in list(self.more_headers.items()):
            if key in ("X-UNIT", "Y-UNIT"):
                continue

            try:
                # Strips line feeds eventually present in header data
                if isinstance(value, str):
                    value = value.replace("\n", "")
                hdu.header[key] = value
            except:
                get_python_logger().exception("Error adding header['%s'] = '%s'" % (key, value))
                raise
        hdu.data = self.y
        return hdu
        
    def cut(self, l0, l1):
        """Cuts *in place* to wavelength interval [l0, l1]. Cut is done within the array objects thus keeping the same objects"""
        ii_delete = np.where(np.logical_or(self.x < l0, self.x > l1))
        self.x = np.delete(self.x, ii_delete)
        self.y = np.delete(self.y, ii_delete)
        
    def cut_idxs(self, i0, i1):
        """Cuts *in place* to slice i0:i1 (pythonic, interval = [i0, i1["""
        self.x = self.x[i0:i1]
        self.y = self.y[i0:i1]

    def resample(self, new_wavelength, kind='linear'):
        """Resamples *in-place* to new wavelength vector using interpolation

        Arguments:
            new_wavelength -- new wavelength vector
            kind -- interpolation kind to be passed to scipy.interpolate.interp1d
        """
        # f = interp1d(self.x, self.y, kind='linear', bounds_error=True, fill_value=0)
        self.y = interp(new_wavelength, self.x, self.y)
        self.wavelength = new_wavelength


    def convert_x(self, new_unit):
        """Converts x-axis to new unit"""

    # def flambda_to_fnu(self):
    #     """
    #     Flux-nu to flux-lambda conversion **in-place**
    #
    #     Formula:
    #         f_nu = f_lambda*(lambda/nu) = f_lambda*lambda**2/c
    #
    #         where
    #             lambda is the wavelength in cm,
    #             c is the speed of light in cm/s
    #             f_lambda has irrelevant unit for this purpose
    #
    #     **Note** By convention in this library, Spectrum wavelength is always in angstrom
    #     """
    #
    #     x_cm = self.x*1e-8
    #     self.y *= 1./(1e-8 * C) * x_cm ** 2
    #
    # def fnu_to_flambda(self):
    #     """
    #
    #     **in-place** flux-lambda to flux-nu conversion
    #
    #     Converts flux from erg/s/cm**2/Hz
    #                     to erg/s/cm**2/angstrom
    #     Formula:
    #         f_lambda = f_nu*(nu/lambda) = f_nu*c/lambda**2
    #
    #         (terms description are the same as in flambda_to_fnu())
    #     """
    #
    #     x_cm = self.x * 1e-8  # angstrom -to cm
    #     #    y * C/x_cm ** 2  would be in erg/s/cm**2/cm
    #     # 1e-8 * C/x_cm ** 2        is in erg/s/cm**2/angstrom
    #     self.y *= 1e-8 * C/x_cm ** 2
