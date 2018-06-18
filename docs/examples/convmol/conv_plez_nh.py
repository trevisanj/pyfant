"""Converts Plez's Turbospectrum file to PFANT format.

Requires Turbospectrum linelist file 'N14H-AX-2011.bsyn.list' (system 'NH A-X PGopher').
"""

import pyfant


fmoldb = pyfant.FileMolDB()
fmoldb.init_default()

molconsts = fmoldb.get_molconsts("NH [A 3 Pi - X 3 Sigma]")
molconsts.None_to_zero()

fplez = pyfant.FilePlezLinelist()
fplez.load("N14H-AX-2011.bsyn.list")

converter = pyfant.ConvPlez(name="NH A-X PGopher", molconsts=molconsts)


fmol, log = converter.make_file_molecules(fplez)
fmol.save_as("nh-converted.dat")