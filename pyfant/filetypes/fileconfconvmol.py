from f311 import FilePyConfig
import a99


__all__ = ["FileConfigConvMol"]


@a99.froze_it
class FileConfigConvMol(FilePyConfig):
    """Configuration file for molecular lines conversion GUI (Python code)"""

    default_filename = "configconvmol.py"
    attrs = ["obj"]
    editors = []

    # Name of variable in module
    modulevarname = "ccm"
