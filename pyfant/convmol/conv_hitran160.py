"""Molecular lines converter from HITRAN to PFANT format."""

__all__ = ["ConvHITRAN160"]

import a99, airvacuumvald as avv, sys
from . import Conv

class ConvHITRAN160(Conv):
    """Converts HITRAN molecular lines data to PFANT "sets of lines" using Einstein's coefficients

    Args:
        isowant: (=1) isotopologue ID according to HITRAN or literature e.g. [1]. Li et al. 2015 didn't follow
                 HITRAN's isotopologues codes for CO

        flag_jl_from_branch: whether to determine Jl from (branch, J2l) using rule:
            branch is P: Jl = J2l-1
            branch is Q: Jl = J2l
            branch is R: Jl = J2l+1

    There is a working example conv_hitran_co.py in examples directory

    References:
        [1] Li, G., Gordon, I.E., Rothman, L.S., Tan, Y., Hu, S.M., Kassi, S., Campargue, A. and Medvedev, E.S., 2015.
        Rovibrational line lists for nine isotopologues of the CO molecule in the X1Σ+ ground electronic state.
        The Astrophysical Journal Supplement Series, 216(1), p.15.

        [2] Plez's conversor translate_molec_linelists_v16.1.f

        [3] Jorge Melendez's work on OH: extraehitran.f
    """

    def __init__(self, *args, isowant=1, flag_jl_from_branch=False, **kwargs):
        super().__init__(*args, **kwargs)
        if not (1 <= isowant <= 9):
            raise ValueError(f"Invalid 'isowant': {isowant} (must be between 1 and 9)")
        self.isowant = isowant
        self.flag_jl_from_branch = flag_jl_from_branch

    def _make_sols(self, f):
        import pyfant
        assert isinstance(f, pyfant.FileHITRAN160)

        HITRAN = 1
        LI2015 = 2
        if isinstance(f, pyfant.FileHITRANHITRAN):
            flavor = HITRAN
        elif isinstance(f, pyfant.FileHITRANLi2015):
            flavor = LI2015
        else:
            raise RuntimeError(f"Cannot handle class {f.__class__.__name__}")

        log = self.log
        sols = self.sols

        n = log.n = len(f)
        if n == 0:
            raise RuntimeError("Zero lines found")

        deltak = self.molconsts.get_deltak()
        S2l = self.molconsts.get_S2l()

        if self.flag_filter_labels and flavor == LI2015:
            raise RuntimeError(f"Cannot filter labels (flag_filter_labels==True), as labels (e.g. \"A\", \"X\") "
                               f"are not provided by FileLi2015")

        if not self.flag_jl_from_branch and flavor == HITRAN:
            raise RuntimeError(f"Cannot determine Jl another way for FileHITRANHITRAN: flag_jl_from_branch must be activated")

        if self.flag_filter_labels:
            ref_from_label = self.molconsts["from_label"]
            ref_to_label = self.molconsts["to_label"]

        for i, line in enumerate(f.lines):
            try:
                if line.iso != self.isowant:
                    log.skip_reasons[f"isotopologue {line.iso}"] += 1
                    continue

                if self.flag_filter_labels:
                    if line.from_label != ref_from_label or line.to_label != ref_to_label:
                        log.skip_reasons[f"Wrong system: {line.from_label}-{line.to_label}"] += 1
                        continue

                if flavor == HITRAN:
                    J2l = line.J2l

                    # The following code was based on Jorge Melendez's extraehitran.f
                    # HITRAN does not have Jl
                    # branch examples: two letters, e.g. "PP", "QP", "SR", "PP", "OP"
                    if line.branch == "PP":
                        Jl = J2l-1
                    elif line.branch == "QQ":
                        Jl = J2l
                    elif line.branch == "RR":
                        Jl = J2l+1
                    else:
                        log.skip_reasons[f"Unhandled branch: {line.branch}"] += 1
                        continue
                    
                elif flavor == LI2015:
                    # This conversion of gp, gpp into Jl, J2l was taken from Plez's conversor [2]
                    # and seems to be correct for the Li 2015 CO file (I checked (vl=3, v2l=0) against the CO from 1998
                    # and J2l matches)
                    J2l = (line.gpp-1.)/2.

                    if not self.flag_jl_from_branch:
                        Jl = (line.gp-1.)/2.
                    else:
                        if line.branch == "P":
                            Jl = J2l-1
                        elif line.branch == "Q":
                            Jl = J2l
                        elif line.branch == "R":
                            Jl = J2l+1
                        else:
                            log.skip_reasons[f"Unhandled branch: {line.branch}"] += 1
                            continue

                else:
                    raise NotImplementedError()

                lambda_ = avv.vacuum_to_air(1e8/line.nu)

                SJ = self.get_sj_einstein(line.A, Jl, J2l, S2l, deltak, line.nu)

                self.append_line2(line.vl, line.v2l, lambda_, SJ, J2l, line.branch)

            except Exception as e:
                reason = a99.str_exc(e)
                log.skip_reasons[reason] += 1
                msg = "#{}{} line: {}".format(i+1, a99.ordinal_suffix(i+1), reason)
                log.errors.append(msg)
                if not self.flag_quiet:
                    a99.get_python_logger().exception(msg)


        return sols, log
