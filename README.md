# pyfant

Welcome!!

pyfant is a Python interface for the 
[PFANT Spectral Synthesis Software](PFANT project: http://github.com/trevisanj/PFANT)
for use in Astronomy.

Appart from spectral synthesis, it provides tools of conversion, data editing,
and visualization, and a programming library to embed spectral synthesis into your code.

# Table of contents

  1. [Introduction](#S1)
  2. [Installation](#S2)
  3. [Handled file types](#S3)
  4. [Tasks](#S4)
  5. [Programming with `pyfant`](#S5)
  6. [Troubleshooting](#S6)


# <a name=S1></a>1 Introduction

The `pyfant` Python package was created as a Python interface for PFANT, a Fortran-developed
Spectral Synthesis Software for use in Astronomy (http://github.com/trevisanj/PFANT).

Spectral Synthesis Softwares (SSS) have several applications in Astronomy. Spectral synthesis is a
crucial step in optimization algorithms, in which the synthetic spectrum is compared with the
measure spectrum of a star, in order to determine stellar properties -- such as temperature,
metallicity, and chemical abundances -- in an iterative fashion.

`pyfant` was first created with the intention to provide an object-oriented library to develop such
algorithms in Python. It allows one to create several "spectral synthesis cases" (_e.g._ similar
calculations where only the chemical abundance of one element will vary slightly) and run these cases
in parallel.

The package has since evolved to provide many graphical and command-line applications to perform
many convenient tasks:
  - editors for many of the file types involved
  - plotting tools
  - conversion of atomic and molecular lines from/to standards from other research groups

`pyfant` is under active development, and we hope that you
will find it useful. If you would like to contribute or have any issues or suggestions, please send
a message to juliotrevisan@gmail.com

# 2 <a name=S2></a>Installation

  - Install required software
  - Clone the repository
  - Run the setup script

## 2.1 Required Software

**Python version:** Python 3.xx

## 2.1.1 Python Packages

Please make sure you have all the packages below
installed on your system.

  - matplotlib   
  - scipy        
  - PyQt4        
  - fortranformat
  - astropy      
  - configobj

Possible way to install on Debian-based Linux:
```shell
sudo apt-get install python3-matplotlib python3-scipy python3-pyqt4 python3-astropy python3-pip python3-configobj
sudo pip3 install fortranformat
```

## 2.2 Clone the repository 

```shell
git clone https://github.com/trevisanj/pyfant
```

or

```shell
git clone ssh://git@github.com/trevisanj/pyfant.git
```

## 2.3 Run the setup script

```shell
cd pyfant
sudo python3 setup.py develop
```



# <a name=S3></a>3 Programs Available

:bulb: To print a list of all command-line tools, run `programs.py`

Graphical applications:
  - `abed.py` -- Abundances file editor
  - `ated.py` -- Atomic lines file editor
  - `cubeed.py` -- Data Cube Editor
  - `explorer.py` -- PFANT Explorer --  list, visualize, and edit data files (_à la_ File Manager)
  - `mained.py` -- Main configuration file editor
  - `mled.py` -- Molecular lines file editor
  - `splisted.py` -- FileSpectrumList editor with import/export FileFullCube
  - `tune-zinf.py` -- Tunes the zinf parameter for each atomic line in atomic lines file.
  - `x.py` -- PFANT Launcher

Command-line tools:
  - `copy-_star.py` -- Copies stellar data files to local directory.
  - `create-grid.py` -- Model Grid Creator from MARCS atmospheric models 
  - `cut-atoms.py` -- Cuts atomic lines file to wavelength interval specified.
  - `cut-molecules.py` -- Cuts molecular lines file to wavelength interval specified.
  - `cut-spectrum.py` -- Cuts spectrum file to wavelength interval specified. Saved in 2-column format.
  - `link.py` -- Creates symbolic links to PFANT data files as an alternative to copying these (sometimes large) files into local directory.
  - `plot-spectra.py` -- Plot spectra to screen or PDF.
  - `programs.py` -- Lists all Fortran/Python programs available (PFANT + pyfant).
  - `run4.py` -- Runs the four Fortran binaries in sequence: innewmarcs, hydro2, pfant, nulbad.
  - `save-pdf.py` -- Looks for file "flux.norm" inside directories session-* and saves one figure per page in a PDF file.
  - `vald3-to-atoms.py` -- Converts VALD3 atomic/molecular lines file to PFANT atomic lines file.


# <a name=S3></a>3 Handled file types

Handled file types:

File type                                                     | Default filename (for all purposes)
------------------------------------------------------------- | -----------------------------------
"Lambda-flux" Spectrum (text file with two columns)           | -
FITS Data Cube                                                | default.fullcube
FITS Sparse Data Cube (storage to take less disk space)       | default.sparsecube
FITS Spectrum                                                 | -
FITS Spectrum List                                            | default.splist
MARCS Opacity Model                                           | modeles.opa
MARCS Atmospheric Model                                       | -
                                                              |
PFANT Stellar Main Configuration                              | main.dat
PFANT Stellar Chemical Abundances                             | abonds.dat
PFANT Stellar Dissociation Equilibrium Information            | dissoc.dat
PFANT Atomic Lines                                            | atoms.dat
PFANT Molecular Lines                                         | molecules.dat
PFANT Hydrogen Line Profile                                   | thalpha
PFANT Hygrogen Lines Map                                      | hmap.dat
PFANT Partition Function                                      | partit.dat
PFANT Atmospheric Model or grid of models (binary file)             | modeles.mod
PFANT Atmospheric model or grid of models (with opacities included) | grid.moo
PFANT Spectrum (`nulbad` output)                                    | -
PFANT Spectrum (`pfant` output)                                     | flux.norm
`x.py` Command-line Options                                         | options.py
`x.py` Differential Abundances and FWHMs (Python source)            | abxfwhm.py


# <a name=S4></a>4 Tasks

This section briefly describes some tasks that can be performed with `pyfant` applications.

## 4.1 Spectral Synthesis from Scratch

Shell commands:
```shell
mkdir mystar
cd mystar
copy-star.py
link.py common
x.py
```

The last command will invoke the PFANT Launcher: 

  1. Change parameters in Tab 1/2/3 (Tab 4 is a different story) 
  2. Click on the "Submit single job" button: a new window named "Runnables Manager" opens
  3. When the "Status" column shows "nulbad finished", double-click on the table item: "PFANT Explorer" window opens
  4. Double-click on "flux.norm": turns green (if wasn't so)
  5. Double-click on "Plot spectrum": spectrum appears

## 4.2 Browsing files with PFANT Explorer

```shell
explorer.py
```

This application allows you to navigate through your file system and visualize/edit files,
depending on their type. 

You can select several spectral files and plot them all at once (stacked in different sub-plots,
or overlapped in a single plot).

## 4.3 <a name=S4_3></a> Converting "VALD3 extended" format atomic lines

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


# <a name=S6></a> Programming using `pyfant`

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

  - [`run4.py` source code](scripts/run4.py)
  

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

:bulb: `explorer.py` has a "Collect Fortran errors" button, which
recurses directories in search for error/warning messages in all files named `fortran.log`

## Metallicity/temperature/gravity of star is outside range in the grid of models
  
You can activate option "--allow True" to make bypass this check, but beware that the calculation
may be incorrect.

This can be done in the command line, _e.g._, `run4.py --allow T`, or check option "--alow"
in Tab 3 of `x.py`.