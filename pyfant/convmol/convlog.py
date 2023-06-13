from collections import Counter
import a99, tabulate

@a99.froze_it
class MolConversionLog(object):

    @property
    def num_lines_skipped(self):
        """Sums all counts in self.skip_reasons"""
        return sum(self.skip_reasons.values())

    @property
    def n(self):
        return self.num_lines

    @n.setter
    def n(self, x):
        self.num_lines = x

    def __init__(self, num_lines=0, flag_ok=True):
        # Number of lines in input file
        self.num_lines = num_lines
        # Whether the conversion was considered successful (despite errors)
        self.flag_ok = flag_ok
        # List of error strings
        self.errors = []
        # Counter: {"reason": number_of_times, ...}
        # The key should be a descriptive reason, however shortish
        # Access like this:
        #     >>> log.skip_reasons["FCF not found for (vl,v2l)"] += 1
        #
        self.skip_reasons = Counter()

        self.cnt_in = 0

    def __str__(self):
        INDENT = "    "
        n = self.num_lines
        _ret = [f"num_lines: {n}", f"flag_ok: {self.flag_ok}", f"included: {self.cnt_in}/{n}", f"excluded: {n-self.cnt_in}/{n}"]

        if self.skip_reasons:
            _ret.append("\n*** Skip reasons ***")
            _ret.append("\n".join([INDENT+line for line in tabulate.tabulate([(k, v) for k, v in self.skip_reasons.items()], ["Reason", "number of occurences"]).split("\n")]))
        if self.errors:
            _ret.append("\n*** Errors ***")
            _ret.append("\n".join([INDENT+line for line in self.errors]))
        return "\n".join(_ret)
