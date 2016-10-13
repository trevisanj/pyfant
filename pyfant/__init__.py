def init_agg():
    # Problems with Tk:
    # - plot windows pop as modal
    # - configuration options not as rich as Qt4Agg
    import matplotlib
    matplotlib.use('Qt4Agg')

init_agg()

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
from .blocks import *
import datatypes
import misc
import plotting
# note that gui is not imported automatically
