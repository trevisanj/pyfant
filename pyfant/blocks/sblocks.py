__all__ = [
"SB_Rubberband", "SB_AddNoise", "SB_FNuToFLambda", "SB_ElementWise", "SB_Extend", "SB_SNR"
]


import numpy as np
from pyfant import *
from pyfant.datatypes.filesplist import SpectrumList
import copy
from .baseblocks import *

class SB_Rubberband(SBlock):
    """Returns a rubber band"""

    def __init__(self, flag_upper=True):
        SBlock.__init__(self)
        # Upper or lower rubberband
        self.flag_upper = flag_upper

    def _do_use(self, input):
        output = self._new_output()
        y = input.y
        if self.flag_upper:
            y = -y
        output.y = rubberband(y)
        if self.flag_upper:
            output.y = -output.y
        return output


class SB_AddNoise(SBlock):
    def __init__(self, std=1.):
        SBlock.__init__(self)
        # Standard deviation of noise
        self.std = std

    def _do_use(self, input):
        n = len(input)
        output = self._new_output()
        output.y = np.copy(input.y)+np.random.normal(0, self.std, n)
        return output


class SB_FNuToFLambda(SBlock):
    """
    Flux-nu to flux-lambda conversion. Assumes the wavelength axis is in angstrom
    """
    def _do_use(self, input):
        raise NotImplementedError()
        output = self._new_output()
        output.y = input.y


class SB_ElementWise(SBlock):
    """Applies function to input.flux. function must return vector of same dimension as input"""

    def __init__(self, func):
        SBlock.__init__(self)
        self.func = func

    def _do_use(self, input):
        output = self._new_output()
        output.wavelength = np.copy(input.wavelength)
        output.flux = self.func(input.flux)
        if len(output.flux) != len(output.wavelength):
            raise RuntimeError(
                "func returned vector of length %d, but should be %d" % (len(output.flux), len(output.wavelength)))
        return output


class SB_Extend(SBlock):
    """
    Extends to left and/or right side

    Arguments:
      fraction -- amount relative to number of points. Note that this
                  applies individually to left and right (see below)
      flag_left -- whether to extend by fraction to left
      flag_right -- whether to extend by fraction to right

    The y-value to use is found by using a "coarse" 2nd-order polynomial baseline.
    The baseline is "coarse" because it does not allow for many iterations until the
    baseline is found

    **Case**
    >> self.extend(.1, True, True)
    # if original has 100 points, resulting will have 120 points

    >> self.extend(.1, True, False)
    # if original has 100 points, resulting will have 110 points
    """

    def __init__(self, fraction=.1, flag_left=True, flag_right=False):
        SBlock.__init__(self)
        self.fraction = fraction
        self.flag_left = flag_left
        self.flag_right = flag_right

    def _do_use(self, input):
        output = self._copy_input(input)

        if not (self.flag_left or self.flag_right):
            return output
        num_add = int(self.fraction*len(output.wavelength))
        if num_add <= 0:
            return output

        x_left, x_right, y_left, y_right = np.array([]), np.array([]), np.array([]), np.array([])

        rubber = -poly_baseline(-output.y, 2, maxit=15)

        if self.flag_left:
            x_left = np.arange(num_add)*output.delta_lambda+(output.x[0]-output.delta_lambda*num_add)
            y_left = np.ones(num_add)*rubber[0]

        if self.flag_right:
            x_right = np.arange(num_add) * output.delta_lambda + (output.x[-1] + output.delta_lambda)
            y_right = np.ones(num_add) * rubber[-1]

        output.x = np.concatenate((x_left, output.x, x_right))
        output.y = np.concatenate((y_left, output.y, y_right))

        return output


class SB_SNR(SBlock):
    """
    Calculates Signal-to-noise ratio (SNR) using a part of the "signal" (i.e. the spectrum)

    The signal-to-noise ratio (SNR) is often defined as (signal power) / (noise power), herein
    calculated as

        y_RMS**2 / variance(y)     (https://en.wikipedia.org/wiki/Signal-to-noise_ratio)

    It is assumed that the "signal" is *stationary* within [llzero, llfin]
    meaning that the mean and variance of the "signal" is the same for all points within
    this region (more precisely "weak-sense stationary"
    (https://en.wikipedia.org/wiki/Stationary_process#Weak_or_wide-sense_stationarity))
    """

    def __init__(self, llzero, llfin):
        SBlock.__init__(self)
        self.llzero = llzero
        self.llfin = llfin

    def _do_use(self, input):
        x = input.x
        y = input.y
        signal = y[np.logical_and(x >= self.llzero, x <= self.llfin)]

        output = np.mean(signal**2)/np.var(signal)
        return output


