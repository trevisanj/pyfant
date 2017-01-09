# TODO list

  - ~~OK implement ToScalar_UseNumPyFunc~~
  - ~~OK add combobox to XToScalar~~
  - ~~OK Smarter loading of Full Cube~~
  
  
  
  - ~~FIX MOLECULES FILE!!!!!
    comparing old x new moleculagrade
    perhaps best it is to keep both versions: contemplating diversity and whoever did whatever
    best would be to create an editor to mingle the molecules~~
  
  
  - Normalize("1") cause re-sampling, sth is not right
  - Fill origin when converting from FileFullCube to FileSpectrumList (somehow)
  - Get rid of WSpectrumList "More..." tab (make sure everything is implemented as blocks)
  - XHelpDialog is too ugly
  - Investigate what this a_XAtomsHistogram is about
  - Make sun Grevesse 1998 as default sun for pyfant
  - ~~legend=False in plot_*()~~
  - ~~p.conf.sid.clean() not intuitive~~
  - ~~easier to work with command line options~~
  - ~~nulbad load_result~~
  - Warn assumptions in ConvMol
  - ~~Resolve branches for other molecules~~ HITRAN OK


## Conversion of molecular lines from other formats to PFANT

### General

  - Yes allow one to change the constants in the GUI, especially the molecule-wide constants, 
    because apparently some of them are **not molecule-wide** 
    (such as `S` (found this cue: `S = 0.5   # dubleto: X2 PI`), or
    `CRO` (found this cue: 
    `delta Kronecker (2-delta_{Sigma, 0}); 
     delta_{Sigma, 0} = 0 for Sigma transitions; 1 for non-Sigma transitions`)). The best
     way to solve this now is to allow the user of `convmol.py` to have some freedom while
     converting
  - ~~Sort S~~ ~~**ONLY MISSING THE DOCUMENTATION**~~
  - ~~Sord DELTA_K~~
  - Maybe S and DELTA_K are state-specific
  - Find scaling factor for Kurucz linelists ON THE WAY ...
  - Compare the two and show BLB

### Questions to BLB

  - ~~J2l: do we write integer or half-integer value? (I am now saving the half-integer J2l, despite "ojo, estamos colocando J2L-0.5!")~~
  - ~~Why different scale factors for each transition? tried 730 for 0-29 but does not apply to others
    it is weird because loggf Kurucz varies greatly in magnitude from transition to transition, but HLFs in PFANT do not so much~~
    **A: Franck-Condon Factors sometimes incorporated, sometimes in transition "header"**
  - ~~FEL in molecular lines file not like Bruno page 29 (and some have fel=1.0 which gives huge lines)!!!!!~~
    **Same as previous question: FEL sometimes incorporated, sometimes in transition "header"**
  - Are Kurucz lines with spin 1/2 either triplet/quintet?
    **Actually Apparently not, since the old `OHbrunook.dat` has branch up to 9
  - **Could the (P/Q/R from delta_J) + (spin 1/2) + (e/f determine the branch?) (I could check this)**
    **Apparently yes, but ths spli 1/2 didn't yield as expected**
  - ~~Where does the normalization of the HLF come from?~~
  - ~~Normalization: times 2 or times 1.499 ...~~ 
  - ~~FVVP, FVVQ, FVVR ??~~
    **Franck-Condon Factors**
  - ~~P/Q/R is for singlet & P1/P2/Q1/Q2/R1/R2 for dublet?~~
    **ŷêŝ**
  - ~~The only thing we need from the molecular lines file is the wavelength and the branch, right?~~
    **ýéś**
  - ~~Most important seems to be the BRANCH!! Or work around with loggf~~
    **Understand what Bruno did, then maybe work with loggf**
  
**FeH, C2 & CN (the latter especially red)** PFANT is from laboratory & is better


  - Corrigir ...lamm1.f
  - Converter o arquivo do Kurucz usando agora o Branch
  - O que do Kurucz corresponde ao que do PFANT (o que é o loggf? = SJ*v'v''*...)
  - PFANT no futuro poderia utilizar o gf do Kurucz
  - TiO (tripletos) do Kurucz
  - CH do Plez é o melhor de todos
  
### Show BLB

  - Plots from cli-...:
    - 0..29
    - 2..51 with/without scaling
     
  
  
### Franck-Condon factors

The Franck-Condon Factor (FCF; `qqv`) is assumed to be 1.0 in the conversions
implemented (files `pyfant.convmol.conv_*.py`). Actually, looking into
the original molecules file, `moleculagrade.dat` (PC version), from 1060
existing transitions, only in 58 transitions the FCF is < 1.0
 
 So, maybe assuming 1.0 is not much of a problem...
  
 ### Branches
 
 Branches P/Q/R can be derived from (delta J), but branches P1, Q1, R1,
  P2, Q2, R2, P3, Q3, R3 require extra information. The Fortran program
  `extraeoh.f` by Jorge Melendez (converting from a 100-character HITRAN format)
  gives cues on how to figure this out. This program translates 
  (PP/QQ/RR, 11/22, e/f) into P/Q/R/P1/Q2/R1/P2/Q2/R2/P3/Q3/R3, where:
  
- PP, QQ, RR are considered to be branches P, Q, R respectively
- Lines tieh other letter combinations -- such as PQ, QR -- are skipped
- e/f is the "Symmetry" according to (Rothman 2003) Table 4
- 11/22 is undocumented in (Rothman 2003); variable name in `extraeoh.f` is `pi12` if this says something


### State database

For each line in a molecular lines file, it is necessary to know a set of constants, 
some are molecule-specific, others are molecular state-specific. For example, _beta_e_, _omega_e_ etc.

I created `moldb.sqlite`, database to store constants, kicking off from information downloaded from
the NIST Web Book using a robot that I created (try `get-nist-mol.py` to consult the NIST Web Book
and print a table with all the states for a single molecule). This database can be
created from scratch using `_create-moldb.py` and it is shipped with `pyfant`
(directory `pyfant/data/default`). It is actually used as a starting point for you to save your
own molecular constants database locally.

This database is used to calculate the values `ggv`, `ddv`, `bbv` that go
into PFANT molecular lines files

**Note** `ggv`, `ddv`, `bbv` depend only on the molecular constants
 and on (_v'_, _v''_), the latter being part of the molecular line description 
 in most file types. Conversion to PFANT actually groups the lines by (_v'_, _v''_) 

The **TODO**: add columns to table `state` and implement searches to allow the molecular constants
to be found automatically. Currently, `convmol.py` requires you to inform which molecule and state a particular file
is about, however some files (_e.g._, VALD3) have mixed information for a lot of different molecules and states.
Therefore, the information "X ²Pi" needs to be separated in different fields to be made searchable.

For some files, like Kurucz, one may still have to inform the molecule and state information.
  

### TurboSpectrum

Not sure about converting from TurboSpectrum, since VALD3 can be a source for both TurboSpectrum and PFANT

### Convert from PFANT to other formats

This should be done in Fortran, not Python, because it has to go through most PFANT calculations.
A 5th Fortran executable (the other four being `innewmarcs`, `hydro2`, `pfant` and `nulbad`) 
was already created, named `convmol` (source: `PFANT/fortran/convmol.f90`) that can save in VALD3 extended format,
but the calculations were not verified.


 ### Plan
 
 - Try to reproduce the OH from source of lines **Kurucz OHAX**
  
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
