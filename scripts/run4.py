#!/usr/bin/env python3
"""
Runs the four Fortran binaries in sequence: `innewmarcs`, `hydro2`, `pfant`, `nulbad`

Check session directory "session-<number>" for log files.
"""

import argparse
import pyfant as pf
import astroapi as aa
import logging


aa.logging_level = logging.INFO
aa.flag_log_file = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=aa.SmartFormatter
    )

    names = pf.Conf().opt.get_names() # option names

    for name in names:
        # name = name.replace('_', '-')
        parser.add_argument("--"+name, type=str, help='')

    args = parser.parse_args()


    # Configuration for Python logging messages.
    logger = aa.get_python_logger()

    c = pf.Combo()
    c.conf.flag_log_file = True  # Configuration for Fortran messages
    c.conf.flag_log_console = True  # "
    c.conf.flag_output_to_dir = False  # Will generate outputs in current directory

    for name in names:
        x = args.__getattribute__(name)
        if x is not None:
            c.conf.opt.__setattr__(name, x)

    c.run()
    logger.info("Session directory: %s" % c.conf.sid.dir)
