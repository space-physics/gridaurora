[![image](https://zenodo.org/badge/36744963.svg)](https://zenodo.org/badge/latestdoi/36744963)
[![image](https://travis-ci.org/scivision/gridaurora.svg?branch=master)](https://travis-ci.org/scivision/gridaurora)
[![image](https://ci.appveyor.com/api/projects/status/2jjhaq3rqjrw77vg?svg=true)](https://ci.appveyor.com/project/scivision/gridaurora)
[![image](https://coveralls.io/repos/scivision/gridaurora/badge.svg?branch=master&service=github)](https://coveralls.io/github/scivision/gridaurora?branch=master)

# Grid for Auroral models

Discretizations of space (grids) and time conversions useful for aeronomy and auroral modeling.

## Install

    python -m pip install -e .

Note: you will need a Fortran compiler on your system for `f2py` modules.
It works on Linux, Mac, [Windows](https://scivision.co/f2py-running-fortran-code-in-python-on-windows/), etc.

## Eigenprofiles

Currently GLOW and Rees-Sergienko-Ivanov are available (Transcar in future). 
You can install these models with

```sh
pip install reesaurora

pip install glowaurora
```

Once installed, select model by:

* `-M rees`  Rees-Sergienko-Ivanov
* `-M glow`  Stan Solomon's GLOW model


### Command Line Options

-t time, format yyyy-mm-ddTHH:MM:SSZ where Z sets UTC time zone -c lat,
lon WGS84 geodetic degrees -o output, hDF5 ends in .h5 -M model select
(see table above) -z min,max altitude to plot [km]

### Example Command

    python MakeIonoEigenprofile.py -t 2013-01-31T09:00:00Z -c 65 -148 -o out.h5 -M rees

Auroral Data Files
------------------

The functions in `gridaurora/calcemissions.py`, based on work by
Zettergren, computes per-wavelength volume emission rate along a flux
tube as a function of altitude along the tube. Starting with quantities
such as neutral densities computed by MSIS, differential number flux as
a function of energy and altitude along the tube (this is what TRANSCAR
computes), excitation cross sections as a function of energy,
Franck-Condon factors and Einstein coefficients, the *prompt* volume
emission rate may be computed.

### precompute/vjeinfc.h5

This file is compiled from tables in Vallance Jones *Aurora* 1974 and other sources
by Matthew Zettergren, and corrected and put into HDF5 format by Michael Hirsch. 
The information within concerns:

* N2+1NG:   N~2~^+^ first negative group
* N2_1PG:   N~2~ first positive group
* N2_2PG:   N~2~ second positive group
* N2+Meinel:   N~2~^+^ Meinel band
* atomic:   atomic oxygen
* metastable:   metastable O and O^+^

#### Einstein coefficient matrix A

arranged A(𝜈',𝜈'') where:

* 𝜈' upper state vibrational levels, excited from ground state 𝜈''' by particle impact
* 𝜈'' lower state vibrational levels, decayed into from the upper state

as discussed in Appendix C of Zettergren PhD thesis, Eqn. (C.2), photon
volume emission rate follows the relation P~𝜈',𝜈''~ = A(𝜈',𝜈'')
n~𝜈'~

#### lamdba

wavelength in nanometers corresponding to the Einstein coefficient
matrix `A` except `atomic` that uses the reaction rates directly.

#### Franck-Condon factor fc

as described in Zettergren thesis Appendix C, specifically for Eqn
(C.6-C.8), the Franck-Condon factors modify the total upper state
excitation cross section multiplicitively.

## Function Description

function  | description
----------|----------------------------------------------------------------------------------------------------------------
ztanh.py  | continuously varying grid using hyperbolic tangent. Inspired by suggestion from Prof. Matt Zettergren of ERAU.


