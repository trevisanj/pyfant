# Example script of how to convert HITRAN molecular linelist to PFANT format

from f311 import hapi
import pyfant, a99, os

#=== BEGIN SETUP ===

DATADIR = "."  # where hapi will look for ".par" files
DATANAME = "CO_dV11_stable-sample"  # filename minus ".par" extension
ISOWANT = 1  # see ConvHitran class
FE = None  # Line strength scaling factor for the whole molecule
SYSTEMDESCR = "CO [X 1 Sigma - X 1 Sigma]"  # Use moldbed.py --> "System description" box

#=== END SETUP

#=== BEGIN CONVERSION ===

fmoldb = pyfant.FileMolDB()
try:
    fmoldb.load(os.path.join(DATADIR, fmoldb.default_filename))
except FileNotFoundError:
    fmoldb.init_default()

molconsts = fmoldb.get_molconsts(SYSTEMDESCR)
molconsts.None_to_zero()

hapi.VARIABLES['BACKEND_DATABASE_NAME'] = DATADIR
hapi.loadCache()

hapidata = hapi.LOCAL_TABLE_CACHE[DATANAME]

converter = pyfant.ConvHITRAN(comment=f"from {DATANAME}, iso={ISOWANT}",
                              molconsts=molconsts,
                              flag_quiet=True,
                              isowant=ISOWANT,
                              fe=FE)
fmol, log = converter.make_file_molecules(hapidata)
for line in str(log).split("\n"):
    a99.get_python_logger().info(line)
fmol.save_as(f"{DATANAME}.PFANT.dat")

#=== END CONVERSION ===
