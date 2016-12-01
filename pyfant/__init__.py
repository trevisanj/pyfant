

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
from .misc import *
from .datatypes import *
from .conf import *
from .runnables import *
from .rm import *
from .util import *
from .from_vald import *
from .multirunnable import *
from .gui import *
from . import datatypes
from . import misc
from . import gui
from . import vis


# # Temporary imports
#   =================
# These modules should be be del'eted at the end
import sys
import astroapi as aa


# # Prevents from running in Python 2
#   =================================
# (http://stackoverflow.com/questions/9079036)
if sys.version_info[0] < 3:
    raise RuntimeError("Python version detected:\n*****\n%s\n*****\nCannot run, must be using Python 3" % sys.version)


# # Function to access package-specific config file
#   ===============================================
def get_config():
    """Returns PyfantConfigObj object that corresponds to file ~/.pyfant.conf"""
    return aa.get_config_obj(".pyfant.conf")


# # Function to be called from astroapi package
#   ==========================================
# **Note** To make astroapi execute this, astroapi/__init__.py has to be changed
def _setup_astroapi():
    """Adds entries to the astroapi module"""

    import astroapi as aa

    aa._classes_txt.extend([FileAbsoru2, FileHmap, FileMain, FileDissoc,
                           FileToH, FileAbonds, FileAtoms, FileMolecules])
    aa._classes_file.extend(aa.get_classes_in_module(datatypes, aa.DataFile))
    aa._classes_vis.extend(aa.get_classes_in_module(vis, aa.Vis))


# # Finally, gets rid of unwanted symbols in the workspace
#   ======================================================
del sys, aa

