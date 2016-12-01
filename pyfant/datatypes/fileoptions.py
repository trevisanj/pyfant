import re
import sys
import imp
import astroapi as aa


__all__ = ["FileOptions"]


@aa.froze_it
class FileOptions(aa.DataFile):
    """
    `x.py` Command-line Options

    For each xxxx attribute not starting with "_" there exists
    a variable in config.f90 named config_xxxx, and
    a command-line option "--xxxx"

    """

    description = "command-line options"
    default_filename = "options.py"
    attrs = []

    def __init__(self):
        aa.DataFile.__init__(self)

        # innewmarcs, hydro2, pfant, nulbad
        self.logging_level = None
        self.logging_console = None
        self.logging_file = None
        self.fn_logging = None
        self.fn_main = None
        self.explain = None
        self.play = None

        # innewmarcs, hydro2, pfant
        self.fn_modeles = None

        # innewmarcs
        self.fn_modgrid = None
        self.fn_moo = None
        self.allow = None

        # innewmarcs, pfant
        self.opa = None
        self.fn_opa = None

        # hydro2, pfant
        self.fn_absoru2 = None
        self.fn_hmap = None
        self.llzero = None
        self.llfin = None

        # hydro2
        self.zph = None
        self.kik = None
        self.amores = None
        self.kq = None

        # pfant
        self.fn_dissoc    = None
        self.fn_partit    = None
        self.fn_abonds    = None
        self.fn_atoms   = None
        self.fn_molecules = None
        self.fn_lines     = None
        self.fn_log       = None
        self.fn_progress = None
        self.flprefix = None
        self.no_molecules = None
        self.no_h = None
        self.no_atoms = None
        self.zinf = None
        self.pas = None
        self.aint = None
        self.interp = None
        self.abs = None
        self.sca = None
        self.absoru = None

        # nulbad
        self.norm = None
        self.flam = None
        self.convol = None
        self.fwhm = None
        self.pat = None
        self.fn_flux = None
        self.fn_cv = None


    def init_default(self):
        """Overriden to reset all options to None."""
        for option_name in self.get_names():
            self.__setattr__(option_name, None)

    def get_names(self):
        """Returns a list with the names of all the options. Names come sorted"""
        d = dir(aa.DataFile())
        return [x for x in dir(self) if not x.startswith(('_', 'get_')) and
         x not in d]

    def get_args(self):
        """
        Returns a list of command-line arguments (only options that have been set)
        """
        l = []
        names = self.get_names()
        for attr_name in names:
            value = self.__getattribute__(attr_name)
            if value is not None:
                s_value = ("T" if value else "F") if isinstance(value, bool) else str(value)
                if re.search(r"[,|& ]", s_value):
                    s_value = '"'+s_value+'"'  # adds quotes if string contains one of the characters above
                l.extend(["--"+attr_name, s_value])
        return l

    def _do_load(self, filename):
        with open(filename, "r") as h:
            lines = h.read()
        cfg = imp.new_module('cfg')
        exec(lines, cfg.__dict__)

        valid_names = self.get_names()
        for option_name in valid_names:
            # resets all options, because if they are not specified in the file, they should be not set
            self.__setattr__(option_name, None)

        for option_name in dir(cfg):
            if option_name.startswith("_"):
                continue
            if not option_name in valid_names:
                raise RuntimeError("Invalid option: '%s'" % option_name)
            self.__setattr__(option_name, cfg.__dict__[option_name])

    def _do_save_as(self, filename):
        l = []
        names = self.get_names()
        for attr_name in names:
            value = self.__getattribute__(attr_name)
            if value is not None:
                l.append("%s = %s" % (attr_name, repr(value)))

        with open(filename, "w") as h:
            h.write("# Command-line options\n")
            h.write("# Note: do not edit this file directly, as any changes will be overwritten by x.py\n\n")

            h.write(("\n".join(l))+"\n")

_options = FileOptions()
FileOptions.attrs = _options.get_names()