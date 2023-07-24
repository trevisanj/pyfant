from .calc_qgbd import *
import datetime
from collections import OrderedDict
import math
import pyfant
import a99
from enum import Enum

__all__ = ["Conv", "ConvMode"]


# _DEFAULT_QGBD_CALCULATOR = calc_qgbd_tio_like


class ConvMode(Enum):
    # Hönl-London factors
    HLF = 1
    # Einstein's "A" coefficient (1/s)
    EINSTEIN = 2
    EINSTEIN_MINIMAL = 3
    # Oscillator strength (f_(Jl,J2l)-falue)
    F = 4


class Conv(object):
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

        molconsts: a dict-like object combining field values from tables 'molecule', 'state',
                    'pfantmol', and 'system' from a FileMolDB database

        flag_norm_sj: Whether to multiply calculated SJ's by normalization factor

        fcfs: Franck-Condon Factors (dictionary of floats indexed by (vl, v2l))

        flag_quiet: Will not log exceptions when a molecular line fails

        flag_special_fcf: check _get_fcf() for formula: transforms any number <n> into 0.<n>; no idea why. This was some
                          Kurucz conversion 2017 thing

        molcomment: comments to be added to molecule description

        fe: (=None) if used, replaces "fe" from molecular constants

        do: (=None) if used, replaces "do" from molecular constants

        fact: (=None) if used, replaces default pyfant.SetOfLines.fact

        strengthfactor: (=1.) all resulting line strengths ("sj") will be multiplied by this factor
                        Note: it is better to use "fe" argument instead
        flag_fcf: Whether to multiply calculated gf's by Franck-Condon Factor
                  (only makes sense when mode==ConvMode.HLF)

        flag_filter_labels: whether to filter lines by labels [taken from self.molconsts e.g. ("A", "X")].

        moldb: FileMolDB instance to automatically get information from (for example will take FCF's if needed)

        inputfilename: if passed, will be included in FileMolecules.titm

    Both strengthfactor and fe are ways to achieve the same result (multiply the line strength), but the former applies
    to sj whereas the latter is recorded as the molecule's "FE"
    """

    def __init__(self, mode=ConvMode.HLF, molconsts=None, flag_norm_sj=True, fcfs=None,
                 flag_quiet=True, fe=None, do=None, fact=None,
                 flag_special_fcf=False, molcomment="", strengthfactor=1.,
                 flag_fcf=False, flag_filter_labels=False, moldb=None, inputfilename=None):
        self.mode = mode
        # self.qgbd_calculator = qgbd_calculator if qgbd_calculator else calc_qgbd_tio_like
        self.molconsts = molconsts
        self.fcfs = fcfs
        self.flag_norm_sj = flag_norm_sj
        self.flag_quiet = flag_quiet
        self.molcomment = molcomment
        self.fe = fe
        self.do = do
        self.fact = fact
        self.flag_special_fcf = flag_special_fcf
        self.strengthfactor = strengthfactor
        self.flag_fcf = flag_fcf
        self.flag_filter_labels = flag_filter_labels
        self.inputfilename = inputfilename

        if flag_fcf and fcfs is None:
            if not moldb:
                raise ValueError("flag_fcf==True, fcfs==None but moldb not provided to automatically get Franck-Condon factors!")
            self.fcfs = moldb.get_fcf_dict(molconsts["id_system"])
            if len(self.fcfs) == 0:
                raise RuntimeError("Frank-Condon factors not available")

        # These will be filled in upon conversion
        self.sols = None
        self.log = None
        self.mtools = None

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
        self.sols = {}
        self.log = pyfant.MolConversionLog()
        self._make_sols(lines)

        sols_list = list(self.sols.values())
        sols_list.sort(key= lambda sol: sol.vl*1000+sol.v2l)

        mol = pyfant.molconsts_to_molecule(self.molconsts)

        if self.fe:
            mol.fe = self.fe
        if self.do:
            mol.do = self.do
        if self.molcomment:
            mol.description += f"; {self.molcomment}"

        mol.sol = sols_list
        f = pyfant.FileMolecules()
        now = a99.dt2str(datetime.datetime.now())

        fromfile = ""
        if self.inputfilename:
            fromfile = f" from file '{self.inputfilename}'"

        f.titm = f"Converted using pyfant.{self.__class__.__name__} @ {now}{fromfile}"
        f.molecules = [mol]
        return f

    def kovacs_toolbox(self):
        """Wraps f311.physics.multiplicity.kovacs_toolbox()"""
        return pyfant.kovacs_toolbox(self.molconsts, flag_normalize=self.flag_norm_sj)

    def append_line(self, line, gf_pfant, branch):
        """Use to append line to object"""
        self.append_line2(line.vl, line.v2l, line.lambda_, gf_pfant, line.J2l, branch)

    def append_line2(self, vl, v2l, lambda_, sj, jj, branch):
        """Alernative way to append line, created in 2023. Takes (vl, v2l) and PFANT relevant line-specific info.

        append_line() requires a "line" object which made sense when ConvKurucz was implemented, but unelegant when one
        already has all the values loose as variables.

        Arguments are as in PFANT molecular linelist files. See filemolecules.py and pfantlib.f90::file_molecules
        module.
        """
        sol_key = (vl, v2l)

        if self.flag_fcf and sol_key not in self.fcfs:
            raise KeyError("FCF not available for (vl, v2l) = ({}, {})".format(vl, v2l))

        if sol_key not in self.sols:
            qv = self.fcfs[sol_key] if self.flag_fcf else 1.
            gbd = calc_gbd(self.molconsts, v2l)  # self.qgbd_calculator(self.molconsts, v2l)
            self.sols[sol_key] = pyfant.SetOfLines(vl, v2l, qv, gbd["gv"], gbd["bv"], gbd["dv"],
                                                   fact=1. if self.fact is None else self.fact)

        self.sols[sol_key].append_line(lambda_, sj*self.strengthfactor, jj, branch)

        self.log.cnt_in += 1

    # Must reimplement this
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

    def get_hlf(self, vl, v2l, J2l, branch):
        """Calculates SJ Hönl-London factor according to Kovács formulation.

        Returns:
            sj
        """

        if self.mtools is None:
            self.mtools = self.kovacs_toolbox()

        sj = self.mtools.get_sj(vl, v2l, J2l, branch)
        if sj < 0:
            raise ValueError("Negative SJ")

        return sj

    @staticmethod
    def get_sj_einstein(A, Jl, J2l, S2l, deltak, nu):
        """Calculates SJ and wavelength using Einstein's coefficient "A"."""
        normalizationfactor = Conv.get_normalizationfactor(J2l, S2l, deltak)
        SJ = normalizationfactor*A*1.499*(2*Jl+1)/nu**2
        return SJ

    @staticmethod
    def get_normalizationfactor(J2l, S2l, deltak):
        ret = 1/((2*S2l+1)*(2*J2l+1)*(2-deltak))
        return ret

    # (20230719) This is not used ATM
    def _get_fcf(self, vl, v2l):
        try:
            fcf = self.fcfs[(vl, v2l)]

            if self.flag_special_fcf:
                fcf = fcf * 10 ** -(math.floor(math.log10(fcf)) + 1)

        except KeyError as e:
            raise KeyError("FCF not available for (vl, v2l) = ({}, {})".format(vl, v2l))
        return fcf



########################################################################################################################

def calc_gbd(molconsts, v_lo):
    """
    Calculates gv, bv, dv

    Based on Fortran source 'agrup.plez7.f'

    Args:
        molconsts: dict-like object with keys:
            "omega_e"
            "omega_ex_e"
            "omega_ey_e"
            "B_e"
            "alpha_e"
            "D_e"
            "beta_e"

        v_lo: (integer) low transition level

    Returns: bdg, i.e., a dictionary with keys:
            "gv", "bv", "dv", "gzero"
    """

    omega_e = molconsts["state2l_omega_e"]
    omega_ex_e = molconsts["state2l_omega_ex_e"]
    omega_ey_e = molconsts["state2l_omega_ey_e"]
    B_e = molconsts["state2l_B_e"]
    D_e = molconsts["state2l_D_e"]
    alpha_e = molconsts["state2l_alpha_e"]
    beta_e = molconsts["state2l_beta_e"]

    if int(v_lo) != v_lo:
        raise ValueError("Argument 'v_lo' must be an integer")

    gzero = omega_e / 2.0 - omega_ex_e / 4.0 + omega_ey_e / 8.0
    v_lo5 = v_lo + 0.5

    # rotational constant "B_v"
    bv = B_e - alpha_e * v_lo5
    # rotational constant "D_v"
    dv = (D_e + beta_e * v_lo5) * 1.0e+06
    # rotational term " G_A"
    gv = omega_e * v_lo5 - omega_ex_e * v_lo5 ** 2 + omega_ey_e * v_lo5 ** 3 - gzero

    gbd = {"gv": gv, "bv": bv, "dv": dv, "gzero": gzero}

    return gbd
