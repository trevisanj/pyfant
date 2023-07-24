"""Parses Brooke 2014 molecular line list"""

__all__ = ["FileBrooke2014"]

import a99, math
from f311 import DataFile
from dataclasses import dataclass

@dataclass
class FileBrooke2014Line:
    # Upper electronic state
    eSl: str
    # Lower electronic state
    eS2l: str
    # Upper state vibrational level
    vl: int
    # Lower state vibrational level
    v2l: int
    # Upper state J level
    Jl: float
    # Lower state J level
    J2l: float
    # Upper state parity
    pl: str
    # Lower state parity
    p2l: str
    # observed wavenumber in cm^-1
    nu_obs: float
    # calculated wavenumber in cm^-1
    nu_calc: float
    # Einstein A value
    A: float
    # Transition description
    Des: str
    # Branch taken from description (above)
    branch: str

    def nu_obs_or_calc(self):
        nu = self.nu_obs
        if math.isnan(nu):
            nu = self.nu_calc
        return nu

@a99.froze_it
class FileBrooke2014(DataFile):
    """
    Brooke 2014 molecular lines file [1]

    Model file CN1214-Brookeetal-2014-list.txt provided by Bertrand Plez [2]. This file contains an introductory
    descriptive text. This class is prepared to load files either with or without this introductory text.

    References:
        [1] Brooke, James SA, et al. "Einstein a coefficients and oscillator strengths for the A2Π–X2Σ+(red)
            and B2Σ+–X2Σ+(violet) systems and rovibrational transitions in the X2Σ+ State of CN."
            The Astrophysical Journal Supplement Series 210.2 (2014): 23.

        [2] https://www.lupm.in2p3.fr/users/plez/
    """

    def __init__(self):
        DataFile.__init__(self)
        self.lines = []

    def __len__(self):
        return len(self.lines)

    def nu_obs_or_calc(self, i):
        """Returns observed or calculated wavenumber.

        Preference is observed, but if not present, returns calculated."""

        return self.lines[i].nu_obs_or_calc()

    def _do_load(self, filename):
        with open(filename, "r") as h:
            state = "line"
            k = -1
            for i, s in enumerate(h):
                try:
                    if i == 0 and s[:5] == "Title":
                        state = "exp_note4"
                    if state == "line":
                        k += 1

                        try:
                            nu_obs = float(s[38:49])
                        except ValueError:
                            nu_obs = float("nan")
                        Des = s[107:118]

                        line = FileBrooke2014Line(nu_obs = nu_obs,
                                                  eSl=s[0:1],
                                                  eS2l=s[2:3],
                                                  vl=int(s[4:6]),
                                                  v2l=int(s[7:9]),
                                                  Jl=float(s[10:15]),
                                                  J2l=float(s[16:21]),
                                                  pl=s[26:27],
                                                  p2l=s[28:29],
                                                  nu_calc=float(s[50:60]),
                                                  A=float(s[81:93]),
                                                  Des=Des,
                                                  branch=Des[1:Des.index("(")],
                                                  )
                        self.lines.append(line)

                    elif state == "exp_note4":
                        if s[:8] == "Note (4)":
                            state = "exp_dashes"
                    elif state == "exp_dashes":
                        if s[:8] == "--------":
                            state = "line"

                except Exception as e:
                    raise RuntimeError("Error around %d%s row of file '%s': \"%s\""%
                                       (i+1, a99.ordinal_suffix(i+1), filename, a99.str_exc(e))) from e


"""
Title: Einstein A Coefficients and Oscillator Strengths for the 
       A^2^{Pi}-X^2^{Sigma}^+^ (red) and B^2^{Sigma}^+^-X^2^{Sigma}^+^ (violet)
       Systems and Rovibrational Transitions in the X^2^{Sigma}^+^ State of CN
Authors: Brooke J.S.A., Ram R.S., Western C.M., Li G.,
         Schwenke D.W., Bernath P.F.
Table: List of observed and calculated positions and calculated intensities of 
       the CN A^2^{Pi}-X^2^{Sigma}^+^ and B^2^{Sigma}^+^-X^2^{Sigma}^+^ systems,
       and X^2^{Sigma}^+^ state rovibrational transitions
================================================================================
Byte-by-byte Description of file: apjs489210t4_mrt.txt
--------------------------------------------------------------------------------
   Bytes Format Units Label  Explanations
--------------------------------------------------------------------------------
       1 A1     ---   eS'    Upper electronic state
       3 A1     ---   eS''   Lower electronic state
   5-  6 I2     ---   v'     Upper state vibrational level
   8-  9 I2     ---   v''    Lower state vibrational level
  11- 15 F5.1   ---   J'     Upper state J level
  17- 21 F5.1   ---   J''    Lower state J level
      23 I1     ---   F'     Upper state F level (1)
      25 I1     ---   F''    Lower state F level (1)
      27 A1     ---   p'     Upper state parity
      29 A1     ---   p''    Lower state parity
  31- 33 A3     ---   N'     Upper state N level
  35- 37 I3     ---   N''    Lower state N level
  39- 49 F11.5  ---   Obs    ? Observed transition position (2)
  51- 60 F10.4  ---   Cal    Position calculated by PGOPHER (3)
  62- 69 F8.5   ---   Res    ? Observed - calculated position
  71- 80 F10.4  ---   E''    Lower state energy calculated by PGOPHER (4)
  82- 93 E12.6  ---   A      Einstein A value
  95-106 E12.6  ---   f      The f-value
 108-118 A11    ---   Des    Transition description
--------------------------------------------------------------------------------
Note (1): In the A state, F=1 refers to omega=0.5, and F=2 to omega=1.5. In 
          the B and X states, F=1 refers to e parity, and F=2 to f parity.
Note (2): Blank if line not observed in any study.
Note (3): Using constants published in ????
Note (4): Relative to v''=0 band origin.
--------------------------------------------------------------------------------
A X  0  0   1.5   2.5 1 1 e e       2  9082.98330  9082.9702  0.01313    11.3536  7.685729E+3  9.310961E-5 pP1(2.5)
A X  0  0   2.5   3.5 1 1 e e       3  9079.91520  9079.8980  0.01723    22.7030  1.152579E+4  1.571904E-4 pP1(3.5)
A X  0  0   3.5   4.5 1 1 e e       4  9076.35990  9076.3587  0.00119    37.8337  1.405716E+4  2.046548E-4 pP1(4.5)
A X  0  0   4.5   5.5 1 1 e e       5  9072.35580  9072.3561 -0.00032    56.7451  1.596585E+4  2.423418E-4 pP1(5.5)
A X  0  0   5.5   6.5 1 1 e e       6  9067.89420  9067.8947 -0.00046    79.4362  1.751230E+4  2.736789E-4 pP1(6.5)
"""
