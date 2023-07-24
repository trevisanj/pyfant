from .convlog import *
from .conv import *
import pyfant

__all__ = ["ConvPlez"]


class ConvPlez(Conv):
    """
    Converts Plez molecular lines data to PFANT "sets of lines"

        Args:
            species: species name within Plez's file. Examples: "NH A-X PGopher", "Sneden web" etc.

    ***Note** old format (FilePlezMoleculeOld) does not have loggf information,
              therefore the only way to work with the latter file type is
              mode==CONVPLEZMODE_HLF
    """

    def __init__(self, *args, species="", **kwargs):
        Conv.__init__(self, *args, **kwargs)
        self.species = species

    def _make_sols(self, file):

        log = self.log
        sols = self.sols

        def append_error(msg):
            log.errors.append("#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), str(msg)))

        if not isinstance(file, pyfant.FilePlezLinelistBase):
            raise TypeError("Invalid type for argument 'fileobj': {}".format(type(file).__name__))

        try:
            lines = file.molecules[self.species].lines
        except KeyError:
            raise KeyError(f"Species '{self.species}' not found in {list(file.molecules.keys())}")
        n = log.n = len(lines)

        if n == 0:
            raise RuntimeError("Species '{}' has zero lines".format(self.species))

        if self.mode == ConvMode.HLF:
            mtools = self.kovacs_toolbox()
        else:
            deltak = self.molconsts.get_deltak()
            S2l = self.molconsts.get_S2l()

        if self.flag_filter_labels:
            if self.mode == ConvMode.EINSTEIN_MINIMAL:
                raise ValueError(f"mode==ConvMode.EINSTEIN_MINIMAL and flag_filter_label==True are incompatible")

            from_label = self.molconsts["from_label"]
            to_label = self.molconsts["to_label"]

        for i, line in enumerate(lines):
            branch = line.branch
            sj = 1.

            try:
                if self.flag_filter_labels:
                    if line.from_label != from_label or line.to_label != to_label:
                        log.skip_reasons[f"Wrong system: {line.from_label}-{line.to_label}"] += 1
                        continue

                if self.mode == ConvMode.HLF:
                    try:
                        hlf = mtools.get_sj(line.vl, line.v2l, line.J2l, branch)
                    except pyfant.NoLineStrength:
                        log.skip_reasons["Cannot calculate HLF"] += 1
                        continue

                    if hlf < 0:
                        log.skip_reasons["Negative SJ"] += 1
                        continue

                    sj *= hlf

                else:
                    if self.mode == ConvMode.EINSTEIN_MINIMAL:
                        J = (line.gu-1.)/2.
                        if J < 0: J = 0
                        line.Jl = line.J2l = J
                        line.vl = line.v2l = 0

                    if not branch:
                        branch = "-"

                    normalizationfactor = self.get_normalizationfactor(line.J2l, S2l, deltak)
                    sj *= normalizationfactor*10**line.loggf

                self.append_line(line, sj, branch)

            except Exception as e:
                reason = a99.str_exc(e)
                log.skip_reasons[reason] += 1
                msg = "#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), reason)
                log.errors.append(msg)
                if not self.flag_quiet:
                    a99.get_python_logger().exception(msg)
                continue

        return sols, log
