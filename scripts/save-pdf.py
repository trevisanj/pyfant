#!/usr/bin/env python3

"""
Looks for file "flux.norm" inside directories session-* and saves one figure per page in a PDF file
"""
"""
References:
http://stackoverflow.com/questions/17788685
"""


import glob
import os
import matplotlib.backends.backend_pdf
import argparse
from pyfant import *
import matplotlib.pyplot as plt
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

    parser.add_argument('--samey',
        help='Creates all plots with same y-limits of [0, 1.02]', action="store_true")
    parser.add_argument('fn_output', nargs='?', default='output.pdf', type=str,
                        help='PDF output file name')

    args = parser.parse_args()

    dd = glob.glob(conf.session_prefix+"*")
    dd.sort()

    v = aa.VisSpectrum()
    pdf = matplotlib.backends.backend_pdf.PdfPages(args.fn_output)

    aa.format_BLB()

    for d in dd:
        name = d[8:]

        print("Saving ", name, "...")

        f = aa.FileSpectrumPfant()
        f.load(os.path.join(d, "flux.norm"))

        v.title = "%s" % name
        v.use(f)

        fig = plt.gcf()
        if args.samey:
            plt.ylim([0, 1.02])
        else:
            y = f.spectrum.y
            ymin, ymax = min(y), max(y)
            margin = .02*(ymax-ymin)
            plt.ylim([ymin-margin, ymax+margin])
        ax = plt.gca()
        p = ax.get_position()
        p.x0 = 0.11
        ax.set_position(p)  # Try to apply same position for all figures to improve flicking experience
        pdf.savefig(fig)
        plt.close()

    # for fig in xrange(1, figure().number): ## will open an empty extra figure :(
    #     pdf.savefig( fig )
    pdf.close()

