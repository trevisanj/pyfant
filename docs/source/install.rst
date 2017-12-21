Installation
============

If you have both **Python 3** and **PFANT** installed, then simply type::

    pip install pyfant


Pre-requisites
--------------

PFANT
~~~~~

The PFANT spectral synthesis software installation instructions can be found at
`<http://trevisanj.github.io/PFANT/install.html>`_.

Python 3
~~~~~~~~

If you need to set up your Python 3 environment, one option is to visit project F311
installation instructions at `<http://trevisanj.github.io/install.html>`_. That page also
provides a troubleshooting section that applies.

Installing PyFANT in developer mode
-----------------------------------

This is an alternative to the "pip" at the beginning of thie section.

Use this option if you would like to download and modify the Python source code.

First clone the "pyfant" GitHub repository:

.. code:: shell

   git clone ssh://git@github.com/trevisanj/pyfant.git

or

.. code:: shell

   git clone http://github.com/trevisanj/pyfant

Then, install PyFANT in **developer** mode:

.. code:: shell

   cd pyfant
   python setup.py develop

Upgrade ``pyfant``
------------------

Package ``pyfant`` can be upgraded to a new version by typing::

    pip install pyfant --upgrade
