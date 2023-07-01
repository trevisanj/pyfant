__all__ = ["FileMollist"]

"""Represents file such as mollist.dat (2023)"""

import a99
from f311 import DataFile
import tabulate


@a99.froze_it
class FileMollist(DataFile):
    """
    List of PFANT molecular lines files
    """

    default_filename = "mollist.dat"
    attrs = ["filenames"]

    def __init__(self):
        DataFile.__init__(self)

        # List of HmapRow objects
        self.filenames = []

    def __len__(self):
        return len(self.filenames)

    def _do_load(self, filename):
        """Loads from file."""

        with open(filename, "r") as h:
            for line in h:
                line = line.strip()
                if not line.startswith("#"):
                    self.filenames.append(line)

    def _do_save_as(self, filename):
        with open(filename, "w") as h:
            for r in self.filenames:
                a99.write_lf(h, r)
