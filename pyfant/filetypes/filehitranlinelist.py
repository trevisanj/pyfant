# Represents file parsed by HITRAN's "hapi"
#
# This class was creates mainly to fulfill existing structure in "convmol" framework, namely Conv._to_sols() expects
# a "file" class. However, load() is dummy
__all__ = ["FileHITRANLinelist"]


import a99
from f311 import DataFile
import tabulate

@a99.froze_it
class FileHITRANLinelist(DataFile):
    """
    HITRAN linelist
    """

    def __init__(self):
        DataFile.__init__(self)

        # Will later have contents as in hapi.LOCAL_TABLE_CACHE[filename_without_extension], which is a dictionary
        # with keys "header" and "data"
        self.data = None

    def __str__(self):
        return super().__str__()

    def __len__(self):
        return len(self.data["data"]["molec_id"])  # TODO test

    def _do_load(self, filename):
        pass
