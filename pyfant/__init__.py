def init_agg():
    # Problems with Tk:
    # - plot windows pop as modal
    # - configuration options not as rich as Qt5Agg
    import matplotlib
    matplotlib.use('Qt5Agg')

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
from .blocks import *
from . import datatypes
from . import misc
from . import plotting
from . import blocks
# note that gui is not imported automatically
