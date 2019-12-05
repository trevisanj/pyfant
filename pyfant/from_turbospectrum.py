"""
TurboSpectrum-to-PFANT conversions
"""

__all__ = ["turbospectrum_to_atoms"]

import csv
import a99
import sys
import pyfant

# Comparison of same atomic line
#
#--|PFANT begin|--
#LI1   4601.843
#1.8479 -5.804 3e-32 0 0 0.1 1 0
#(kiex algf ch gr ge zinf abondr finrai)
#--|PFANT end|--
#
#--|TurboSpectrum begin|--
#' 3.000              '    1       110
#'Li I '
#  4601.843  1.848  -5.804  2.50    6.0  5.01E+07 'p' 'f'   0.0    1.0 'Li I    2p  2P    4f  2F     SEN    '
# 16814.155  4.541  -2.790 -5.54    2.0  3.02e+07 'x' 'x' 0.0 1.0 'LI  I   4d  2D      11p  2P   '

#--|TurboSpectrum end|--

_Symbols = ['H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne', 'Na', 'Mg', 'Al', 'Si', 'P', 'S',
            'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga',
            'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd',
            'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd', 'Pm',
            'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os',
            'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
            'Pa', 'U']

# File reader states
_X_EL0 = 0  # expecting first line of element specification
_X_EL1 = 1  # expecting second line of element specification
_X_LINE_OR_EL0 = 2  # expecting line data


def turbospectrum_to_atoms(file_obj):
    """
    Converts data from a TurboSpectrum file into a FileAtoms object.

    Args:
      file_obj: file-like object, e.g., returned by open()

    Returns: a FileAtoms object
    """

    _logger = a99.get_python_logger()

    def log_skipping(r, reason, row):
        _logger.info("Skipping row #%d (%s)" % (r, reason))
        _logger.info(str(row))

    ret = pyfant.FileAtoms()
    edict = {}  # links atomic symbols with Atom objects created (key is atomic symbol + ionization)
    r = 0  # number of current row
    num_skip_ioni, num_skip_mol = 0, 0
    state = _X_EL0
    try:
        for row in file_obj:
            r += 1

            if state < _X_LINE_OR_EL0:
                if row[0] != "'":
                    raise ParseError("Expecting element specification, but found something else")

            if state == _X_EL0:
                #' 3.000              '    1       110
                #0123456
                elem = _Symbols[int(row[1:3])]
                ioni = int(row[4:7])+1
                state = _X_EL1
            elif state == _X_EL1:
                state = _X_LINE_OR_EL0
            elif state == _X_LINE_OR_EL0:
                if row[0] == "'":
                    elem = _Symbols[int(row[1:3])]
                    ioni = int(row[4:7]) + 1
                    state = _X_EL1
                else:
                    if ioni > 2:
                        # log_skipping(r, "ionization > 2", row)
                        num_skip_ioni += 1
                        continue

                    #'Li I '
                    #  4601.843  1.848  -5.804  2.50    6.0  5.01E+07 'p' 'f'   0.0    1.0 'Li I    2p  2P    4f  2F     SEN    '
                    #0         1         2         3
                    #01234567890123456789012345678901234567890

                    rr = row.split()

                    _waals = float(rr[3])
                    if _waals > 0:
                        _waals = 0

                    line = pyfant.AtomicLine()
                    line.lambda_ = float(rr[0])
                    line.kiex = float(rr[1])
                    line.algf = float(rr[2])
                    if _waals == 0:
                        line.ch = 0.3e-31
                    else:
                        try:
                            # Formula supplied by Elvis Cantelli:
                            # extracted from cross-entropy code by P. Barklem
                            line.ch = 10**(2.5*_waals-12.32)
                        except:
                            # Catches error to log _waals value that gave rise to error
                            _logger.critical("Error calculating ch: waals=%g" % _waals)
                            raise

                    # Setting gr to zero will cause PFANT to calculate it using a formula.
                    # See pfantlib.f90::read_atoms() for the formula.
                    line.gr = 0.0
                    # ge is not present in VALD3 file.
                    # it enters as a multiplicative term in popadelh(). The original
                    # atom4070g.dat and atoms.dat all had ge=0 for all lines.
                    line.ge = 0.0
                    # Attention: zinf must be tuned later using tune-zinf.py
                    line.zinf = 0.5
                    # Never used in PFANT
                    line.abondr = 1

                    key = f"{elem:2}{ioni:1}"  # will group elements by this key
                    if key in edict:
                        a = edict[key]
                    else:
                        a = edict[key] = pyfant.Atom()
                        a.elem = pyfant.adjust_atomic_symbol(elem)
                        a.ioni = ioni
                        ret.atoms.append(a)
                    a.lines.append(line)

    except Exception as e:
        raise type(e)(("Error around %d%s row of TurboSpectrum file" %
            (r, a99.ordinal_suffix(r)))+": "+str(e)).with_traceback(sys.exc_info()[2])
    _logger.debug("VALD3-to-atoms conversion successful!")
    _logger.info("Number of lines skipped (molecules): %d" % num_skip_mol)
    _logger.info("Number of lines skipped (ioni > 2): %d" % num_skip_ioni)
    _logger.debug("Number of (element+ioni): %s" % len(ret))
    _logger.debug("Total number of atomic lines: %d" % (sum(len(a) for a in ret.atoms),))
    return ret




