__all__ = ["str_vector", "float_vector", "int_vector", "readline_strip", "multirow_str_vector",
"get_pyfant_default_data_path", "new_filename", "_rename_to_temp_lock", "rename_to_temp",
"overwrite_fits", "write_lf", "slugify", "copy_default_file", "get_pfant_path", "get_pfant_data_path",
"get_pfant_data_subdirs", "get_pyfant_path", "get_pfant_star_subdirs", "symlink", "print_skipped",
"crunch_dir", "get_fortrans", "load_with_classes", "is_text_file",
"get_pyfant_scripts_path", "get_script_info", "format_script_info"]


import os.path
import re
import shutil
from threading import Lock
import glob
import imp
import textwrap
import platform
from astropy.io import fits
from .textinterface import *
from .loggingaux import *


# #################################################################################################
# # I/O routines


def str_vector(f):
    """
    Reads next line of file and makes it a vector of strings

    Note that each str.split() already strips each resulting string of any whitespaces.
    """
    return f.readline().split()


def float_vector(f):
    """Reads next line of file and makes it a vector of floats."""
    return [float(s) for s in str_vector(f)]


def int_vector(f):
    """Reads next line of file and makes it a vector of floats."""
    return [int(s) for s in str_vector(f)]


def readline_strip(f):
    """Reads next line of file and strips the newline."""
    return f.readline().strip('\n')


def multirow_str_vector(f, n, r=0):
    """
    Assembles a vector that spans several rows in a text file.

    Arguments:
      f -- file-like object
      n -- number of values expected
      r (optional) -- Index of last row read in file (to tell which file row in
                      case of error)

    Returns:
      (list-of-strings, number-of-rows-read-from-file)
    """

    so_far = 0
    n_rows = 0
    v = []
    while True:
        temp = str_vector(f)
        n_rows += 1
        n_now = len(temp)

        if n_now+so_far > n:
            get_python_logger().warning(('Reading multi-row vector: '
                'row %d should have %d values (has %d)') %
                (r+n_rows, n-so_far, n_now))

            v.extend(temp[:n-so_far])
            so_far = n

        elif n_now+so_far <= n:
            so_far += n_now
            v.extend(temp)

        if so_far == n:
            break

    return v, n_rows


def new_filename(prefix, extension=""):
  """returns a file name that does not exist yet, e.g. prefix.0001.extension"""

  i = 0
  while True:
    ret = '%s.%04d.%s' % (prefix, i, extension) \
      if extension else '%s.%04d' % (prefix, i)
    if not os.path.exists(ret):
      break
    i += 1
    if i > 9999:
        raise RuntimeError("Could not make a new file name for (prefix='%s', extension='%s')" %
                           (prefix, extension))
  return ret


_rename_to_temp_lock = Lock()
def rename_to_temp(filename):
    """*Thread-safe* renames file to temporary filename. Returns new name"""
    with _rename_to_temp_lock:
        root, ext = os.path.splitext(filename)
        if len(ext) > 0:
            ext = ext[1:]  # the dot (".") is originally included
        new_name = new_filename(root, ext)
        os.rename(filename, new_name)
        return new_name


def overwrite_fits(hdulist, filename):
    """
    Saves a FITS file. Combined file rename, save new, delete renamed for FITS files

    Why: HDUlist.writeto() does not overwrite existing files

    Why(2): It is also a standardized way to asve FITS files
    """

    assert isinstance(hdulist, (fits.HDUList, fits.PrimaryHDU))
    temp_name = None
    flag_delete_temp = False
    if os.path.isfile(filename):
        # PyFITS does not overwrite file
        temp_name = rename_to_temp(filename)
    try:
        hdulist.writeto(filename, output_verify='warn')
        flag_delete_temp = temp_name is not None
    except:
        # Writing failed, reverts renaming
        os.rename(temp_name, filename)
        raise

    if flag_delete_temp:
        os.unlink(temp_name)


def write_lf(h, s):
  """Adds lf to end of string and writes it to file."""
  h.write(s+"\n")


def slugify(value, flagLower=True):
  """
  Converts to lowercase, removes non-alpha characters,
  and converts spaces to hyphens.

  Useful for making file names.

  Source: http://stackoverflow.com/questions/5574042/string-slugification-in-python
  """
  value = re.sub('[^\w\s.]', '', value).strip()
  if flagLower:
    value = value.lower()
  value = re.sub('[-\s]+', '-', value)
  return value


def copy_default_file(filename):
    """Copies file from pyfant/data/default directory to local directory."""
    fullpath = get_pyfant_default_data_path(filename)
    shutil.copy(fullpath, ".")


def get_pyfant_path(*args):
  """Returns full path pyfant package. Arguments are added at the end of os.path.join()"""
  p = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", *args))
  return p


def get_pyfant_default_data_path(fn):
  """Returns full path to default data file."""
  p = os.path.join(get_pyfant_path(), "datatypes", "default", fn)
  return p


def get_pyfant_scripts_path(*args):
    """Returns path to pyfant scripts. Arguments are added to the end os os.path.join()"""
    return get_pyfant_path("..", "scripts", *args)


def get_pfant_path(*args):
    """
    Returns absolute path to the "PFANT" directory.

    PFANT binaries must be in PATH,
    otherwise it will not work

    Arguments passed will be incorporated into path
    """
    p = os.getenv("PATH")
    pos1 = p.rfind("PFANT")
    pos0 = p.rfind(os.pathsep, 0, pos1)

    # works even if pos0 == -1
    path_prefix = p[pos0 + 1:pos1+5]

    return os.path.abspath(os.path.join(path_prefix, *args))


def get_pfant_data_path():
    """Returns absolute path to PFANT/data"""
    return get_pfant_path("data")


def get_pfant_data_subdirs():
    """returns a list containing all subdirectories of PFANT/data (their names only, not full path)."""
    dd = glob.glob(os.path.join(get_pfant_data_path(), "*"))
    ret = []
    for d in dd:
        if os.path.isdir(d):
            ret.append(os.path.basename(d))
    return ret


def get_pfant_star_subdirs():
    """Returns only subdirectories of PFANT/data that contain file main.dat."""
    dd = glob.glob(os.path.join(get_pfant_data_path(), "*"))
    ret = []
    for d in dd:
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, 'main.dat')):
            ret.append(os.path.basename(d))
    return ret


def symlink(source, link_name):
    """
    Creates symbolic link for either operating system.

    http://stackoverflow.com/questions/6260149/os-symlink-support-in-windows
    """
    os_symlink = getattr(os, "symlink", None)
    if callable(os_symlink):
        os_symlink(source, link_name)
    else:
        import ctypes
        csl = ctypes.windll.kernel32.CreateSymbolicLinkW
        csl.argtypes = (ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_uint32)
        csl.restype = ctypes.c_ubyte
        flags = 1 if os.path.isdir(source) else 0
        if csl(link_name, source, flags) == 0:
            raise ctypes.WinError()


def print_skipped(reason):
    """Standardized printing for when a file was skipped."""
    print "   ... SKIPPED (%s)." % reason


def crunch_dir(name, n=50):
    """Puts "..." in the middle of a directory name if lengh > n."""
    if len(name) > n + 3:
        name = "..." + name[-n:]
    return name


class ScriptInfo(object):
    def __init__(self, filename, description, flag_error, flag_gui):
        self.filename = filename
        self.description = description
        self.flag_error = flag_error
        self.flag_gui = flag_gui


def get_script_info(dir_):
    """
    Returns a list of ScriptInfo objects

    The ScriptInfo objects represent the ".py" files in directory dir_,
    except those starting with a "_"
    """

    ret = []
    # gets all scripts in script directory
    ff = glob.glob(os.path.join(dir_, "*.py"))
    # discards scripts whose file name starts with a "_"
    ff = [f for f in ff if not os.path.basename(f).startswith("_")]
    ff.sort()

    for f in ff:
        _, filename = os.path.split(f)
        flag_error = False
        flag_gui = None
        try:
            # Checks if it is a graphical application

            with open(f, "r") as h:
                flag_gui = "QApplication" in h.read()

            script_ = imp.load_source('script_', f)  # module object
            descr = script_.__doc__.strip()
            descr = descr.split("\n")[0]  # first line of docstring
        except Exception as e:
            flag_error = True
            descr = "*%s*: %s" % (e.__class__.__name__, str(e))

        ret.append(ScriptInfo(filename, descr, flag_error, flag_gui))

    return ret


def _format_script_info(py_len, title, scriptinfo, format):
    ret = []
    if format == "markdown-list":
        ret.append("\n%s:" % title)
        for si in scriptinfo:
            ret.append("  - `%s` -- %s" % (si.filename, si.description))
    elif format == "markdown-table":
        ret.append("\n%s:\n" % title)
        mask = "%%-%ds | %%s" % (py_len+2, )
        ret.append(mask % ("Script name", "Purpose"))
        ret.append("-" * (py_len + 3) + "|" + "-" * 10)
        for si in scriptinfo:
            ret.append(mask % ("`%s`" % si.filename, si.description))
    elif format == "text":
        hr = "*"*(len(title)+2)
        ret.append("\n%s\n*%s*\n%s" % (hr, title, hr))
        for si in scriptinfo:
            piece = si.filename + " " + ("." * (py_len - len(si.filename)))
            if si.flag_error:
                ret.append(piece+si.description)
            else:
                # ret.append(piece)
                ss = textwrap.wrap(si.description, 79 - py_len - 1)
                ret.append(piece+" "+(ss[0] if ss and len(ss) > 0 else "no doc"))
                for i in range(1, len(ss)):
                    ret.append((" " * (py_len + 2))+ss[i])
    return ret


def format_script_info(scriptinfo, format="text"):
    """
    Generates listing of all Python scripts available as command-line programs.

    Arguments:
      infolist -- list of ScriptInfo objects

      format -- One of the options below:
        "text" -- generates plain text for printing at the console
        "markdown-list" -- generates MarkDown as a list
        "markdown-table" -- generates MarkDown as a table

    Returns: (list of strings, maximum filename size)
      list of strings -- can be joined with a "\n"
      maximum filename size
    """

    py_len = max([len(si.filename) for si in scriptinfo])

    sisi_gra = [si for si in scriptinfo if si.flag_gui]
    sisi_cmd = [si for si in scriptinfo if not si.flag_gui]
    sisi_gra.sort(cmp=lambda x, y: x.filename < y.filename)
    sisi_cmd.sort(cmp=lambda x, y: x.filename < y.filename)

    ret = []
    if len(sisi_gra) > 0:
        ret.extend(_format_script_info(py_len, "Graphical applications", sisi_gra, format))
    if len(sisi_cmd) > 0:
        ret.extend(_format_script_info(py_len, "Command-line tools", sisi_cmd, format))

    return ret, py_len


def get_fortrans(max_len=None):
    """
    Generates listing of files in the Fortran bin directory

    Arguments
      max_len -- (optional) if passed, will use it, otherwise will be the
                 maximum number of characters among all Fortran executable names.

    Returns: list of filenames
    """

    ret = []
    bindir = os.path.join(get_pfant_path(), "fortran", "bin")
    ihpn = ["innewmarcs", "hydro2", "pfant", "nulbad"]
    if max_len is None:
        max_len = max(len(x) for x in ihpn)

    if platform.system() == "Windows":
        def has_it(x):
            return os.path.isfile(os.path.join(bindir, x+".exe"))
    else:
        def has_it(x):
            return os.path.isfile(os.path.join(bindir, x))
    for name in ihpn:
        status = "not found"
        if has_it(name):
            status = "found"
        piece = name + " " + ("." * (max_len-len(name)))
        ret.append(("%-"+str(max_len)+"s %s") % (piece, status))
    return ret


def load_with_classes(filename, classes):
    """Attempts to load file by trial-and-error using a given list of classes.

    Arguments:
      filename -- full path to file
      classes -- list of DataFile descendant classes

    Returns: DataFile object if loaded successfully, or None if not.

    Note: it will stop at the first successful load.

    Attention: this is not good if there is a bug in any of the file readers,
    because *all exceptions will be silenced!*
    """

    ok = False
    for class_ in classes:
        obj = class_()
        try:
            obj.load(filename)
            ok = True
        # cannot let IOError through because pyfits raises IOError!!
        # except IOError:
        #     raise
        except OSError:
            raise
        except Exception as e:  # (ValueError, NotImplementedError):
            # Note: for debugging, switch the below to True
            if False:
                get_python_logger().exception("Error trying with class \"%s\"" % \
                                              class_.__name__)
            pass
        if ok:
            break
    if ok:
        return obj
    return None


###############################################################################
#http://eli.thegreenplace.net/2011/10/19/perls-guess-if-file-is-text-or-binary-implemented-in-python
import sys
_PY3 = sys.version_info[0] == 3

# A function that takes an integer in the 8-bit range and returns
# a single-character byte object in py3 / a single-character string
# in py2.
#
_int2byte = (lambda x: bytes((x,))) if _PY3 else chr

_text_characters = (
        b''.join(_int2byte(i) for i in range(32, 127)) +
        b'\n\r\t\f\b')

def is_text_file(filepath, blocksize=2**13):
    """ Uses heuristics to guess whether the given file is text or binary,
        by reading a single block of bytes from the file.
        If more than 30% of the chars in the block are non-text, or there
        are NUL ('\x00') bytes in the block, assume this is a binary file.
    """
    with open(filepath, "rb") as fileobj:
        block = fileobj.read(blocksize)
        if b'\x00' in block:
            # Files with null bytes are binary
            return False
        elif not block:
            # An empty file is considered a valid text file
            return True

        # Use translate's 'deletechars' argument to efficiently remove all
        # occurrences of _text_characters from the block
        nontext = block.translate(None, _text_characters)
        return float(len(nontext)) / len(block) <= 0.30
