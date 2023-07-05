import pyfant
from .calc_qgbd import *
from .convlog import *
import datetime
from collections import OrderedDict
import math
import pyfant
from enum import Enum

__all__ = ["Conv", "ConvSols", "ConvMode"]


_DEFAULT_QGBD_CALCULATOR = calc_qgbd_tio_like

class ConvMode(Enum):
    HLF =1
    EINSTEIN = 2
    EINSTEIN_MINIMAL = 3

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
        mode: specifies how SJ's are calculated:
                ConvMode.HLF: using Honl-London factors using Kovácz formulation
                ConvMode.EINSTEIN: using Einstein's "A" coefficients (given in s^-1)
                ConvMode.EINSTEIN_MINIMAL: using Einstein's "A" coefficients (given in s^-1); and
                                           assuming vl=0, v2l=0, J2l=Jl. Experimental conversion using minimal data
                                           from Plez linelist

                **Note** mode is handles by subclasses and may be partially implemented or ignored. The code
                         (e.g. conv_brooke2014.py) must be checked for class-specific behaviour

        qgbd_calculator: callable that can calculate "qv", "gv", "bv", "dv",
                         Default: calc_qbdg_tio_like

        molconsts: a dict-like object combining field values from tables 'molecule', 'state',
                    'pfantmol', and 'system' from a FileMolDB database

        flag_norm_sj: Whether to multiply calculated SJ's by normalization factor

        fcfs: Franck-Condon Factors (dictionary of floats indexed by (vl, v2l))

        flag_quiet: Will not log exceptions when a molecular line fails

        flag_special_fcf: check _get_fcf() for formula: transforms any number <n> into 0.<n>; no idea why. This was some
                          Kurucz conversion 2017 thing

        fe: (=None) if used, replaces fe from molecular constants

        strengthfactor: (=1.) all resulting line strengths ("sj") will be multiplied by this factor
                        Note: it is better to use "fe" argument instead
        flag_fcf: Whether to multiply calculated gf's by Franck-Condon Factor
                  (only makes sense when mode==ConvMode.HLF)

        flag_filter_labels: whether to filter lines by labels [taken from self.molconsts e.g. ("A", "X")].

        moldb: FileMolDB instance to automatically get information from (for example will take FCF's if needed)

    Both strengthfactor and fe are ways to achieve the same result (multiply the line strength), but the former applies
    to sj whereas the latter is recorded as the molecule's "FE"
    """

    def __init__(self, mode=ConvMode.HLF, qgbd_calculator=None, molconsts=None, flag_norm_sj=True, fcfs=None,
                 flag_quiet=False, fe=None, flag_special_fcf=False, comment="", strengthfactor=1., flag_fcf=False,
                 flag_filter_labels=True,
                 moldb=None):
        self.mode = mode
        self.qgbd_calculator = qgbd_calculator if qgbd_calculator else calc_qgbd_tio_like
        self.molconsts = molconsts
        self.fcfs = fcfs
        self.flag_norm_sj = flag_norm_sj
        self.flag_quiet = flag_quiet
        self.comment = comment
        self.fe = fe
        self.flag_special_fcf = flag_special_fcf
        self.strengthfactor = strengthfactor
        self.flag_fcf = flag_fcf
        self.flag_filter_labels = flag_filter_labels

        if flag_fcf and fcfs is None:
            if not moldb:
                raise ValueError("flag_fcf==True, fcfs==None but moldb not provided to automatically get Franck-Condon factors!")
            self.fcfs = moldb.get_fcf_dict(molconsts["id_system"])

        # These will be filled in upon conversion
        self.sols = None
        self.log = None
        self.mtools = None

    @staticmethod
    def get_sj_einstein(A, Jl, J2l, S2l, deltak, nu, strengthfactor):
        """Calculates SJ and wavelength using Einstein's coefficient "A"."""
        normalizationfactor = Conv.get_normalizationfactor(J2l, S2l, deltak, strengthfactor)
        SJ = normalizationfactor*A*1.499*(2*Jl+1)/nu**2
        return SJ

    @staticmethod
    def get_normalizationfactor(J2l, S2l, deltak, strengthfactor):
        ret = strengthfactor/((2*S2l+1)*(2*J2l+1)*(2-deltak))
        return ret
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
        self.sols = pyfant.ConvSols(self.qgbd_calculator, self.molconsts)
        self.log = pyfant.MolConversionLog()
        self._make_sols(lines)

        sols_list = list(self.sols.values())
        sols_list.sort(key= lambda sol: sol.vl*1000+sol.v2l)

        mol = pyfant.molconsts_to_molecule(self.molconsts)
        if self.fe: mol.fe = self.fe
        if self.comment: mol.description += f"; {self.comment}"
        mol.sol = sols_list
        f = pyfant.FileMolecules()
        now = datetime.datetime.now()
        f.titm = "PFANT molecular lines file. Created by f311.convmol.Conv.make_file_molecules() @ {}".format(now.isoformat())
        f.molecules = [mol]
        return f

    def kovacs_toolbox(self):
        """Wraps f311.physics.multiplicity.kovacs_toolbox()"""
        return pyfant.kovacs_toolbox(self.molconsts, flag_normalize=self.flag_norm_sj)

    # Must reimplement thig
    def _make_sols(self, lines):
        """Converts molecular lines into a list of SetOfLines object

        Args:
            lines: see make_file_molecules()

        Returns:
            None
        """
        raise NotImplementedError()

    ######
    # Gear

    def _calculate_qgbd(self, v2l):
        return self.qgbd_calculator(self.molconsts, v2l)

    def _get_fcf(self, vl, v2l):
        try:
            fcf = self.fcfs[(vl, v2l)]

            if self.flag_special_fcf:
                fcf = fcf * 10 ** -(math.floor(math.log10(fcf)) + 1)

        except KeyError as e:
            raise KeyError("FCF not available for (vl, v2l) = ({}, {})".format(vl, v2l))
        return fcf

    def _get_hlf(self, vl, v2l, J2l, branch):
        """Calculates SJ Hönl-London factor according to Kovács formulation.

        Returns:
            SJ, flag_error
        """
        flag_error = False

        if self.mtools is None:
            self.mtools = self.kovacs_toolbox()

        SJ = self.strengthfactor
        try:
            hlf = self.mtools.get_sj(vl, v2l, J2l, branch)
        except pyfant.NoLineStrength as e:
            self.log.skip_reasons[str(e)] += 1
            flag_error = True
        else:
            if hlf < 0:
                self.log.skip_reasons["Negative SJ"] += 1
                flag_error = True
            else:
                SJ *= hlf

                if self.flag_fcf:
                    try:
                        SJ *= self._get_fcf(vl, v2l)
                    except KeyError as e:
                        self.log.skip_reasons[str(e)] += 1
                        flag_error = True

        return SJ, flag_error
