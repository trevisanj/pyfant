from f311 import FilePy
import a99
from ..molconsts import MolConsts
from . import FileMolDB

__all__ = ["FileMolConsts"]

@a99.froze_it
class FileMolConsts(FilePy):
    """Molecular constants config file (Python code)"""

    default_filename = "configmolconsts.py"
    attrs = ["fn_moldb", "molconsts"]
    editors = ["mced.py"]

    def __init__(self):
        FilePy.__init__(self)
        self.fn_moldb = FileMolDB.default_filename
        self.molconsts = MolConsts()

    def _do_load(self, filename):
        module = a99.import_module(filename)
        try:
            self.fn_moldb = module.fn_moldb
        except AttributeError:
            pass
        self._copy_attr(module, "molconsts", MolConsts)

    def _do_save_as(self, filename):
        with open(filename, "w") as h:
            h.write("{}\n"
                    "from pyfant import MolConsts\n"
                    "\n"
                    "fn_moldb = '{}'\n"
                    "\n"
                    "molconsts = {}\n".format(self._get_header(), self.fn_moldb, self.molconsts))

    def init_default(self):
        pass