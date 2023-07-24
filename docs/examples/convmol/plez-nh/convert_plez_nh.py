"""
Converts Plez's Turbospectrum file to PFANT format using sample file derived from 'N14H-AX-2011.bsyn.list'
(system 'NH A-X PGopher').
"""

import pyfant, os, a99

#=== BEGIN SETUP ===

INPUTFILENAME = "N14H-AX-2011-sample.bsyn.list"
SYSTEMDESCR = "NH [A 3 Pi - X 3 Sigma]"

_temp = os.path.split(INPUTFILENAME)[1]
outputfilename = _temp[:_temp.index(".")]+".PFANT.dat"

#=== END SETUP

#=== BEGIN CONVERSION ===


fmoldb = pyfant.FileMolDB()
try:
    fmoldb.load()
except FileNotFoundError:
    fmoldb.init_default()

molconsts = fmoldb.get_molconsts(SYSTEMDESCR)
molconsts.None_to_zero()

fplez = pyfant.FilePlezLinelistN14H()
fplez.load(INPUTFILENAME)

# Obs: name must match species name in original bsyn file
converter = pyfant.ConvPlez(species="0107.000014",
                            molconsts=molconsts,)

fmol = converter.make_file_molecules(fplez)

for line in str(converter.log).split("\n"):
    a99.get_python_logger().info(line)


fmol.save_as(outputfilename)

#=== END CONVERSION ===