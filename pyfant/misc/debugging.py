__all__ = ["GetCurrentFunctionName", "MyLock"]


import inspect
from threading import Lock, current_thread
import traceback
from .misc import *


###############################################################################
# # Debugging facilities

def GetCurrentFunctionName(k=0):
  """Returns the function name of the caller.

  Arguments:
    k=0 -- 1: caller of the caller,
       2: caller of the caller of the caller etc

  Obs: profiling shows that this function grabs a lot of execution time for itself."""
  return inspect.stack()[1+k][3]


class MyLock(object):
    """Lock with verbosing, helps to find deadlocks"""

    def __init__(self, name=None, flag_verbose=False):
        if name is None:
            name = random_name()
        self.name = name
        self.flag_verbose = flag_verbose
        self.__lock = Lock()

    def acquire(self, *args):
        if self.__lock.locked():
            self.__log("Tried to lock, but is already locked!!")
            get_python_logger().info("\n".join(traceback.format_stack()))
        else:
            pass
            # self.__log("Will acquire lock")
        self.__lock.acquire(*args)
        self.__log("Acquired lock, good")

    def release(self):
        self.__lock.release()
        self.__log("Released lock")

    # For the "with" statement
    def __exit__(self, *args):
        self.release()
    __enter__ = acquire

    def __log(self, s):
        if self.flag_verbose:
            get_python_logger().info("--- MyLock %s --- %s (caller: %s; thread: %s)" %
            (self.name, s, GetCurrentFunctionName(2), current_thread().name))

