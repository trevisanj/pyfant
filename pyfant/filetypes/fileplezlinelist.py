"""TurboSpectrum linelist format. Prepared for molecules only"""


__all__ = ["PlezAtomicLine", "PlezMolecularLine", "PlezSpecies", "FilePlezLinelist", "FilePlezLinelist1",
           "FilePlezLinelistBase", "load_plez_mol", "FilePlezLinelistN14H", "FilePlezLinelist12C16OLi2015",
           "FilePlezLinelistC2"]

import a99
from f311 import DataFile
import io
import os
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
        self.fdamp = 1.
        self.gu = 1.
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
    def __init__(self, elstring, ion, name, lines=None):
        if lines is None:
            lines = []

        self.elstring = elstring
        self.ion = ion
        self.name = name
        self.lines = lines

    def __len__(self):
        return len(self.lines)

    def __iter__(self):
        return iter(self.lines)


class FilePlezLinelistBase(DataFile):
    """Base class for diffent types of Plez atomic/molecular lines file"""


@a99.froze_it
class FilePlezLinelist(FilePlezLinelistBase):
    """
    Plez molecular lines file

    **Note** Plez file so far refers to one molecule only.

    **Note** Load only

    Descentands of this class must implement _do_processline()
    """

    def __init__(self):
        DataFile.__init__(self)

        self.molecules = dict()
        self.atoms = dict()

        self.expr_branch = re.compile("[PQRS]\d*")  # regular expression to find the branch

    def _do_load(self, filename):
        with open(filename, "r") as h:
            self._do_load_h(h, filename)

    def _process_line_molecule(self, species, line, s):
        self._do_process_line_molecule(species, line, s)

    def _do_process_line_molecule(self, species, line, s):
        pass  # 20230605 no need to raise here raise NotImplementedError()

    def _do_load_h(self, h, filename):
        r = 0  # counts rows of file
        ii = 0

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

                            s_ = s[1:]
                            elstring = s_[:s_.index("'")].strip()
                            s__ = s_[s_.index("'")+1:]
                            ion, nline = [int(x.strip()) for x in s__.split(" ") if x.strip()]

                            # Determines whether atom or molecule
                            atnumber = int(s[1:s.index(".")])
                            is_atom = atnumber <= 92

                            if is_atom:
                                elstring = f"{elstring:>02}"
                            else:
                                elstring = f"{elstring:>011}"

                            state = EXP_NAME

                        elif EXP_NAME:
                            name = s.strip("'").strip()
                            species = self._get_species(is_atom, elstring, ion, name)

                            a99.get_python_logger().info(
                                 "Loading '{}': species '{}' ('{}')".format(filename, elstring, name))

                            state = EXP_ANY

                    else:
                        if state != EXP_ANY:
                            raise RuntimeError("Not expecting line right now")
                        # It is a line

                        # Read 6 numeric values then something between quotes
                        line = PlezAtomicLine() if is_atom else PlezMolecularLine()

                        # Description string after 6th value is not mandatory
                        if "'" in s:
                            line.lambda_, line.chiex, line.loggf, line.fdamp, line.gu, line.raddmp = \
                                [float(x) for x in s[:s.index("'")].split()]
                        else:
                            line.lambda_, line.chiex, line.loggf, line.fdamp, line.gu, line.raddmp = \
                                [float(x) for x in s.split()]

                        if not is_atom:
                            self._process_line_molecule(species, line, s)

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
            raise
            raise RuntimeError("Error around %d%s row of file '%s': \"%s\"" %
                               (r + 1, a99.ordinal_suffix(r + 1), filename, a99.str_exc(e))) from e

    def _get_species(self, is_atom, elstring, ion, name):
        """Returns PlezSpecies instance, creating one if necessary."""
        list_ = self.atoms if is_atom else self.molecules
        try:
            ret = list_[elstring]
        except KeyError:
            ret = PlezSpecies(elstring, ion, name)
            list_[elstring] = ret
        return ret


    def _do_save_as(self, filename):
        def save_species(h, species):
            a99.write_lf(h, f"'{species.elstring}' {species.ion} {len(species)}")
            a99.write_lf(h, f"'{species.name}'")
            for line in species:
                a99.write_lf(h, f"{line.lambda_:13.3f} {line.chiex:9.3f} {line.loggf:9.3f} {line.fdamp:7.2f} {line.gu:7.1f} {line.raddmp:10.3e}")
        with open(filename, "w") as h:
            for species in self.atoms.values():
                save_species(h, species)
            for species in self.molecules.values():
                save_species(h, species)

    def molecule_by_index(self, i):
        return list(self.molecules.values())[i]

    def atom_by_index(self, i):
        return list(self.atoms.values())[i]

@a99.froze_it
class FilePlezLinelistN14H(FilePlezLinelist):
    """
    Class that can open file "N14H-AX-2011.bsyn.list" (system 'NH A-X PGopher').
    """


    def _do_process_line_molecule(self, species, line, s):

        #'0107.000014          '  1       12150
        #'NH A-X Fernando et al., 2018, JQSRT, 217,29 '
        #   3357.55219    0.004   -2.205 .00    3.  0.000E+00 'qR23(0)        0    1.0  e  F2e  -  0    0.0  e  F3e A            X           '
        #   3349.33946    0.004   -2.625 .00    3.  0.000E+00 'rR3(0)         0    1.0  e  F3e  -  0    0.0  e  F3e       A            X     '

        # Get the branch

        tmp = s[s.index("'"):].strip("'").split()
        _branch = tmp[0]

        line.branch = self.expr_branch.search(_branch).group()
        line.vl = int(tmp[1])
        line.Jl = float(tmp[2])
        line.v2l = int(tmp[6])
        line.J2l = float(tmp[7])


@a99.froze_it
class FilePlezLinelist12C16OLi2015(FilePlezLinelist):
    """
    Class that can open file "12C16O_Hitran.bsyn"

    File "12C16O_Hitran.bsyn" was provided by Masseron in 2023-04 and was converted from Li 2025 HITRAN-format data to
    bsyn (Turbospectrum) data using code so far unknown.

    Complete list of files provided at that time: 12C16O_Hitran.bsyn, 12C17O_Hitran.bsyn, 12C18O_Hitran.bsyn,
    13C16O_Hitran.bsyn, 13C17O_Hitran.bsyn, 13C18O_Hitran.bsyn
    ```
    """

    #'0608.012016          '  1      125497
    #'12C16O Li2015'
    #41558583.29020    8.302   -6.047 .00    3.  0.100E+01 'X' 'X'   0.0    1.0 '     R  0     41   1.0       X1Sigma+  - 41   0.0       X1Sigma+      '
    #40942652.84178    8.161   -6.058 .00    3.  0.100E+01 'X' 'X'   0.0    1.0 '     R  0     40   1.0       X1Sigma+  - 40   0.0       X1Sigma+      '
    #                                                                                 |         |     |                    |     |
    #                                                                            branch        vl    Jl                  v2l   J2l
    #                                                                                 0  1      2     3              4  5  6     7
    #                                                                            0123456789012345678901234567890123456789012345678901234567890123456789
    #                                                                            0         1         2         3         4         5         6

    #'0606.012012 ' 1 24212
    #'EXOMOL '
    #   15000.04111    3.417   -3.130 .00   25.  0.100E+01 'X' 'X'   0.0    1.0 '    23  12.0 F1e  +   b3Sigmag-  - 19  11.0 F2e  -       a3Piu   '
    #   15000.05881    1.724   -8.590 .00   81.  0.100E+01 'X' 'X'   0.0    1.0 '     9  40.0 F1e  +   b3Sigmag-  -  7  39.0 F2e  -       a3Piu   '
    #   15000.15088    1.954   -4.438 .00  139.  0.100E+01 'X' 'X'   0.0    1.0 '     7  69.0 F1f  +   b3Sigmag-  -  6  70.0 F1f  -       a3Piu   '
    #   15000.33324    1.443   -2.043 .00   79.  0.100E+01 'X' 'X'   0.0    1.0 '     5  39.0 F1e  -       A1Piu  -  5  40.0 F0e  +   X1Sigmag+   '
    #   15000.34819    1.954   -4.474 .00  137.  0.100E+01 'X' 'X'   0.0    1.0 '     7  68.0 F0e  +   b3Sigmag-  -  6  69.0 F0e  -       a3Piu   '
    #   15000.36067    2.522   -9.903 .00  185.  0.100E+01 'X' 'X'   0.0    1.0 '     7  92.0 F1e  +   b3Sigmag-  -  2  93.0 F2e  -       a3Piu   '





    # OBS: (2023-04-04) VERY IMPORTANT I think positions 1 and 5 would give further branch information for doublet, triplet etc.


    def _do_process_line_molecule(self, species, line, s):
        # this will give the clean comments section for a line as in sample above
        comments = s.split("'")[5]

        _branch = comments[0:6]
        line.branch = self.expr_branch.search(_branch).group()

        line.vl = int(comments[9:16])
        line.Jl = float(comments[16:22])
        line.v2l = int(comments[40:43])
        line.J2l = float(comments[43:49])


@a99.froze_it
class FilePlezLinelistC2(FilePlezLinelist):
    """
    Deals with .bsyn C2 files (see description).

    This class was made to deal with the following files:
        - 12C12C_15000-17500_P-BR.bsyn
        - 12C13C_15000-17500_P-BR.bsyn
        - 13C13C_15000-17500_P-BR.bsyn
    """

    # '0606.012012 ' 1 24212
    # 'EXOMOL '
    #   15000.04111    3.417   -3.130 .00   25.  0.100E+01 'X' 'X'   0.0    1.0 '    23  12.0 F1e  +   b3Sigmag-  - 19  11.0 F2e  -       a3Piu   '
    #   15000.05881    1.724   -8.590 .00   81.  0.100E+01 'X' 'X'   0.0    1.0 '     9  40.0 F1e  +   b3Sigmag-  -  7  39.0 F2e  -       a3Piu   '
    #   15000.15088    1.954   -4.438 .00  139.  0.100E+01 'X' 'X'   0.0    1.0 '     7  69.0 F1f  +   b3Sigmag-  -  6  70.0 F1f  -       a3Piu   '
    #   15000.33324    1.443   -2.043 .00   79.  0.100E+01 'X' 'X'   0.0    1.0 '     5  39.0 F1e  -       A1Piu  -  5  40.0 F0e  +   X1Sigmag+   '
    #   15000.34819    1.954   -4.474 .00  137.  0.100E+01 'X' 'X'   0.0    1.0 '     7  68.0 F0e  +   b3Sigmag-  -  6  69.0 F0e  -       a3Piu   '
    #   15000.36067    2.522   -9.903 .00  185.  0.100E+01 'X' 'X'   0.0    1.0 '     7  92.0 F1e  +   b3Sigmag-  -  2  93.0 F2e  -       a3Piu   '

    #'0606.012013 ' 1 51113
    #'EXOMOL '
    #   15000.00151    3.598   -5.105 .00  157.  0.100E+01 'X' 'X'   0.0    1.0 '    18  78.0 F0e  +   b3Sigmag-  - 15  79.0 F0e  -       a3Piu   '
    #   15000.00567    0.469   -3.448 .00    3.  0.100E+01 'X' 'X'   0.0    1.0 '     3   1.0 F1f  +   b3Sigmag-  -  2   0.0 F0f  -       a3Piu   '
    #   15000.01264    0.488   -3.181 .00   23.  0.100E+01 'X' 'X'   0.0    1.0 '     3  11.0 F1e  -   b3Sigmag-  -  2  10.0 F0e  +       a3Piu   '
    #   15000.08361    3.396   -2.187 .00   69.  0.100E+01 'X' 'X'   0.0    1.0 '    22  34.0 F0e  +   b3Sigmag-  - 18  34.0 F2f  -       a3Piu   '

    #'0606.013013 ' 1 54388
    #'EXOMOL '
    #   15000.02834    3.306   -2.835 .00   21.  0.100E+01 'X' 'X'   0.0    1.0 '    23  10.0 F1f  -   b3Sigmag-  - 19  10.0 F0e  +       a3Piu   '
    #   15000.06192    1.757   -6.268 .00   95.  0.100E+01 'X' 'X'   0.0    1.0 '     9  47.0 F1f  +   b3Sigmag-  -  7  47.0 F0e  -       a3Piu   '
    #   15000.09163    1.087   -6.495 .00  151.  0.100E+01 'X' 'X'   0.0    1.0 '     1  75.0 F0e  -   b3Sigmag-  -  0  75.0 F1f  +       a3Piu   '
    #   15000.15101    2.122   -6.552 .00  135.  0.100E+01 'X' 'X'   0.0    1.0 '     9  67.0 F0e  -   b3Sigmag-  -  8  66.0 F0e  +       a3Piu   '
    #                                                                                 |     |                        |     |
    #                                                                                vl    Jl                      v2l   J2l
    #                                                                            0123456789012345678901234567890123456789012345678901234567890123456789
    #                                                                            0         1         2         3         4         5         6

    def _do_process_line_molecule(self, species, line, s):
        # this will give the clean comments section for a line as in sample above
        comments = s.split("'")[5]

        line.branch = "-"

        row = [x for x in comments.split(" ") if x]
        line.vl = int(row[0])
        line.Jl = float(row[1])
        line.v2l = int(row[6])
        line.J2l = float(row[7])
        line.from_label = row[4][0]
        line.to_label = row[10][0]
        # line.vl = int(comments[0:6])
        # line.Jl = float(comments[6:12])
        # line.v2l = int(comments[34:37])
        # line.J2l = float(comments[37:43])
        # line.from_label = comments[22]
        # line.to_label = comments[57]


@a99.froze_it
class FilePlezLinelist1(FilePlezLinelistBase):
    """
    Plez molecular lines file having "linelistCN1214V130710.dat" as holotype.
    """

    def __init__(self):
        DataFile.__init__(self)

        self.molecules = {}
        self.atoms = {}

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

