__all__ = ["SLB_UseSBlock", "SLB_ExtractContinua", "SLB_MergeDownBlock", "SLB_MergeDown", "SLB_SNR"]


import numpy as np
from pyfant import *
from pyfant.datatypes.filesplist import SpectrumList
import copy
from .baseblocks import *


class SLB_UseSBlock(SLBlock):
    """Calls sblock.use() for each individual spectrum"""
    def __init__(self, sblock=None):
        SLBlock.__init__(self)
        self.sblock = sblock

    def _do_use(self, inp):
        output = self._new_output()
        for i, sp in enumerate(inp.spectra):
            output.add_spectrum(self.sblock.use(sp))
        return output


class SLB_ExtractContinua(SLBlock):
    """Calculates upper envelopes and subtracts mean(noise std)"""

    # TODO this is not a great system. Just de-noising could substantially improve the extracted continua

    def _do_use(self, inp):
        output = SLB_UseSBlock(SB_Rubberband(flag_upper=True)).use(inp)
        spectrum_std = SLB_MergeDown(func=np.std).use(inp)
        mean_std = np.mean(spectrum_std.spectra[0].y)
        for spectrum in output.spectra:
            spectrum.y -= mean_std*3
        return output


class SLB_MergeDownBlock(SLBlock):
    """Base class for all SpectrumList-to-Spectrumlist blocks whose output has only one row in it

    This class has no gear and exists for grouping purposes only"""


class SLB_MergeDown(SLB_MergeDownBlock):
    """Output contains single spectrum whose y-vector is calculated using a numpy function

    The numpy function must be able to operate on the first axis, e.g., np.mean(), np.std()
    """

    def __init__(self, func=np.std):
        SLB_MergeDownBlock.__init__(self)
        self.func = func

    def _do_use(self, inp):
        output = self._new_output()
        sp = Spectrum()
        sp.wavelength = np.copy(inp.wavelength)
        sp.flux = self.func(inp.matrix(), 0)
        if len(sp.flux) != len(sp.wavelength):
            raise RuntimeError("func returned vector of length %d, but should be %d" % (len(sp.flux), len(sp.wavelength)))
        output.add_spectrum(sp)
        return output


class SLB_SNR(SLB_MergeDownBlock):
    """Calculates the SNR(lambda) = Power_signal(lambda)/Power_noise(lambda)

    Arguments:
        continua -- SpectrumList containing the continua that will be used as the "signal" level.
                    If not passed, will be calculated from the input spectra using a SB_Rubberband(True) block

    References:
        [1] https://en.wikipedia.org/wiki/Signal_averaging
    """

    # TODO I think that it is more correct to talk about "continuum" not continua

    def __init__(self, continua=None):
        SLB_MergeDownBlock.__init__(self)
        self.continua = continua

    def _do_use(self, inp):
        if self.continua is None:
            continua = SLB_UseSBlock(SB_Rubberband(True)).use(inp)
        else:
            continua = self.continua
        cont_2 = SLB_UseSBlock(SB_ElementWise(np.square)).use(continua)  # continua squared
        mean_cont_2 = SLB_MergeDown(np.mean).use(cont_2)
        var_spectra = SLB_MergeDown(np.var).use(inp)
        output = self._new_output()
        sp = Spectrum()
        sp.wavelength = np.copy(inp.wavelength)
        sp.flux = mean_cont_2.spectra[0].flux/var_spectra.spectra[0].flux
        output.add_spectrum(sp)
        return output
