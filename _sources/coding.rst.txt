Coding using the API
====================

This section contains a series of examples on how to use the PFANT Fortran executables from a
Python script. These "bindings" to the Fortran binaries, together with the ability to load,
manipulate and save PFANT data files allow for complex batch operations.

Spectral synthesis
~~~~~~~~~~~~~~~~~~

The following code generates :numref:`figsyn0`.

.. literalinclude:: ../examples/synthesis/synthesis-simple.py

.. _figsyn0:

.. figure:: figures/norm-convolved.png
   :align: center

   -- ``pfant`` (file "flux.norm") and ``nulbad`` outputs.


Spectral synthesis - convolutions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following example convolves the synthetic spectrum (file "flux.norm") with Gaussian profiles of
different FWHMs (:numref:`figsyn1`).

.. literalinclude:: ../examples/synthesis/synthesis-many-convolutions.py

.. _figsyn1:

.. figure:: figures/many-convs.png
   :align: center

   -- single ``pfant`` output and several ``nulbad`` outputs.

Spectral synthesis - Continuum
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code generates :numref:`figcont`.

.. literalinclude:: ../examples/synthesis/synthesis-continuum.py

.. _figcont:

.. figure:: figures/continuum.png
   :align: center

   -- continuum.

Spectral synthesis - Separate atomic species
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PFANT atomic lines files contains wavelength, log_gf and other tabulated information for several
(element, ionization level) atomic species.

The following code calculates isolated atomic spectra for a list of arbitrarily chosen atomic
species (:numref:`figatoms`).

.. literalinclude:: ../examples/synthesis/synthesis-atoms.py

.. _figatoms:

.. figure:: figures/synthesis-atoms.png
   :align: center

   -- atomic lines synthesized separately for each species.

Spectral synthesis - Separate molecules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following code generates :numref:`figmol0`, :numref:`figmol1`,
and additional plots not shown here.

.. literalinclude:: ../examples/synthesis/synthesis-molecules.py

.. _figmol0:

.. figure:: figures/synthesis-molecules-0.png
   :align: center

   -- molecular lines synthesized separately for each species

.. _figmol1:

.. figure:: figures/synthesis-molecules-1.png
   :align: center

   -- molecular lines synthesized separately for each species.


Gaussian profiles as ``nulbad`` outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``nulbad`` is one of the Fortran executables of the PFANT package. It is the one that convolves
the synthetic spectrum calculated by ``pfant`` with a Gaussian profile specified by a "fwhm"
parameter (:numref:`figsyn5`).

.. literalinclude:: ../examples/synthesis/gaussian-profiles.py

.. _figsyn5:

.. figure:: figures/gaussian-profiles.png
   :align: center

   -- Gaussian profiles illustrated for different FWHMs.


Plot hydrogen profiles
~~~~~~~~~~~~~~~~~~~~~~

The following code generates :numref:`figsyn6`.

.. literalinclude:: ../examples/plot-hydrogen-profiles/plot-hydrogen-profiles.py

.. _figsyn6:

.. figure:: figures/hydrogen-profiles.png
   :align: center

   -- hydrogen lines profiles as calculated by ``hydro2``.


Import Kurucz' molecular linelist file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../docs/examples/filetypes/import-kurucz.py

This code should print the following:

.. code-block:: none

    KuruczMolLine(lambda_=2877.558,
                  loggf=-14.533,
                  J2l=23.0,
                  E2l=2354.082,
                  Jl=24.0,
                  El=37095.578,
                  atomn0=6,
                  atomn1=6,
                  state2l='a',
                  v2l=0,
                  lambda_doubling2l='e',
                  spin2l=1,
                  statel='d',
                  vl=10,
                  lambda_doublingl='e',
                  spinl=3,
                  iso=12)
