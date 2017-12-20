"""Currently all moved to f311.filetypes.basic.misc"""

"""
Miscellanea of basic routines used to implement the file classes
"""

import re
import os
import shutil
import sys
import a99
import unicodedata


__all__ = ["SS_PLAIN", "SS_SUPERSCRIPT", "SS_ALL_SPECIAL", "SS_RAW",
           "greek_to_spdf", "spdf_to_greek", "state_to_str", "molconsts_to_system_str",
           "adjust_atomic_symbol", "str_to_elem_ioni", "parse_system_str",
           "split_molecules_description", "description_to_symbols", "symbols_to_formula",
           "iz_to_branch", "branch_to_iz", "iz_to_branch_alt", "branch_to_iz_alt",
           "branch_to_iz_alt2",
           ]

# **        ****                ******        ****                ******        ****
#   **    **    ******    ******      **    **    ******    ******      **    **    ******    ******
#     ****            ****              ****            ****              ****            ****
#
# Multiplicity- and spdf-related conversion and formatting routines

# # System styles
# Example: "A 2 SIGMA - X 2 PI"
SS_PLAIN = -1
# multiplicity as superscript, spdf as Greek letter name
SS_SUPERSCRIPT = 2
# multiplicity as superscript, spdf as Greek letter
SS_ALL_SPECIAL = 0
# Does not convert SPDF to string. Example: "A 2 0 - X 2 1"
SS_RAW = 1

__A = ["Sigma", "Pi", "Delta", "Phi"]

_SPDF_TO_GREEK = dict(zip(range(len(__A)), __A))
_GREEK_TO_SPDF = dict(zip(__A, range(len(__A))))

def greek_to_spdf(greek):
    """Converts Greek letter name (e.g., "sigma", "Sigma" (case **sensitive**)) to int value in [0, 1, 2, 3]"""
    try:
        ret = _GREEK_TO_SPDF[greek]
    except KeyError:
        raise ValueError("Invalid SPDF: '{}' (value must be in {})".format(greek, list(_SPDF_TO_GREEK.values())))
    return ret

def spdf_to_greek(number):
    """Converts int value in [0, 1, 2, 3] to the name of a Greek letter (all uppercase)"""
    try:
        return _SPDF_TO_GREEK[number]
    except KeyError:
        # "?" is the "zero-element"
        return "?"


def state_to_str(label, mult, spdf, style=SS_ALL_SPECIAL):
    """Compiles electronic state information into string

    Args:
        label: e.g., "A"
        mult: e.g., 2 (meaning doublet)
        spdf: e.g., 0 (meaning Sigma)

        style: rendering style: one of SS_*

    Returns:
        str
    """

    if style == SS_PLAIN:
        fmult = lambda x: x
        fspdf = lambda x:spdf_to_greek(x)
    elif style == SS_ALL_SPECIAL:
        fmult = lambda x: a99.int_to_superscript(x)
        fspdf = lambda x: a99.greek_to_unicode(spdf_to_greek(x).capitalize())
    elif style == SS_RAW:
        fmult = lambda x: x
        fspdf = lambda x: x
    elif style == SS_SUPERSCRIPT:
        fmult = lambda x: a99.int_to_superscript(x)
        fspdf = lambda x:spdf_to_greek(x)
    else:
        raise ValueError("Invalid style: {}".format(style))

    return "{} {} {}".format(label, fmult(int(mult)), fspdf(spdf))


def molconsts_to_system_str(molconsts, style=SS_ALL_SPECIAL):
    """Compiles electronic system information into string

    Args:
        molconsts: dict-like containing keys 'from_label', 'from_mult', 'from_spdf', 'to_label',
                    'to_mult', 'to_spdf'

        style: rendering style: one of SS_*

    Returns:
        str
    """
    return "{} - {}".format(
        state_to_str(molconsts["from_label"], molconsts["from_mult"], molconsts["from_spdf"], style),
        state_to_str(molconsts["to_label"], molconsts["to_mult"], molconsts["to_spdf"], style),
    )

# **        ****                ******        ****                ******        ****
#   **    **    ******    ******      **    **    ******    ******      **    **    ******    ******
#     ****            ****              ****            ****              ****            ****
#
# Conversion and formatting routines: Atomic symbols and formulas


def adjust_atomic_symbol(x):
    """Makes sure atomic symbol is right-aligned and upper case (PFANT convention)."""
    assert isinstance(x, str)
    return "%2s" % (x.strip().upper())


def str_to_elem_ioni(search):
    """str_to_elem_ioni("C1") --> (adjust_atomic_symbol("C"), 1)"""
    r = re.search("(\w+)(\d+)", search)
    if r is None:
        raise ValueError(
            "Invalid search string: '{}' (must be '<element><ioni>')".format(search))
    elem, ioni = r.groups()
    elem = adjust_atomic_symbol(elem)
    ioni = int(ioni)
    return elem, ioni


# Formulas that can be recognized in PFANT molecule header information ("titulo")
# This exists for backward compatibility. New molecules should have its symbols informed separately
#
# **Careful** If you add entried, make sure everything is in uppercase
_BUILTIN_FORMULAS = {
     "MGH": ["MG", "H"],
     "C2": ["C", "C"],
     "CN": ["C", "N"],
     "CH": ["C", "H"],
     "13CH": ["A", "H"],
     "12C16O": ["C", "O"],
     "NH": ["N", "H"],
     "OH": ["O", "H"],
     "FEH": ["FE", "H"],
     "TIO": ["TI", "O"],
     "CO": ["C", "O"],
}

__TRBLOCK = [lambda x: x, lambda x: int(x), lambda x: greek_to_spdf(x.capitalize())]
# lambda functions to convert the parsed bits, in sync with (from_label, ..., to_spdf)
_PSS_TRANSFORMS = __TRBLOCK * 2

def parse_system_str(string):
    """
    Parses "system string" --> (from_label, from_mult, from_spdf, to_label, to_mult, to_spdf)

    Args:
        string: see convention below

    **Convention** system string::

        "from_label from_mult from_spdf_greek - from_label from_mult from_spdf_greek"
        or
        "label mult spdf_greek" (assumed initial and final state are the same).

        **Note** (*spdf*) are Greek letter names, case-INsensitive;
                 extra "+"/"-" (for example, in "SIGMA+") is ignored

    System string examples::

        "[A 2 Sigma - X 2 Pi]"

        "[X 1 SIGMA+]"

    """

    expr = re.compile(
        "\[\s*([a-zA-Z])\s*(\d+)\s*([a-zA-Z0-9]+)[+-]{0,1}\s*-+\s*\s*([a-zA-Z])\s*(\d+)\s*([a-zA-Z0-9]+)[+-]{0,1}\s*\]")
    groups = expr.search(string)
    if groups is not None:
        # TODO this may be giving error
        _pieces = [groups[i] for i in range(1, 7)]
    else:
        # Initial and final state are the same. Example "12C16O INFRARED [X 1 SIGMA+]"
        expr = re.compile("\[\s*([a-zA-Z])\s*(\d+)\s*([a-zA-Z0-9]+)[+-]{0,1}\s*\]")

        groups = expr.search(string)
        if groups is not None:
            _pieces = [groups[i] for i in range(1, 4)] * 2

        if groups is None:
            raise ValueError("Could not understand str '{}'".format(string))


    pieces = [f(piece) for f, piece in zip(_PSS_TRANSFORMS, _pieces)]

    return pieces


def split_molecules_description(descr):
    """Breaks PFANT molecule description into "(name) (system) (optional notes)" --> (name, system, notes)

    System is identified by enclosing square brackets ("[", "]")
    """

    match = re.match("(.+?)\s*(\[.+\])\s*(.*)", descr)

    if match is None:
        raise ValueError("Invalid PFANT molecule description: '{}'".format(descr))

    return match.groups()


def description_to_symbols(descr):
    """Finds molecular formula in description text and returns separate symbols

    This routine is similar to pfantlib.f90:assign_symbols_by_formula()

    It is used when the symbols are not informed separately
    after the first "#" in the molecule 'titulo'

    Args:
        descr: string

    Returns:
        list of two elements, e.g., [" C", " O"]

    Example:

    >>> import pyfant
    >>> pyfant.description_to_symbols("12C16O INFRARED  X 1 SIGMA+,   version 15/oct/98")
    [' C', ' O']
    """

    descr = descr.upper()
    for formula, symbols in _BUILTIN_FORMULAS.items():
        # Searches for formula at start or after whitespace
        if re.search(r'(^|\W){}([^0-9A-Z]|$)'.format(formula), descr):
            return [adjust_atomic_symbol(x) for x in symbols]
    return None
    # raise RuntimeError("Could not find a valid formula in description '{}'".format(descr))


def symbols_to_formula(symbols):
    """Converts two symbols to a formula as recorded in the 'molecule' table

    Args:
        symbols: 2-element list as returned by f311.filetypes.basic.description_to_symbols()

    Returns:
        str: examples: 'MgH', 'C2', 'CH'

    Formulas in the 'molecule' table have no isotope information
    """
    rec = re.compile("[a-zA-Z]+")
    symbols_ = [rec.search(x).group().capitalize() for x in symbols]
    symbols_ = ["C" if x == "A" else x for x in symbols_]
    if symbols_[0] == symbols_[1]:
        return "{}{}".format(symbols_[0], "2")
    else:
        return "".join(symbols_)

# **        ****                ******        ****                ******        ****
#   **    **    ******    ******      **    **    ******    ******      **    **    ******    ******
#     ****            ****              ****            ****              ****            ****
#
# Conversion and formatting routines: Branch-related
#

_iz_to_branch_map = {"1": "P", "2": "Q", "3": "R", "4": "P1", "5": "Q1", "6": "R1", "7": "P2",
                     "8": "Q2", "9": "R2", "10": "P3", "11": "Q3", "12": "R3", }
_branch_to_iz_map = dict(((value, key) for key, value in _iz_to_branch_map.items()))


# alternative mapping
_iz_to_branch_map_alt = {"1": "P1","2": "P12","3": "P21","4": "P2","5": "Q1","6": "Q12",
                         "7": "Q21","8": "Q2","9 ": "R1","10": "R12","11": "R21","12": "R2",}
_branch_to_iz_map_alt = dict(((value, key) for key, value in _iz_to_branch_map_alt.items()))


# another alternative mapping
_iz_to_branch_map_alt2 = {"1": "P1","2": "Q1","3": "R1","4": "P2", "5": "Q2","6": "R2",
                          "7": "P3","8": "Q3","9 ": "R3"}
_branch_to_iz_map_alt2 = dict(((value, key) for key, value in _iz_to_branch_map_alt2.items()))



def iz_to_branch(iz):
    """Converts BLB's 'iz' code to string P/Q/R/P1. Inverse of branch_to_iz()

    (see pfantlib.90:read_molecules())

    **Note** iz-to-branch conversion cannot be trusted because different molecules use different
             conventions. To solve this in the future, new PFANT molecular lines .dat files will
             have branch saved as string.

    TODO note above is important
    """
    return _iz_to_branch_map[str(iz)]


def branch_to_iz(br):
    """Converts branch P/Q/R/P1, etc. into BLB's 'iz' code

    Args:
        br: str, [P/Q/R][/1/2/3], for example "P", "P1"

    Returns:
        str: from "1" to "12"
    """
    return _branch_to_iz_map[br]


def iz_to_branch_alt(iz):
    """Alternative mapping used by Bruno Castilho's CH. Inverse of branch_to_iz_alt()

    This is the mapping found in Bruno Castilho's work for molecule CH
    (directory ATMOS/wrk4/bruno/Mole/CH, check file, e.g., sja000.dat and source selech.f)
    """
    return _iz_to_branch_map_alt[str(iz)]


def branch_to_iz_alt(br):
    """
    Alternative mapping used by Bruno Castilho's CH

    Args:
        br: str, [P/Q/R][1/12/21/2], for example "P1", "Q21"

    Returns:
        str: from "1" to "12"

    This is the mapping found in Bruno Castilho's work for molecule CH
    (directory ATMOS/wrk4/bruno/Mole/CH, check file, e.g., sja000.dat and source selech.f)
    """
    return _branch_to_iz_map_alt[br]

def branch_to_iz_alt2(br):
    """
    Still another alternative mapping (for triplets)

    Args:
        br: str: P1/P2/P3/Q1/Q2/Q3/R1/R2/R3

    Returns:
        str: from "1" to "9"

    This is the mapping found in Bruno Castilho's work for molecule NH
    (directory ATMOS/wrk4/bruno/Mole/NH, check file, e.g., sj0000.dat)
    """
    return _branch_to_iz_map_alt2[br]
