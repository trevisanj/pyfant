"""TurboSpectrum linelist format. Prepared for molecules only"""


__all__ = ["PlezAtomicLine", "PlezMolecularLine", "PlezSpecies", "FilePlezLinelist", "FilePlezLinelist1",
           "FilePlezLinelistBase", "load_plez_mol"]

import a99
from f311 import DataFile
import io
import os
from collections import defaultdict
import re


# Will update progress status every time the following number of lines is read from file
_PROGRESS_INDICATOR_PERIOD = 1030 * 5


def load_plez_mol(filename):
    """
    Attempts to load Plez molecular line list

    Returns:
        FilePlezLinelistBase
    """
    import f311
    return f311.load_with_classes(filename, [FilePlezLinelist, FilePlezLinelist1])


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
        self.vl = 0
        self.v2l = 0
        self.Jl = 0.
        self.J2l = 0.


class PlezSpecies(object):
    def __init__(self, name="", lines=None):
        if lines is None:
            lines = []

        self.name = name
        self.lines = lines


class FilePlezLinelistBase(DataFile):
    """Base class for diffent types of Plez molecular lines file"""


@a99.froze_it
class FilePlezLinelist(FilePlezLinelistBase):
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

         # '0107.000014          '  1       12150
         # 'NH A-X Fernando et al., 2018, JQSRT, 217,29 '
         #    3357.55219    0.004   -2.205 .00    3.  0.000E+00 'qR23(0)        0    1.0  e  F2e  -  0    0.0  e  F3e A            X           '
         #    3349.33946    0.004   -2.625 .00    3.  0.000E+00 'rR3(0)         0    1.0  e  F3e  -  0    0.0  e  F3e       A            X     '

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

                            tmp = s[s.index("'"):].strip("'").split()
                            _branch = tmp[0]

                            line.branch = expr_branch.search(_branch).group()
                            line.Jl = float(tmp[2])
                            line.vl = int(tmp[1])
                            line.v2l = int(tmp[6])
                            line.J2l = float(tmp[7])


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


@a99.froze_it
class FilePlezLinelist1(FilePlezLinelistBase):
    """
    Plez molecular lines file having "linelistCN1214V130710.dat" as holotype.
    """

    def __init__(self):
        DataFile.__init__(self)

        self.molecules = defaultdict(lambda: PlezSpecies())
        self.atoms = defaultdict(lambda: PlezSpecies())

    def _do_load(self, filename):
        with open(filename, "r") as h:
            self._do_load_h(h, filename)

    def _do_load_h(self, h, filename):
        r = 0  # counts rows of file
        ii = 0
        species = None
        flag_break = False

        try:
            while True:
                s = h.readline().strip()
                if len(s) == 0:
                    break

                # linelistCN1214V130710.dat
                #
                # Mol vup vlow JLow branch gf       wavenumber  exc (eV) transition (V=violet, R=red)
                # 0   1   2    3    5      6        7
                #---BEGIN SAMPLE---
                #CN1 11 03 034 +  R1   0.4853E-07  40369.070  1.020 V
                #CN1 11 03 035 +  R1   0.5286E-07  40359.670  1.036 V
                #CN1 11 03 036 +  R1   0.5757E-07  40349.879  1.052 V
                #---END SAMPLE---

                tmp = s.split()
                species = self.molecules[tmp[0]]

                line = PlezMolecularLine()

                line.Jl = None
                line.vl = int(tmp[1])
                line.v2l = int(tmp[2])
                line.J2l = float(tmp[3])
                line.lambda_ = 1/float(tmp[7])*1e8  # we assume the wavenumber is in 1/cm
                line.branch = tmp[5]

                species.lines.append(line)

                r += 1
                ii += 1
                if ii == _PROGRESS_INDICATOR_PERIOD:
                    # a99.get_python_logger().info(
                    #      "Loading '{}': {}".format(filename, a99.format_progress(r, num_lines)))
                    ii = 0

        except Exception as e:
            raise RuntimeError("Error around %d%s row of file '%s': \"%s\"" %
                               (r + 1, a99.ordinal_suffix(r + 1), filename, a99.str_exc(e))) from e



@a99.froze_it
class FilePlezLinelist1(FilePlezLinelistBase):
    """
    Plez molecular lines file having "linelistCN1214V130710.dat" as holotype.
    """

    def __init__(self):
        DataFile.__init__(self)

        self.molecules = defaultdict(lambda: PlezSpecies())
        self.atoms = defaultdict(lambda: PlezSpecies())

    def _do_load(self, filename):
        with open(filename, "r") as h:
            self._do_load_h(h, filename)

    def _do_load_h(self, h, filename):
        r = 0  # counts rows of file
        ii = 0
        species = None
        flag_break = False

        try:
            while True:
                s = h.readline().strip()
                if len(s) == 0:
                    break

                # linelistCN1214V130710.dat
                #
                # Mol vup vlow JLow branch gf       wavenumber  exc (eV) transition (V=violet, R=red)
                # 0   1   2    3    5      6        7
                #---BEGIN SAMPLE---
                #CN1 11 03 034 +  R1   0.4853E-07  40369.070  1.020 V
                #CN1 11 03 035 +  R1   0.5286E-07  40359.670  1.036 V
                #CN1 11 03 036 +  R1   0.5757E-07  40349.879  1.052 V
                #---END SAMPLE---

                tmp = s.split()
                species = self.molecules[tmp[0]]

                line = PlezMolecularLine()

                line.Jl = None
                line.vl = int(tmp[1])
                line.v2l = int(tmp[2])
                line.J2l = float(tmp[3])
                line.lambda_ = 1/float(tmp[7])*1e8  # we assume the wavenumber is in 1/cm
                line.branch = tmp[5]

                species.lines.append(line)

                r += 1
                ii += 1
                if ii == _PROGRESS_INDICATOR_PERIOD:
                    # a99.get_python_logger().info(
                    #      "Loading '{}': {}".format(filename, a99.format_progress(r, num_lines)))
                    ii = 0

        except Exception as e:
            raise RuntimeError("Error around %d%s row of file '%s': \"%s\"" %
                               (r + 1, a99.ordinal_suffix(r + 1), filename, a99.str_exc(e))) from e
