Pyfant Installation
===================

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

Installing Pyfant in developer mode
-----------------------------------

This option allows you to download and modify the source code.

Clone the "pyfant" GitHub repository:

.. code:: shell

   git clone ssh://git@github.com/trevisanj/pyfant.git

or

.. code:: shell

   git clone http://github.com/trevisanj/pyfant

Then, install Pyfant in **developer** mode:

.. code:: shell

   cd pyfant
   python setup.py develop

Upgrade ``pyfant``
----------------

Pacakge ``pyfant`` can be upgraded to a new version by typing::

    pip install pyfant --upgrade --no-deps

Contact
~~~~~~~
For bugs reports or suggestions, please open an issue at the project
site on `GitHub <http://github.com/trevisanj/pyfant>`_.