"""Python interface to the PFANT spectral synthesis software (Fortran)"""

# # Temporary imports
#   =================
# These modules should be be del'eted at the end
import a99


# # Setup
#   =====
SESSION_PREFIX_SINGULAR = 'session-'
SESSION_PREFIX_PLURAL = 'session-'
MULTISESSION_PREFIX = 'multi-session-'

def get_custom_multisession_dirname(session_id):
    """This defines how custom directory name is made up"""
    # return pyfant.MULTISESSION_PREFIX+session_id
    return session_id


# # Imports
#   =======
from .basic import *
from .filetypes import *
from .downloaders import *
from .run import *
from .util import *
from .convmol import *
from .from_vald import *
from .molconsts import *
from .kovacs import *
from .gui import *
from . import gui
from .vis import *


# # Function to access package-specific config file
#   ===============================================
def get_config():
    """Returns PyfantConfigObj object that corresponds to file ~/.ftpyfant.conf"""
    return a99.get_config_obj(".pyfant.conf")


# # Finally, gets rid of unwanted symbols in the workspace
#   ======================================================
del a99
