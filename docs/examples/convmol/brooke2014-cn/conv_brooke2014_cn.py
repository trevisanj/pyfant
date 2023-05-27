# Example script of how to convert Brooke 2014 molecular linelist to PFANT format

import pyfant, a99, os

#=== BEGIN SETUP ===

INPUTFILENAME = "CN1214-Brookeetal-2014-list-sample.txt"
FE = None  # Line strength scaling factor for the whole molecule
SYSTEMID = "CN [A 2 Pi - X 2 Sigma]"  # Use moldbed.py to find out

_temp = os.path.split(INPUTFILENAME)[1]
outputfilename = _temp[:_temp.index(".")]+".PFANT.dat"

#=== END SETUP

#=== BEGIN CONVERSION ===

fmoldb = pyfant.FileMolDB()
try:
    fmoldb.load(fmoldb.default_filename)
except FileNotFoundError:
    fmoldb.init_default()

molconsts = fmoldb.get_molconsts(SYSTEMID)
molconsts.None_to_zero()

f = pyfant.FileBrooke2014()
f.load(INPUTFILENAME)


converter = pyfant.ConvBrooke2014(comment=f"from {INPUTFILENAME}",
                              molconsts=molconsts,
                              flag_quiet=True,
                              fe=FE)
fmol, log = converter.make_file_molecules(f)
for line in str(log).split("\n"):
    a99.get_python_logger().info(line)
fmol.save_as(outputfilename)

#=== END CONVERSION ===
