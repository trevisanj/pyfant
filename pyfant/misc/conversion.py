"""Conversion routines"""


__all__ = ["adjust_atomic_symbol", "str2bool", "bool2str", "chunk_string",
"ordinal_suffix", "seconds2str", "make_fits_keys_dict", "eval_fieldnames",
"valid_fits_key", "module_to_dict", "expr_to_fieldname"]


import numpy as np
import re


def adjust_atomic_symbol(x):
    """Makes sure atomic symbol is right-aligned and upper case (PFANT convention)."""
    assert isinstance(x, str)
    return "%2s" % (x.strip().upper())


def str2bool(s):
    """Understands "T"/"F" only (case-sensitive). To be used for file parsing."""
    if s == "T":
        return True
    elif s == "F":
        return False
    raise ValueError("I don't understand '%s' as a logical value" % s)


def bool2str(x):
    """Converts bool variable to either "T" or "F"."""
    assert isinstance(x, bool)
    return "T" if x else "F"


def chunk_string(string, length):
    """
    Splits a string into fixed-length chunks.

    This function returns a generator, using a generator comprehension. The
    generator returns the string sliced, from 0 + a multiple of the length
    of the chunks, to the length of the chunks + a multiple of the length
    of the chunks.

    Reference: http://stackoverflow.com/questions/18854620
    """
    return (string[0 + i:length + i] for i in range(0, len(string), length))


def ordinal_suffix(i):
    """Returns 'st', 'nd', or 'rd'."""
    return 'st' if i == 1 else 'nd' if i == 2 else 'rd' if i == 3 else 'th'


def seconds2str(seconds):
    """Returns string such as 1h 05m 55s."""

    if seconds < 0:
        return "%.3gs" % seconds
    elif np.isnan(seconds):
        return "NaN"
    elif np.isinf(seconds):
        return "Inf"

    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h >= 1:
        return "%dh %02dm %.3gs" % (h, m, s)
    elif m >= 1:
        return "%02dm %.3gs" % (m, s)
    else:
        return "%.3gs" % s


def make_fits_keys_dict(keys):
    """
    Returns a dictionary to translate to unique FITS header keys up to 8 characters long

    This is similar to Windows making up 8-character names for filenames that
    are longer than this

    "The keyword names may be up to 8 characters long and can only contain
    uppercase letters A to Z, the digits 0 to 9, the hyphen, and the underscore
    character." [1]

    Arguments:
        keys -- list of strings

    Returns:
        dictionary whose keys are the elements in the "keys" argument, and whose
        values are made-up uppercase names

    References:
        [1] http://fits.gsfc.nasa.gov/fits_primer.html
    """

    key_dict = {}
    new_keys = []
    for key in keys:
        # converts to valid FITS key according to reference [1] above
        fits_key = valid_fits_key(key)
        num_digits = 1
        i = -1
        i_max = 9
        while fits_key in new_keys:
            i += 1
            if i > i_max:
                i = 0
                i_max = i_max * 10 + 9
                num_digits += 1
            fits_key = fits_key[:(8 - num_digits)] + (("%%0%dd" % num_digits) % i)

        key_dict[key] = fits_key
        new_keys.append(fits_key)

    return key_dict


def valid_fits_key(key):
    """
    Makes valid key for a FITS header

    "The keyword names may be up to 8 characters long and can only contain
    uppercase letters A to Z, the digits 0 to 9, the hyphen, and the underscore
    character." (http://fits.gsfc.nasa.gov/fits_primer.html)
    """

    ret = re.sub("[^A-Z0-9\-_]", "", key.upper())[:8]
    if len(ret) == 0:
        raise RuntimeError("key '%s' has no valid characters to be a key in a FITS header" % key)
    return ret


def eval_fieldnames(string_, varname="fieldnames"):
    """Evaluates string_, must evaluate to list of strings. Also converts field names to uppercase"""
    ff = eval(string_)
    if not isinstance(ff, list):
        raise RuntimeError("%s must be a list" % varname)
    if not all([isinstance(x, str) for x in ff]):
        raise RuntimeError("%s must be a list of strings" % varname)
    ff = [x.upper() for x in ff]
    return ff


def expr_to_fieldname(expr):
    """Keeps the rightmost part of the class name after the "_" """
    return expr[:expr.index("(")].strip().split("_")[-1]



def module_to_dict(module):
    """Creates a dictionary whose keys are module.__all__"""

    lot = [(key, module.__getattribute__(key)) for key in module.__all__]
    ret = dict(lot)
    return ret

