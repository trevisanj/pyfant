#!/usr/bin/env python
"""
Convolve spectrum with Gaussian profile.

This is the Python version of "nulbad", the PFANT convolution-with-Gaussian
utility. This script ``nulbad.py`` was created in order to support more input
formats.

On the other hand, it does not open file "main.dat" to get parameters as
Fortran ``nulbad`` does. The latter also has a re-sampling ability that
this one doesn't.

The resulting file, compared to Fortran ``nulbad``, is nearly alike (you may see
a difference around the 6th digit). This one has one more data point at each side.

Supported file formats
======================

    Format                         Input?   Output?  Notes
    -----------------------------  -------  -------- ---------------------
    ``pfant`` output               YES      no    
    XY (two-column "lambda-flux")  YES      YES      default output format
    FITS                           YES      YES

Examples
========

  1) Create file 'flux.norm.pynulbad.0.08':

     nulbad.py --fwhm 0.08 flux.norm

  2) Create file 'flux.norm.pynulbad.0.08.fits':

     nulbad.py --fwhm 0.08 -f fits flux.norm

"""

import argparse
import logging
import sys
import a99
import f311
import pyfant
import f311
import numpy as np

a99.logging_level = logging.INFO

DEF_FN_CV = '<fn_flux>.<fwhm>'

OCLSS = {"xy": f311.FileSpectrumXY, "fits": f311.FileSpectrumFits}


def save(args, sp):

    f = OCLSS[args.format]()
    f.spectrum = sp
    f.save_as(args.fn_cv)

    print("Successfully created file '{0!s}'".format(args.fn_cv))


def get_gaussian(fwhm, pas):
    """Calculate Gaussian curve

    Args:
        fwhm
        pas: delta-lambda of curve

    Returns: 
        y: numpy vector containing calculated Gaussian curve
    """

    # Relation between the standard deviation and FWHM
    # (https://en.wikipedia.org/wiki/Full_width_at_half_maximum)
    sigma = fwhm/(2*np.sqrt(2*np.log(2)))

    NUM_SIGMAS = 3*1.4142
    num_points = 2*np.ceil(NUM_SIGMAS*sigma/pas)+1  # note this is an odd number
    offset = pas*((num_points-1)/2)

    x = np.arange(num_points, dtype=float)*pas-offset

    k1 = 1/(sigma*np.sqrt(2*np.pi))
    k2 = 2*sigma**2
    y = k1*np.exp(-x**2/k2)*pas

    return y

def convolve(args, sp):
    """Convolve spectrum with Gaussian profile and return new spectrum.

    The new spectrum has a narrower range"""

    sp2 = f311.Spectrum()

    h = get_gaussian(args.fwhm, sp.delta_lambda)
    num_points = len(h)

    sp2.y = np.convolve(sp.y, h, 'valid')
    off = int((num_points-1)/2)  # number of invalid points at each edge
    sp2.x = sp.x[off:-off]

    assert(len(sp2.x) == len(sp2.y))

    return sp2

def main(args):    
    sp = f311.load_spectrum(args.fn_flux)
    if not sp:
        print("File '{0!s}' not recognized as a spectrum file.".format(args.fn_flux))
        sys.exit()

    sp2 = convolve(args, sp)

    save(args, sp2)






if __name__ == "__main__":
    parser = argparse.ArgumentParser(
     description=__doc__,
     formatter_class=a99.SmartFormatter
     )
 
    parser.add_argument('--fwhm', type=float, nargs='?', default=0.12, 
        help="full width at half maximum (FWHM) of Gaussian curve")
    parser.add_argument('-f', '--format', type=str, nargs='?', default='xy',
        choices=["xy", "fits"], help="Output format")
    parser.add_argument('fn_flux', type=str,  
        help='input spectral filename')
    parser.add_argument('fn_cv', type=str, help='output file name', nargs='?', default=DEF_FN_CV)

    args = parser.parse_args()

    if args.fn_cv == DEF_FN_CV:
        more = ".fits" if args.format == "fits" else ""
        args.fn_cv = "{}.pynulbad.{:.3f}{}".format(args.fn_flux, args.fwhm, more)

    print("fn_flux (input filename) =", args.fn_flux)
    print("fn_cv (output filename) =", args.fn_cv)
    print("fwhm =", args.fwhm)
    print("output format = ", args.format)

    main(args)

 
