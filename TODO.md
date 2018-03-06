# pyfant TODO list

## Top priority

- test well these GUIs

- tune-zinf.py needs to release memory! With 298000 lines, it started to eat all memory

## Low priority

- run4.py + fileoptions + x.py tab3: move documentation ifnroamtion to inside fileoptions so that I can publish the descriptions of the parameters in `run4.py --help`

- x.py, tab 3: verify if files exist

- File .spec taking too long to open

- abed: Element Abundance (A(X)(ref)) (A(X)) [X/Fe]; A(X) is the current informationz
 
- new script to print filetypes as table

- mled.py: Set-of-lines deletion

- Throw new buttons in Abundances widget to expose export dissoc and export turbospectrum

- Rename TRAPRB exeutable to "traprb" instead of "fcf"

- convmol: sort redundancy in pfantmol description. MolConsts only
  populates properly if there is a pfantmol row with the "Formula [System]" in in its description

## Documentation

- Release notes: roughly what has been done since the beginning

### Specific examples

- synthesis: varying "pas"

# Future suggestions

- Introduce "notes" field for main.dat: could be sth like "<star name> # <notes>"
