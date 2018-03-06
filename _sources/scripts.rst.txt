Index of applications (scripts)
===============================

.. only:: html

    This script was already executed. It can be executed only once.
    pyfant -- Python interface to the PFANT spectral synthesis software (Fortran)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Graphical applications
    ^^^^^^^^^^^^^^^^^^^^^^
    
    * :doc:`abed.py <autoscripts/script-abed>`: Abundances file editor
    * :doc:`ated.py <autoscripts/script-ated>`: Atomic lines file editor
    * :doc:`convmol.py <autoscripts/script-convmol>`: Conversion of molecular lines data to PFANT format
    * :doc:`mained.py <autoscripts/script-mained>`: Main configuration file editor.
    * :doc:`mced.py <autoscripts/script-mced>`: Editor for molecular constants file
    * :doc:`mled.py <autoscripts/script-mled>`: Molecular lines file editor.
    * :doc:`moldbed.py <autoscripts/script-moldbed>`: Editor for molecules SQLite database
    * :doc:`optionsed.py <autoscripts/script-optionsed>`: PFANT command-line options file editor.
    * :doc:`tune-zinf.py <autoscripts/script-tune-zinf>`: Tunes the "zinf" parameter for each atomic line in atomic lines file
    * :doc:`x.py <autoscripts/script-x>`: PFANT Launcher -- Graphical Interface for Spectral Synthesis
    
    Command-line tools
    ^^^^^^^^^^^^^^^^^^
    
    * :doc:`copy-star.py <autoscripts/script-copy-star>`: Copies stellar data files (such as main.dat, abonds.dat, dissoc.dat) to local directory
    * :doc:`create-grid.py <autoscripts/script-create-grid>`: Merges several atmospheric models into a single file (_i.e._, the "grid")
    * :doc:`cut-atoms.py <autoscripts/script-cut-atoms>`: Cuts atomic lines file to wavelength interval specified
    * :doc:`cut-molecules.py <autoscripts/script-cut-molecules>`: Cuts molecular lines file to wavelength interval specified
    * :doc:`hitran-scraper.py <autoscripts/script-hitran-scraper>`: Retrieves molecular lines from the HITRAN database [Gordon2016]
    * :doc:`link.py <autoscripts/script-link>`: Creates symbolic links to PFANT data files as an alternative to copying these (sometimes large) files into local directory
    * :doc:`merge-molecules.py <autoscripts/script-merge-molecules>`: Merges several PFANT molecular lines file into a single one
    * :doc:`nist-scraper.py <autoscripts/script-nist-scraper>`: Retrieves and prints a table of molecular constants from the NIST Chemistry Web Book [NISTRef]
    * :doc:`nulbad.py <autoscripts/script-nulbad>`: Convolve spectrum with Gaussian profile.
    * :doc:`run-multi.py <autoscripts/script-run-multi>`: Runs pfant and nulbad in "multi mode" (equivalent to Tab 4 in "x.py")
    * :doc:`run4.py <autoscripts/script-run4>`: Runs the four Fortran binaries in sequence: `innewmarcs`, `hydro2`, `pfant`, `nulbad`
    * :doc:`vald3-to-atoms.py <autoscripts/script-vald3-to-atoms>`: Converts VALD3 atomic/molecular lines file to PFANT atomic lines file.
    
    

.. only:: latex

    This chapter is a reference to all scripts in project PyFANT

    .. toctree::
        :maxdepth: 1

        autoscripts/script-copy-star
        autoscripts/script-create-grid
        autoscripts/script-cut-atoms
        autoscripts/script-cut-molecules
        autoscripts/script-hitran-scraper
        autoscripts/script-link
        autoscripts/script-merge-molecules
        autoscripts/script-nist-scraper
        autoscripts/script-nulbad
        autoscripts/script-run-multi
        autoscripts/script-run4
        autoscripts/script-vald3-to-atoms
        autoscripts/script-abed
        autoscripts/script-ated
        autoscripts/script-convmol
        autoscripts/script-mained
        autoscripts/script-mced
        autoscripts/script-mled
        autoscripts/script-moldbed
        autoscripts/script-optionsed
        autoscripts/script-tune-zinf
        autoscripts/script-x