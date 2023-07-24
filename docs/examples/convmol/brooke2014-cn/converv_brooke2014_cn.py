# Example script of how to convert Brooke 2014 molecular linelist to PFANT format

import pyfant, a99, os

#=== BEGIN SETUP ===

INPUTFILENAME = "CN1214-Brookeetal-2014-list-sample.txt"
FE = 2.  # Line strength scaling factor for the whole molecule
SYSTEMDESCR = "CN [A 2 Pi - X 2 Sigma]"  # Use moldbed.py --> "System description" box

_temp = os.path.split(INPUTFILENAME)[1]
outputfilename = _temp[:_temp.index(".")]+".PFANT.dat"

#=== END SETUP

#=== BEGIN CONVERSION ===

fmoldb = pyfant.FileMolDB()
try:
    fmoldb.load(fmoldb.default_filename)
except FileNotFoundError:
    fmoldb.init_default()

molconsts = fmoldb.get_molconsts(SYSTEMDESCR)
molconsts.None_to_zero()

f = pyfant.FileBrooke2014()
f.load(INPUTFILENAME)


converter = pyfant.ConvBrooke2014(molcomment=f"from {INPUTFILENAME}",
                                  mode=pyfant.ConvMode.HLF,
                                  molconsts=molconsts,
                                  flag_quiet=True,
                                  fe=FE,)
fmol = converter.make_file_molecules(f)
for line in str(converter.log).split("\n"):
    a99.get_python_logger().info(line)
fmol.save_as(outputfilename)

#=== END CONVERSION ===
