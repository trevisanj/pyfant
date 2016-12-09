#!/usr/bin/env python3

import tabulate
import sys

from pyfant.convmol.nistbot import get_nist_webbook_constants

if __name__ == "__main__":
    formula = sys.argv[1]
    data, header, title = get_nist_webbook_constants(formula)
    print("\n*** {} ***\n".format(title))
    print(tabulate.tabulate(data, header))


