from .convlog import *
from .conv import *
import pyfant

__all__ = ["ConvKurucz"]


class ConvKurucz(Conv):
    """Converts Kurucz molecular lines data to PFANT "sets of lines"

        Args:
            flag_spinl: Whether or not to use the spinl of the Kurucz line list
                        for branch determination (spin2l is always used). Effect:

                - True: possible branches are P1, P12, P21, P2 and repeat for Q, R
                        (12 possibilities in total)

                - False: possible branches are P1, P2 and repeat for Q, R
                         (6 possibilities in total)

            iso: (int or None) isotope. If specified as int, only that isotope will be filtered;
                 otherwise, all isotopes in file will be included. Isotope is
                 field KuruczMolLine.iso (see KuruczMolLine, FileKuruczMol).

                 **Note** old Kurucz file format does not have the isotope information, therefore,
                          iso must be None or the thing will not work

    """

    def __init__(self, flag_spinl=False, iso=None, *args, **kwargs):
        Conv.__init__(self, *args, **kwargs)
        self.flag_spinl = flag_spinl
        self.iso = iso

    def _make_sols(self, lines):

        log = self.log
        sols = self.sols

        def append_error(msg):
            log.errors.append("#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), str(msg)))

        if not isinstance(lines, pyfant.FileKuruczMoleculeBase):
            raise TypeError("Invalid type for argument 'fileobj': {}".format(type(lines).__name__))
        if self.mode == ConvMode.F:
            if not isinstance(lines, pyfant.FileKuruczMolecule):
                raise ValueError("Old-format file does not contain oscillator strength")

            deltak = self.molconsts.get_deltak()
            S2l = self.molconsts.get_S2l()
        elif self.mode == ConvMode.HLF:
            pass
        else:
            raise ValueError(f"mode=={self.mode} not implemented")


        lines = lines.lines
        log.n = len(lines)
        if log.n == 0:
            raise RuntimeError("Zero lines found")


        STATEL = self.molconsts["from_label"]
        STATE2L = self.molconsts["to_label"]

        mtools = self.kovacs_toolbox()

        for i, line in enumerate(lines):
            if self.iso and line.iso != self.iso:
                log.skip_reasons["Isotope {}".format(line.iso)] += 1
                continue

            if line.statel != STATEL or line.state2l != STATE2L:
                log.skip_reasons["Transition {}-{}".format(line.statel, line.state2l)] += 1
                continue

            branch = mtools.quanta_to_branch(line.Jl, line.J2l,
                spinl=(None if not self.flag_spinl else line.spinl), spin2l=line.spin2l)

            # This was only a test, but filters like these may be useful if line.spin2l != line.spinl:
            #     log.skip_reasons["Different spin"] += 1
            #     continue

            try:
                if self.mode == ConvMode.HLF:
                    sj = self.get_hlf(line.vl, line.v2l, line.J2l, branch)
                else:
                    k = 1/((2*S2l+1)*(2-deltak)*(2*line.J2l+1))
                    sj = k*10**line.loggf

                self.append_line(line, sj, branch)

            except Exception as e:
                reason = a99.str_exc(e)
                log.skip_reasons[reason] += 1
                msg = "#{}{} line: {}".format(i + 1, a99.ordinal_suffix(i + 1), reason)
                log.errors.append(msg)
                if not self.flag_quiet:
                    a99.get_python_logger().exception(msg)
                continue
