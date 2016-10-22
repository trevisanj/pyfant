__all__ = [
"SB_Rubberband", "SB_AddNoise", "SB_FNuToFLambda", "SB_ElementWise", "SB_Extend",
    "Sp2Scalar", "SB_scalar_SNR"
]


import numpy as np
from pyfant import *
from pyfant.datatypes.filesplist import SpectrumList
import copy
from .baseblocks import *

class SNR(Sp2Scalar):
    """
    Calculates Signal-to-noise ratio (SNR) using a part of the "signal" (i.e. the spectrum)

    Output is **scalar**

    The signal-to-noise ratio (SNR) is often defined as (signal power) / (noise power), herein
    calculated as

        y_RMS**2 / variance(y)     (https://en.wikipedia.org/wiki/Signal-to-noise_ratio)

    It is assumed that the "signal" is *stationary* within [llzero, llfin]
    meaning that the mean and variance of the "signal" is the same for all points within
    this region (more precisely "weak-sense stationary"
    (https://en.wikipedia.org/wiki/Stationary_process#Weak_or_wide-sense_stationarity))
    """

    def __init__(self, llzero, llfin):
        SpectrumBlock.__init__(self)
        self.llzero = llzero
        self.llfin = llfin

    def _do_use(self, inp):
        x = inp.x
        y = inp.y
        signal = y[np.logical_and(x >= self.llzero, x <= self.llfin)]

        output = np.mean(signal**2)/np.var(signal)
        return output


