__all__ = ["ScriptInfo", "get_script_info", "format_script_info", "collect_doc", ]


import os
import glob
import imp
import textwrap


# # Introspection-like routines

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
        n = len(title)
        # hr = "*"*(len(title)+2)
        # ret.append("\n%s\n*%s*\n%s" % (hr, title, hr))
        ret.append("\n %s \n%s" % (title, "+"+'-'*n+"+"))
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
    sisi_gra = sorted(sisi_gra, key=lambda x: x.filename)
    sisi_cmd = sorted(sisi_cmd, key=lambda x: x.filename)

    ret = []
    if len(sisi_gra) > 0:
        ret.extend(_format_script_info(py_len, "Graphical applications", sisi_gra, format))
    if len(sisi_cmd) > 0:
        ret.extend(_format_script_info(py_len, "Command-line tools", sisi_cmd, format))

    return ret, py_len


def collect_doc(module, base_class=None, prefix="", flag_exclude_prefix=False):
    """
    Collects class names and docstrings in module for classes starting with prefix

    Arguments:
        module -- Python module
        prefix -- argument for str.startswith(); if not passed, does not filter
        base_class -- filters only descendants of this class
        flag_exclude_prefix -- whether or not to exclude prefix from class name in result

    Returns: [(classname0, docstring0), ...]
    """

    ret = []
    for attrname in module.__all__:
        if prefix and not attrname.startswith(prefix):
            continue

        attr = module.__getattribute__(attrname)

        if base_class is not None and not issubclass(attr, base_class):
            continue

        ret.append((attrname if not flag_exclude_prefix else attrname[len(prefix):], attr.__doc__))

    return ret

