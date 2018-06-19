from .convlog import *
from .conv import *
import pyfant

__all__ = ["ConvPlez"]


class ConvPlez(Conv):
    """Converts Plez molecular lines data to PFANT "sets of lines"

        Args:
            flag_hlf: Whether to calculate the gf's using Honl-London factors or
                      use Plez's loggf instead

                      ***Note** old format (FilePlezMoleculeOld) does not have loggf information,
                                therefore the only way to work with the latter file type is
                                flag_hlf==True

            flag_normhlf: Whether to multiply calculated gf's by normalization factor

            flag_fcf: Whether to multiply calculated gf's by Franck-Condon Factor

            flag_quiet: Will not log exceptions when a molecular line fails

            name: name of molecule+system, e.g., "NH A-X PGopher"
    """

    def __init__(self, flag_hlf=False, flag_fcf=False, flag_quiet=False, flag_special_fcf=False,
                 fcfs=None, name="", *args, **kwargs):
        Conv.__init__(self, *args, **kwargs)
        self.flag_hlf = flag_hlf
        self.flag_fcf = flag_fcf
        self.flag_quiet = flag_quiet
        self.flag_special_fcf = flag_special_fcf
        self.fcfs = fcfs
        self.name = name

    def _make_sols(self, file):

        def append_error(msg):
            log.errors.append("#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), str(msg)))

        if not isinstance(file, pyfant.FilePlezLinelist):
            raise TypeError("Invalid type for argument 'fileobj': {}".format(type(file).__name__))

        lines = file.molecules[self.name].lines
        n = len(lines)

        if n == 0:
            raise RuntimeError("Species '{}' has zero lines".format(self.name))

        STATEL = self.molconsts["from_label"]
        STATE2L = self.molconsts["to_label"]

        mtools = self.kovacs_toolbox()

        # Prepares result
        sols = ConvSols(self.qgbd_calculator, self.molconsts)
        log = MolConversionLog(n)

        for i, line in enumerate(lines):
            branch = line.branch

            try:
                sj = 1.

                if self.flag_hlf:
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
                    sj *= 10**line.loggf

                if self.flag_fcf:
                    sj *= self._get_fcf(line.vl, line.v2l, self.flag_special_fcf)

            except Exception as e:
                reason = a99.str_exc(e)
                log.skip_reasons[reason] += 1
                msg = "#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), reason)
                log.errors.append(msg)
                if not self.flag_quiet:
                    a99.get_python_logger().exception(msg)
                continue

            sols.append_line(line, sj, branch)

        return sols, log
