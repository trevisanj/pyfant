.. code-block:: none

    usage: nulbad.py [-h] [--fwhm [FWHM]] [-f [{xy,fits}]] fn_flux [fn_cv]
    
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
    
    positional arguments:
      fn_flux               input spectral filename
      fn_cv                 output file name (default: <fn_flux>.<fwhm>)
    
    optional arguments:
      -h, --help            show this help message and exit
      --fwhm [FWHM]         full width at half maximum (FWHM) of Gaussian curve
                            (default: 0.12)
      -f [{xy,fits}], --format [{xy,fits}]
                            Output format (default: xy)
    

This script belongs to package *pyfant*
