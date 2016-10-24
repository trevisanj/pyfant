
# (http://stackoverflow.com/questions/9079036)
import sys
if sys.version_info[0] < 3:
    raise RuntimeError("Python version detected:\n*****\n%s\n*****\nCannot run, must be using Python 3" % sys.version)

def init_agg():
    # Problems with Tk:
    # - plot windows pop as modal
    # - configuration options not as rich as Qt4Agg
    import matplotlib
    matplotlib.use('Qt4Agg')

init_agg()

from .constants import *
from .errors import *
from .misc import *
from .datatypes import *
from .conf import *
from .runnables import *
from .rm import *
from .plotting import *
from .util import *
from .from_vald import *
from .multirunnable import *
from . import datatypes
from . import misc
from . import plotting
from . import blocks
# note that gui is not imported automatically
# note that blocks is not imported automatically
