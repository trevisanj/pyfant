.. code-block:: none

    usage: vald3-to-atoms.py [-h] [--min_algf [MIN_ALGF]] [--max_kiex [MAX_KIEX]]
                             [-s [SKIP]]
                             fn_input [fn_output]
    
    Converts VALD3 atomic/molecular lines file to PFANT atomic lines file.
    
    Molecular lines and certain elements are skipped.
    
    Usage examples:
    
        To skip only H and He:
        > vald3-to-atoms --skip "H, He"
    
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
