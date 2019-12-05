.. code-block:: none

    usage: turbospectrum-to-atoms.py [-h] [--min_algf [MIN_ALGF]]
                                     [--max_kiex [MAX_KIEX]] [-s [SKIP]]
                                     fn_input [fn_output]
    
    Converts TurboSpectrum atomic lines file to PFANT atomic lines file.
    
    Certain elements are skipped.
    
    Usage examples:
    
        To skip only H and He:
        > turbospectrum-to-atoms --skip "H, He"
    
    positional arguments:
      fn_input              input file name
      fn_output             output file name (default: atoms-untuned-<fn_input>)
    
    optional arguments:
      -h, --help            show this help message and exit
      --min_algf [MIN_ALGF]
                            minimum algf (log gf) (default: -7)
      --max_kiex [MAX_KIEX]
                            maximum kiex (default: 15)
      -s [SKIP], --skip [SKIP]
                            list of elements to skip (use quotes and separate
                            elements by commas) (default: H, He, F, Ne, P, Ar, Cl,
                            As, Br, Kr, Xe)
    

This script belongs to package *pyfant*
