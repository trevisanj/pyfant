import pyfant
from .calc_qgbd import *
from .convlog import *
import datetime
from collections import OrderedDict
import math
import pyfant

__all__ = ["Conv", "ConvSols"]


_DEFAULT_QGBD_CALCULATOR = calc_qgbd_tio_like


class ConvSols(OrderedDict):
    """Stores (vl, v2l) as keys, SetOfLines as values"""

    def __init__(self, qgbd_calculator, molconsts):
        OrderedDict.__init__(self)
        self.qgbd_calculator = qgbd_calculator if qgbd_calculator else _DEFAULT_QGBD_CALCULATOR
        self.molconsts = molconsts

    def append_line(self, line, gf_pfant, branch):
        """Use to append line to object"""
        sol_key = (line.vl, line.v2l)

        if sol_key not in self:
            qgbd = self.qgbd_calculator(self.molconsts, line.v2l)
            self[sol_key] = pyfant.SetOfLines(line.vl, line.v2l,
                                          qgbd["qv"], qgbd["gv"], qgbd["bv"], qgbd["dv"], 1.)

        self[sol_key].append_line(line.lambda_, gf_pfant, line.J2l, branch)

    def append_line2(self, vl, v2l, lambda_, sj, jj, branch):
        """Alernative way to append line, created in 2023. Takes (vl, v2l) and PFANT relevant line-specific info.

        append_line() requires a "line" object which made sense when ConvKurucz was implemented, but unelegant when one
        already has all the values loose as variables.

        Arguments are as in PFANT molecular linelist files. See filemolecules.py and pfantlib.f90::file_molecules
        module.
        """
        sol_key = (vl, v2l)

        if sol_key not in self:
            qgbd = self.qgbd_calculator(self.molconsts, v2l)
            self[sol_key] = pyfant.SetOfLines(vl, v2l, qgbd["qv"], qgbd["gv"], qgbd["bv"], qgbd["dv"], 1.)
        self[sol_key].append_line(lambda_, sj, jj, branch)


class Conv(object):
    # TODO there is a good chance that flag_hlf, flag_fcf, etc. will be moved to this class
    """Molecular lines converter base class

    Args:
        qgbd_calculator: callable that can calculate "qv", "gv", "bv", "dv",
                         Default: calc_qbdg_tio_like

        molconsts: a dict-like object combining field values from tables 'molecule', 'state',
                    'pfantmol', and 'system' from a FileMolDB database

        flag_normhlf: Whether to multiply calculated gf's by normalization factor

        fcfs: Franck-Condon Factors (dictionary of floats indexed by (vl, v2l))

        flag_quiet: Will not log exceptions when a molecular line fails

        fe: (=None) if used, replaces fe from molecular constants

    """

    def __init__(self, qgbd_calculator=None, molconsts=None, flag_normhlf=True, fcfs=None, flag_quiet=False, fe=None,
                 comment=""):
        self.qgbd_calculator = qgbd_calculator if qgbd_calculator else calc_qgbd_tio_like
        self.molconsts = molconsts
        self.fcfs = fcfs
        self.flag_normhlf = flag_normhlf
        self.flag_quiet = flag_quiet
        self.comment = comment
        self.fe = fe

    @staticmethod
    def get_sj_einstein(A, Jl, J2l, S2l, deltak, nu, strengthfactor):
        """Calculates SJ and wavelength using Einstein's coefficient "A"."""
        normalizationfactor = strengthfactor/((2*S2l+1)*(2*J2l+1)*(2-deltak))
        SJ = normalizationfactor*A*1.499*(2+Jl+1)/nu**2
        return SJ

    def make_file_molecules(self, lines):
        """
        Builds a FileMolecules object

        Args:
            lines: in most cases, a DataFile instance, but may be anything, since the molecular
                   lines data extraction is performed by a particular descendant class.
                   For example, the HITRAN converter expects a structure from the HAPI

        Returns:
            f, log: FileMolecules, MolConversionLog instances
        """


        # Runs specific conversor to SetOfLines
        sols = pyfant.ConvSols(self.qgbd_calculator, self.molconsts)
        log = pyfant.MolConversionLog()
        self._make_sols(sols, log, lines)

        assert isinstance(sols, ConvSols)
        assert isinstance(log, MolConversionLog)

        sols_list = list(sols.values())
        sols_list.sort(key= lambda sol: sol.vl*1000+sol.v2l)

        mol = pyfant.molconsts_to_molecule(self.molconsts)
        if self.fe: mol.fe = self.fe
        if self.comment: mol.description += f"; {self.comment}"
        mol.sol = sols_list
        f = pyfant.FileMolecules()
        now = datetime.datetime.now()
        f.titm = "PFANT molecular lines file. Created by f311.convmol.Conv.make_file_molecules() @ {}".format(now.isoformat())
        f.molecules = [mol]
        return f, log

    def kovacs_toolbox(self):
        """Wraps f311.physics.multiplicity.kovacs_toolbox()"""
        return pyfant.kovacs_toolbox(self.molconsts, flag_normalize=self.flag_normhlf)

    # Must reimplement thig
    def _make_sols(self, sols, log, lines):
        """Converts molecular lines into a list of SetOfLines object

        Args:
            sols: ConvSols
            log: MolConversionLog
            lines: see make_file_molecules()

        Returns:
            None
        """
        raise NotImplementedError()

    ######
    # Gear

    def _calculate_qgbd(self, v2l):
        return self.qgbd_calculator(self.molconsts, v2l)

    def _get_fcf(self, vl, v2l, flag_special=False):
        try:
            fcf = self.fcfs[(vl, v2l)]

            if flag_special:
                fcf = fcf * 10 ** -(math.floor(math.log10(fcf)) + 1)

        except KeyError as e:
            raise KeyError("FCF not available for (vl, v2l) = ({}, {})".format(vl, v2l))
        return fcf
