#!/usr/bin/python

"""
Lists all Fortran/Python programs available (PFANT + pyfant)
"""

from pyfant import *
import argparse
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=SmartFormatter
    )
    parser.add_argument('format', type=str, help='Print format', nargs="?", default="text",
                        choices=["text", "markdown-list", "markdown-table"])
    args = parser.parse_args()

    scriptinfo = get_script_info(get_pyfant_scripts_path())
    linesp, module_len = format_script_info(scriptinfo, format=args.format)
    linesf = get_fortrans(module_len)

    print fmt_ascii_h1("Fortran")
    print "\n".join(linesf)
    print ""

    print fmt_ascii_h1("Python")
    print "\n".join(linesp)

    print ""
    print "Search directories:"
    print "  Fortran: %s" % os.path.join(get_pfant_path(), "fortran", "bin")
    print "  Python: %s" % os.path.join(get_pyfant_path(), "scripts")

