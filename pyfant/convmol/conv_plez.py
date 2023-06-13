from .convlog import *
from .conv import *
import pyfant

__all__ = ["ConvPlez"]


class ConvPlez(Conv):
    """
    Converts Plez molecular lines data to PFANT "sets of lines"

        Args:
            flag_fcf: Whether to multiply calculated gf's by Franck-Condon Factor
                      (only makes sense when mode==ConvMode.HLF)

            name: species name within Plez's file. Examples: "NH A-X PGopher", "Sneden web" etc.

            strengthfactor: (=1.) all resulting line strengths ("sj") will be multiplied by this factor.
                Note: it is better to use "fe" argument instead

    ***Note** old format (FilePlezMoleculeOld) does not have loggf information,
              therefore the only way to work with the latter file type is
              mode==CONVPLEZMODE_HLF
    """

    def __init__(self, *args, flag_fcf=False,
                 name="", strengthfactor=1., **kwargs):
        Conv.__init__(self, *args, **kwargs)
        self.flag_fcf = flag_fcf
        self.name = name
        self.strengthfactor = strengthfactor


    def _make_sols(self, file):

        log = self.log
        sols = self.sols

        def append_error(msg):
            log.errors.append("#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), str(msg)))

        if not isinstance(file, pyfant.FilePlezLinelistBase):
            raise TypeError("Invalid type for argument 'fileobj': {}".format(type(file).__name__))

        lines = file.molecules[self.name].lines
        n = log.n = len(lines)

        if n == 0:
            raise RuntimeError("Species '{}' has zero lines".format(self.name))

        if self.mode == ConvMode.HLF:
            mtools = self.kovacs_toolbox()
        else:
            deltak = self.molconsts.get_deltak()
            S2l = self.molconsts.get_S2l()

        for i, line in enumerate(lines):
            branch = line.branch

            try:
                sj = self.strengthfactor

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

                    if self.flag_fcf:
                        sj *= self._get_fcf(line.vl, line.v2l)

                else:
                    if self.mode == ConvMode.EINSTEIN_MINIMAL:
                        J = (line.gu-1.)/2.
                        if J < 0: J = 0
                        line.Jl = line.J2l = J
                        line.vl = line.v2l = 0

                        if not branch:
                            branch = "-"

                        normalizationfactor = self.get_normalizationfactor(line.J2l, S2l, deltak, self.strengthfactor)
                        sj *= normalizationfactor*10**line.loggf

            except Exception as e:
                reason = a99.str_exc(e)
                log.skip_reasons[reason] += 1
                msg = "#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), reason)
                log.errors.append(msg)
                if not self.flag_quiet:
                    a99.get_python_logger().exception(msg)
                continue
            else:
                sols.append_line(line, sj, branch)

        return sols, log
