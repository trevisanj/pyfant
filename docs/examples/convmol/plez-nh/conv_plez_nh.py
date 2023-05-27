"""
Converts Plez's Turbospectrum file to PFANT format using sample file derived from 'N14H-AX-2011.bsyn.list' (system 'NH A-X PGopher').
"""

import pyfant, os

INPUTFILENAME = "N14H-AX-2011-sample.bsyn.list"

_temp = os.path.split(INPUTFILENAME)[1]
outputfilename = _temp[:_temp.index(".")]+".PFANT.dat"

fmoldb = pyfant.FileMolDB()
try:
    fmoldb.load()
except FileNotFoundError:
    fmoldb.init_default()

molconsts = fmoldb.get_molconsts("NH [A 3 Pi - X 3 Sigma]")
molconsts.None_to_zero()

fplez = pyfant.FilePlezLinelistN14H()
fplez.load(INPUTFILENAME)

# Obs: name must match species name in original bsyn file
converter = pyfant.ConvPlez(name="NH A-X PGopher", molconsts=molconsts)

fmol, log = converter.make_file_molecules(fplez)
fmol.save_as(outputfilename)
