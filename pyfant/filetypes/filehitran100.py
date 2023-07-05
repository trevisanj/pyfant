# 20230705 This is one project to try to reproduce Jorge's OH, but I don't know if it is necessary (I am now working
# with new HITRAN 160-column files, which seem to have similar (and more) information)

__all__ = ["FileHITRAN100"]

import a99
from f311 import DataFile
import tabulate

@a99.froze_it
class FileHITRAN100(DataFile):
    """
    HITRAN's 100-column format

    References:
        [1] Jorge Melendez's work on OH: hitranOH.dat, extraeOH.f
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
