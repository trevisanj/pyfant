#!/usr/bin/env python
"""
Runs pfant and nulbad in "multi mode" (equivalent to Tab 4 in "x.py")

This script runs spectral synthesis and convolutions with Gaussian profile for
several combinations of (atomic abundance, FWHM)
"""

import argparse
import pyfant
import a99
import logging


a99.logging_level = logging.INFO
a99.flag_log_file = True

DEFAULT_SESSION_ID = pyfant.MULTISESSION_PREFIX+"<i>"


if __name__ == "__main__":
    # Configuration for Python logging messages.
    logger = a99.get_python_logger()

    # Parser command-line arguments
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=a99.SmartFormatter)
    names = pyfant.Conf().opt.get_names() # option names
    for name in names:
        # name = name.replace('_', '-')
        parser.add_argument("--"+name, type=str, help='')

    parser.add_argument("-f", "--fn_abxfwhm", type=str, default=pyfant.FileAbXFwhm.default_filename,
                        help="Name of file specifying different abundances and FWHM's")
    parser.add_argument("-s", "--custom_session_id", type=str, default=DEFAULT_SESSION_ID,
                        help="Name of directory where output files will be saved")
    args = parser.parse_args()

    # Makes FileOptions object
    oopt = pyfant.FileOptions()
    for name in names:
        x = args.__getattribute__(name)
        if x is not None:
            oopt.__setattr__(name, x)

    oconf = pyfant.Conf()  # creates a Conf object just to use its get_file_*() methods
    omain = oconf.get_file_main(oopt)
    oabonds = oconf.get_file_abonds(oopt)

    oabxfwhm = pyfant.FileAbXFwhm()
    oabxfwhm.load(args.fn_abxfwhm)

    r = pyfant.MultiRunnable(omain, oabonds, oopt, oabxfwhm)
    if args.custom_session_id != DEFAULT_SESSION_ID:
        custom_id = args.custom_session_id
        if pyfant.get_custom_multisession_dirname(custom_id) == custom_id:
            # Understands that session dirname prefix must be cleared
            r.sid.id_maker.session_prefix_singular = ""
        r.sid.id = custom_id

    r.run()

    logger.info("Session directory: {}".format(r.sid.dir))
