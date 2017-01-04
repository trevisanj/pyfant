# # Temporary imports
#   =================
# These modules should be be del'eted at the end
import pyscellanea as pa


# # Setup
#   =====
SESSION_PREFIX_SINGULAR = 'session-'
SESSION_PREFIX_PLURAL = 'session-'
MULTISESSION_PREFIX = 'multi-session-'

# ## Colors definition
# Color for labels indicating a star parameter
COLOR_STAR = "#2A8000"
# Color for labels indicating a software configuration parameter
COLOR_CONFIG = "#BD6909"


# # Imports
#   =======
from .errors import *
from .gear import *
from .datatypes import *
from .conf import *
from .runnables import *
from .rm import *
from .vis import *
from .util import *
from .from_vald import *
from .multirunnable import *
from .gui import *
from .paths import *
from . import datatypes
from . import gear
from . import gui
from . import vis
from . import convmol

# # Function to access package-specific config file
#   ===============================================
def get_config():
    """Returns PyfantConfigObj object that corresponds to file ~/.pyfant.conf"""
    return pa.get_config_obj(".pyfant.conf")


# # # Function to be called from astroapi package
# #   ==========================================
# # **Note** To make astroapi execute this, astroapi/__init__.py has to be changed
# def _setup_astroapi():
#     """Adds entries to the astroapi module"""
#
#     pa._classes_txt.extend([FileAbsoru2, FileHmap, FileMain, FileDissoc,
#                            FileToH, FileAbonds, FileAtoms, FileMolecules])
#     pa._classes_file.extend(pa.get_classes_in_module(datatypes, pa.DataFile))
#     pa._classes_vis.extend(pa.get_classes_in_module(vis, pa.Vis))
#

# # Finally, gets rid of unwanted symbols in the workspace
#   ======================================================
del pa
