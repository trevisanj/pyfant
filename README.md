# pyfant

Welcome!! `pyfant` is a Python interface for the PFANT Spectral Synthesis Software for use in Astronomy. 

PFANT project: http://github.com/trevisanj/PFANT

# Table of contents

  1. [Introduction](#S1)
  2. [Installation](#S2)
  3. [Command-line tools](#S3)
  4. [Graphical interfaces](#S4)
  5. [Miscellanea how-to](#S5)
     5.1 [Converting atomic lines from VALD3](#S5_1)
  6. [Library](#S6)
  7. [Troubleshooting](#S7)


# <a name=S1></a>1 Introduction

Some features:
  - graphical user interfaces ([see screenshots](screenshots.md)):
    - run Fortran binaries in parallel: `x.py`
    - file explorer: `explorer.py`
    - edit data files: `ated.py`, `mled.py`, `mained.py`, `abed.py`
    - etc
  - handles some types of FITS files (_e.g._, spectrum, data cube)
  - command-line tools for
    - plotting, PDF generation: `plot-spectra.py`, `save-pdf.py`
    - cutting: `cut-atoms.py`, `cut-molecules.py`, `cut-spectra.py`
    - running: `run4.py`
    - VALD3 conversion: `vald3-to-atoms.py`
    - etc
  - object-oriented library for Python coding
     

# 2 <a name=S2></a>Installation

## 2.0 Required Python version

pyfant was developed for Python 2.7.xx

## 2.1 Clone the repository 

```shell
git clone https://github.com/trevisanj/pyfant
```

## 2.2 Run the setup script

```shell
cd pyfant
sudo python setup.py develop
```

:notes: The above may not work, or work even if you don't have all the required
Python packages installed. Please make sure you have all the packages below
installed on your system.

## 2.3 Required Python packages


Package name  | Possible way to install
------------- | ---
matplotlib    | apt-Linux: `sudo apt-get install python-matplotlib`
scipy         | apt-Linux: `sudo apt-get install python-scipy`
pyqt4         | apt-Linux: `sudo apt-get install python-qt4`
              | Windows: download Python 2.7 installer at https://riverbankcomputing.com/software/pyqt/download
fortranformat | All systems: `[sudo] pip install fortranformat`
astropy       | apt-Linux: `sudo apt-get install python-astropy`
              | All systems: `[sudo] pip install astropy`

**Linux users:** you may have to `sudo` your `pip` commands.



# <a name=S3></a> Command-line tools

To get an updated list of available tools, run `programs.py`.

# <a name=S4></a> Graphical interfaces

#### 3.3.1 ```x.py```: PFANT launcher

  1. Starting again from scratch:

```shell
mkdir mystar
cd mystar
copy-star.py sun
link.py common
```

then

```shell
x.py
```

Now, for example:

  2. Take some time to explore Tabs 1, 2 and 3 (Alt+1, Alt+2, Alt+3). Tab 4 ("multi mode") will be explained later.

  3. Once you are done making changes, click on "Submit single job" button. A new window named "Runnables Manager" opens.

  4. When the "Status" column shows "nulbad finished", double-click on the table item
     ("PFANT explorer" window opens).

  5. Double-click on "flux.norm". Note that it turns green.

  6. Double-click on "Plot spectrum" (spectrum appears).
 
#### 3.3.2 `explorer.py`: PFANT Explorer

```shell
explorer.py
```

This file-explorer-like application provides visualization/editing abilities for a number
of relevant file types.


## 5 <a name=S5></a> Miscellanea how-to

### 5.1 <a name=S5_1></a> Converting "VALD3 extended" format atomic lines

The Vienna Atomic Line Database (VALD) is "a 
collection of atomic and molecular transition parameters of astronomical interest"
(http://vald.astro.uu.se/).


To convert from the "VALD3 extended" to a "PFANT atomic lines" file:

```shell
vald3-to-atoms.py <prefix>.vald3x
tune-zinf atoms-<prefix>-untuned.dat
```

This is done in two steps. The first step, `vald3-to-atoms.py` does the actual conversion
(which is quick) and saves a file, _e.g._, `atoms.dat`

The second step (which is time-consuming) is performed by `tune-zinf.py` and aims
to tune an important parameter used by the `pfant` Fortran binary.

It is recommended to use the tool `cut-atoms.py` to cut the file converted by
`vald3-to-atoms.py` to a wavelength region of interest before running `tune-zinf.py`.

For more information, see help for `vald3-to-atoms.py`, `tune-zinf.py`,
`cut-atoms.py` (call these scripts with `--help` option).


# <a name=S6></a> Library

## Minimal example

```python
from pyfant import *
obj = Pfant()
obj.run()
```
This is equivalent to running `pfant` from the command line.

## Running innewmarcs, hydro2, pfant, nulbad in sequence

```python
from pyfant import *
obj = Combo()
obj.run()
```

## More examples

  - The _demos_ directory contains a few (non-exhaustive) examples of how
    to use pyfant to perform different tasks. [](demos/README.md).

  - The _scripts_ directory, which contains tools, is also a good source of
    examples.
  

# <a name=S7></a>7 Troubleshooting

## Tracking down why Fortran binaries fail to run

pyfant creates a "session directory" named `session-xxx` every time it attempts
to run a PFANT binary. Each of these directories will always contain at least two files:
  - _commands.log_ -- this is the command lines attempted. You can copy-paste this
    line in your console to see how the Fortran binary goes.
  - _fortran.log_ -- messages printed by the Fortran binary.

Commonly, inspecting these files will be enough to figure out what happened.

Your current directory will also have a file named _python.log_, containing
debug/info/warning/error messages from Python.

(**new!**) Now `explorer.py` has a "Collect Fortran errors" button, which opens
all files names `fortran.log` in search of errors.