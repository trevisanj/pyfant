"""Class & metaclass stuff"""


__all__ = ["AttrsPart", "froze_it", "collect_doc"]


from functools import wraps


def froze_it(cls):
    """
    Decorator to prevent from creating attributes in the object ouside __init__().

    This decorator must be applied to the final class (doesn't work if a
    decorated class is inherited).

    Yoann's answer at http://stackoverflow.com/questions/3603502
    """
    cls._frozen = False

    def frozensetattr(self, key, value):
        if self._frozen and not hasattr(self, key):
            raise AttributeError("Attribute '{}' of class '{}' does not exist!"
                  .format(key, cls.__name__))
        else:
            object.__setattr__(self, key, value)

    def init_decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self._frozen = True
        return wrapper

    cls.__setattr__ = frozensetattr
    cls.__init__ = init_decorator(cls.__init__)

    return cls


class AttrsPart(object):
    """
    Implements a new __str__() to print selected attributes.

    Note: when descending from this class, set the attrs class variable.
    """

    # for __str__()
    attrs = None
    # for __repr__()
    # Optional; if not set, will be overwritten with self.attrs at __init__()
    less_attrs = None

    def __init__(self):
        if self.less_attrs is None:
            self.less_attrs = self.attrs

    def __repr__(self):
        assert self.attrs is not None, "Forgot to set attrs class variable"

        s_format = "{:>%d} = {}" % max([len(x) for x in self.attrs])
        l = []
        for x in self.attrs:
            y = self.__getattribute__(x)
            if isinstance(y, list):
                # list gets special treatment
                l.append(("%s = [\n" % x)+
                 (" \n".join([z.one_liner_str() if isinstance(z, AttrsPart)
                             else repr(z) for z in y]))+"\n]")
            else:
                l.append(s_format.format(x, self.__getattribute__(x)))

        s = "\n".join(l)
        return s

    def one_liner_str(self):
        assert self.less_attrs is not None, "Forgot to set attrs class variable"
        s_format = "{}={}"
        s = "; ".join([s_format.format(x, self.__getattribute__(x)) for x in self.less_attrs])
        return s


def collect_doc(module, prefix=None, flag_exclude_prefix=True):
    """
    Collects class names and docstrings in module for classes starting with prefix

    Arguments:
        module -- Python module
        prefix -- argument for str.startswith(); if not passed, does not filter (not recommended)
        flag_exclude_prefix -- whether or not to exclude prefix from class name in result

    Returns: [(classname0, docstring0), ...]
    """

    assert not (prefix is None and flag_exclude_prefix), "Cannot exclude prefix if prefix was not passed"

    ret = []
    for attrname in dir(module):
        if not (prefix is None or attrname.startswith(prefix)):
            continue

        attr = module.__getattribute__(attrname)
        ret.append((attrname if not flag_exclude_prefix else attrname[len(prefix):], attr.__doc__))

    return ret