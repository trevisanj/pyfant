Installation
============

.. note:: As of July 2023, the recommended Python version is 3.11 running in Anaconda/Miniconda environment
          (see `F311` instructions below).

Pre-requisites
--------------

PFANT
~~~~~

The PFANT spectral synthesis software (Fortran) installation instructions can be found at
`<http://trevisanj.github.io/PFANT/install.html>`_.

F311
~~~~

Before installing PyFANT, please follow the instructions to install the ``f311`` package here: `<http://trevisanj.github.io/f311/install.html>`_.
``f311`` is a requisite.

Installing PyFANT
-----------------

Installing PyFANT in the majority of cases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once ``f311`` is installed, you can install `PyFANT` like this::

    pip install pyfant

Installing PyFANT in developer mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is an alternative to `pip` which allows one to browse and modify the Python source code.

First clone the `pyfant` GitHub repository:

.. code:: shell

   git clone ssh://git@github.com/trevisanj/pyfant.git

or

.. code:: shell

   git clone http://github.com/trevisanj/pyfant

Then, install PyFANT in **developer mode**:

.. code:: shell

   cd pyfant
   python setup.py develop

Upgrading package ``pyfant``
--------------------------

If package ``pyfant`` is already installed, but you need to install a new version, please follow these instructions.

Upgrading in the majority of cases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Package ``pyfant`` can be upgraded to a new version by typing::

    pip install pyfant --upgrade

Upgrading PyFANT in developer mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enter the `pyfant` repository (directory) cloned from Github, then type::

    git pull
    python setup.py develop
