"""TurboSpectrum linelist format. Prepared for molecules only"""


__all__ = ["PlezAtomicLine", "PlezMolecularLine", "PlezSpecies", "FilePlezLinelist"]

import a99
from f311 import DataFile
import io
import os
from collections import defaultdict
import re


# Will update progress status every time the following number of lines is read from file
_PROGRESS_INDICATOR_PERIOD = 1030 * 5


class PlezLine(object):
    def __init__(self):
        self.lambda_ = 1.
        self.chiex = 1.
        self.loggf = 1.
        self.gu = 1.
        self.fdamp = 1.
        self.raddmp = 1.


class PlezAtomicLine(PlezLine):
    pass


class PlezMolecularLine(PlezLine):
    def __init__(self):
        PlezLine.__init__(self)
        self.branch = ""


class PlezSpecies(object):
    def __init__(self, name="", lines=None):
        if lines is None:
            lines = []

        self.name = name
        self.lines = lines


@a99.froze_it
class FilePlezLinelist(DataFile):
    """
    Plez molecular lines file

    **Note** Plez file so far refers to one molecule only.

    **Note** Load only
    """

    def __init__(self):
        DataFile.__init__(self)

        self.molecules = defaultdict(lambda: PlezSpecies())
        self.atoms = defaultdict(lambda: PlezSpecies())

    def _do_load(self, filename):

        #  '0107.000014          '  1        1300
        #  'NH-ca PGopher'
        #     3257.93970    1.730   -2.102 .00    3.  0.216E+07 'Pe(2)                0   1.0  e    1  -  0   2.0  e    1 Ram et al.

        with open(filename, "r") as h:
            self._do_load_h(h, filename)

    def _do_load_h(self, h, filename):
        r = 0  # counts rows of file
        ii = 0

        expr_branch = re.compile("[PQRS]\d*")  # regular expression to find the branch

        # states
        EXP_SPECIES = 0  # expecting species definition
        EXP_NAME = 1  # expecting name of species
        EXP_ANY = 2

        state = EXP_SPECIES
        is_atom = None
        species = None
        flag_break = False

        try:
            while True:
                s = h.readline().strip()
                if len(s) == 0:
                    flag_break = True

                if not flag_break:
                    if s[0] == "'":
                        if state == EXP_SPECIES or state == EXP_ANY:
                            # New species to come

                            # Determine whether atom or molecule
                            atnumber = int(s[1:s.index(".")])
                            is_atom = atnumber <= 92

                            state = EXP_NAME

                        elif EXP_NAME:
                            name = s.strip("'")
                            species = self.atoms[name] if is_atom else self.molecules[name]

                            a99.get_python_logger().info(
                                 "Loading '{}': species '{}'".format(filename, name))

                            state = EXP_ANY

                    else:
                        if state != EXP_ANY:
                            raise RuntimeError("Not expecting line right now")
                        # It is a line

                        # Read 6 numeric values then something between quotes
                        line = PlezAtomicLine() if is_atom else PlezMolecularLine()

                        line.lambda_, line.chiex, line.loggf, line.gu, line.fdamp, line.raddmp = \
                            [float(x) for x in s[:s.index("'")].split()]

                        if not is_atom:
                            # Get the branch
                            tmp = s[s.index("'"):]
                            line.branch = expr_branch.search(tmp).group()

                        species.lines.append(line)

                if flag_break:
                    break

                r += 1
                ii += 1
                if ii == _PROGRESS_INDICATOR_PERIOD:
                    # a99.get_python_logger().info(
                    #      "Loading '{}': {}".format(filename, a99.format_progress(r, num_lines)))
                    ii = 0

        except Exception as e:
            raise RuntimeError("Error around %d%s row of file '%s': \"%s\"" %
                               (r + 1, a99.ordinal_suffix(r + 1), filename, a99.str_exc(e))) from e


