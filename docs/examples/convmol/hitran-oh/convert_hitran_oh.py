"""
Example script showing how to convert HITRAN 160-column linelist to PFANT format
"""
import pyfant, tabulate, a99, os

a99.flag_log_file = True

#=== BEGIN SETUP ===

DATADIR = "."
INPUTFILENAME = "64a47086-sample.par"
ISOWANT = 1  # Isotopologue: use HITRAN website to find out. IN this case they are: {1: "16OH", 2: "18OH", 3: "16OD"}
SYSTEMID = "OH [X 2 Pi]"  # Use moldbed.py to find out
STRENGTHFACTOR = 1.
FE = 1.

#=== END SETUP

#=== BEGIN CONVERSION ===

# Loads molecules db file, or creates new
fmoldb = pyfant.FileMolDB()
try:
    fmoldb.load(os.path.join(DATADIR, fmoldb.default_filename))
except FileNotFoundError:
    fmoldb.init_default()
molconsts = fmoldb.get_molconsts(SYSTEMID)
molconsts.None_to_zero()


# Shows values of molecular constants
rows = []
names = ["beta_e", "omega_ey_e", "D_e", "B_e", "omega_ex_e", "omega_e", "alpha_e"]
for name in names:
    unicodename = a99.greek_to_unicode_all(name)
    rows.append([unicodename, molconsts["statel_"+name]])

print("\n".join(a99.format_box("Molecular constants")))
print(tabulate.tabulate(rows, ["name", "value"]))


# Loads HITRAN file
f = pyfant.FileHITRANHITRAN()
f.load(os.path.join(DATADIR, INPUTFILENAME))

# Finally the conversion
converter = pyfant.ConvHITRAN160(molcomment=f"from {INPUTFILENAME}, iso={ISOWANT}",
                                 molconsts=molconsts,
                                 flag_quiet=True,
                                 isowant=ISOWANT,
                                 strengthfactor=STRENGTHFACTOR,
                                 fe=FE,
                                 mode=pyfant.ConvMode.EINSTEIN,
                                 flag_jl_from_branch=True,
                                 flag_filter_labels=True)
fmol = converter.make_file_molecules(f)
print("\n"+"\n".join(a99.format_box("Conversion log"))+"\n"+str(converter.log))

# Saves file
basename = os.path.splitext(INPUTFILENAME)[0]
outputfilename = os.path.join(DATADIR, f"{basename}.PFANT.dat")
fmol.save_as(outputfilename)

print(f"Saved file '{outputfilename}'")

