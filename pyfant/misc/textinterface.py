__all__ = ["fmt_ascii_h1", "fmt_error", "print_error", "menu", "format_progress", "markdown_table",
           "print_skipped"]


# #################################################################################################
# # Text interface routines - routines that are useful for building a text interface


def fmt_ascii_h1(s):
    """Returns string enclosed in an ASCII frame, with \n line separators. Does not end in \n."""
    n = len(s)
    return "+"+("-"*(n+2))+"+\n"+ \
           "| "+s+" |\n"+ \
           "+"+("-"*(n+2))+"+"


def fmt_error(s):
    """Standardized embellishment. Adds formatting to error message."""
    return "!! %s !!" % s


def print_error(s):
    """Prints string as error message."""
    print((fmt_error(s)))


def menu(title, options, cancel_label="Cancel", flag_allow_empty=False, flag_cancel=True, ch='.'):
  """Text menu.

  Arguments:
    title -- menu title, to appear at the top
    options -- sequence of strings
    cancel_label='Cancel' -- label to show at last "zero" option
    flag_allow_empty=0 -- Whether to allow empty option

  Returns:
    option -- an integer: None; 0-Back/Cancel/etc; 1, 2, ...

  Adapted from irootlab menu.m"""

  no_options, flag_ok, lt = len(options), 0, len(title)
  option = None  # result
  min_allowed = 0 if flag_cancel else 1  # minimum option value allowed (if option not empty)

  while True:
    print("")
    print(("  "+ch*(lt+8)))
    print(("  "+ch*3+" "+title+" "+ch*3))
    print(("  "+ch*(lt+8)))
    for i, s in enumerate(options):
      print(("  %d - %s" % (i+1, s)))
    if flag_cancel: print(("  0 - << (*%s*)" % cancel_label))
    try:
        s_option = input('? ')
    except:
        print("")

    n_try = 0
    while True:
      if n_try >= 10:
        print('You are messing up!')
        break

      if len(s_option) == 0 and flag_allow_empty:
        flag_ok = True
        break

      try:
        option = int(s_option)
        if min_allowed <= option <= no_options:
          flag_ok = True
          break
      except ValueError:
        print("Invalid integer value!")

      print(("Invalid option, range is [%d, %d]!" % (0, no_options)))

      n_try += 1
      s_option = input("? ")

    if flag_ok:
      break
  return option


def format_progress(i, n):
    """Returns string containing a progress bar, a percentage, etc."""
    if n == 0:
        fraction = 0
    else:
        fraction = float(i)/n
    LEN_BAR = 25
    num_plus = int(round(fraction*LEN_BAR))
    s_plus = '+'*num_plus
    s_point = '.'*(LEN_BAR-num_plus)
    return '[%s%s] %d/%d - %.1f%%' % (s_plus, s_point, i, n, fraction*100)



def markdown_table(headers, data):
    """
    Creates MarkDown table. Returns list of strings

    Arguments:
      headers -- sequence of strings: (header0, header1, ...)
      data -- [(cell00, cell01, ...), (cell10, cell11, ...), ...]
    """

    maxx = [max([len(x) for x in column]) for column in zip(*data)]
    maxx = [max(ll) for ll in zip(maxx, [len(x) for x in headers])]
    mask = " | ".join(["%%-%ds" % n for n in maxx])

    ret = [mask % headers]



    ret.append(" | ".join(["-"*n for n in maxx]))
    for line in data:
        ret.append(mask % line)
    return ret


def print_skipped(reason):
    """Standardized printing for when a file was skipped."""
    print(("   ... SKIPPED (%s)." % reason))