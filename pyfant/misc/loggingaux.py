"""Logging routines"""


__all__ = [
"flag_log_console", "flag_log_file", "logging_level", "get_python_logger", "add_file_handler",
"LogTwo", "SmartFormatter"]


import logging
import sys
from argparse import *
from .parts import *


# # Setup
#   =====
# If the following need change, this should be done before calling get_python_logger() for the
# first time

# Set this to make the python logger to log to the console. Note: will have no
# effect if changed after the first call to get_python_logger()
flag_log_console = True

# Set this to make the python logger to log to a file named "python.log".
# Note: will have no effect if changed after the first call to get_python_logger()
flag_log_file = True

# Logging level for the python logger
logging_level = logging.INFO


_python_logger = None
_fmtr = logging.Formatter('[%(levelname)-8s] %(message)s')
def get_python_logger():
    """Returns logger to receive Python messages (as opposed to Fortran)."""
    global _python_logger
    if _python_logger is None:
        fn = "python.log"
        l = logging.Logger("python", level=logging_level)
        if flag_log_file:
            add_file_handler(l, fn)
        if flag_log_console:
            ch = logging.StreamHandler()
            ch.setFormatter(_fmtr)
            l.addHandler(ch)
        _python_logger = l

    return _python_logger


def add_file_handler(logger, logFilename=None):
    """Adds file handler to logger.

    File is opened in "a" mode (append)
    """
    assert isinstance(logger, logging.Logger)
    ch = logging.FileHandler(logFilename, "a")
    # ch.setFormatter(logging._defaultFormatter) # todo may change to have same formatter as last handler of logger
    ch.setFormatter(_fmtr)
    logger.addHandler(ch)


@froze_it
class LogTwo(object):
  """Logs messages to both stdout and file."""
  def __init__(self, filename):
    self.terminal = sys.stdout
    self.log = open(filename, "w")

  def write(self, message):
    self.terminal.write(message)
    self.log.write(message)

  def close(self):
      self.log.close()


class SmartFormatter(RawDescriptionHelpFormatter):
    """
    Help formatter that will show default option values and also respect
    newlines in description. Neither are done in default help formatter.
    """

    def _get_help_string(self, action):
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not SUPPRESS:
                defaulting_nargs = [OPTIONAL, ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help += ' (default: %(default)s)'
        return help


        # # this is the RawTextHelpFormatter._split_lines
        # if text.startswith('R|'):
        #     return text[2:].splitlines()
        # return argparse.ArgumentDefaultsHelpFormatter._split_lines(self, text, width)


