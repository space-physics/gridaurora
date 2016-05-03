.. image:: https://codeclimate.com/github/scienceopen/gridaurora/badges/gpa.svg
   :target: https://codeclimate.com/github/scienceopen/gridaurora
   :alt: Code Climate

.. image:: https://travis-ci.org/scienceopen/gridaurora.svg?branch=master
    :target: https://travis-ci.org/scienceopen/gridaurora

.. image:: https://coveralls.io/repos/scienceopen/gridaurora/badge.svg?branch=master&service=github 
   :target: https://coveralls.io/github/scienceopen/gridaurora?branch=master 

==========
gridaurora
==========
Discretizations of space (grids) and time conversions useful for aeronomy and auroral modeling.

.. contents::

Prereq
======
Python 3.5+
Fortran compiler

Install
=======
from Terminal::

    git clone --depth 1 https://github.com/scienceopen/gridaurora
    conda install --file requirements.txt
    python setup.py install

Note: you will need a Fortran compiler on your system so that f2py can
work. Yes, it's `possible on Windows too.
<https://scivision.co/f2py-running-fortran-code-in-python-on-windows/>`_

Eigenprofiles
=============
Currently GLOW and Rees-Sergienko-Ivanov are available (Transcar in future).
You will need to separately install `scienceopen/reesaurora <https://github.com/scienceopen/reesaurora>`_ and 
`scienceopen/glowaurora <https://github.com/scienceopen/glowaurora>`_.
This is to keep the install process from becoming gigantic when you just want some of the models.

Once installed, select model by:

=========  ==========
-M option  Model used
=========  ==========
-M rees     Rees-Sergienko-Ivanov
-M glow    Stan Solomon's GLOW model
=========  ==========

Command Line Options
--------------------
-t      time, format yyyy-mm-ddTHH:MM:SSZ  where Z sets UTC time zone
-c      lat, lon WGS84 geodetic degrees
-o      output, hDF5  ends in .h5
-M      model select (see table above)
-z      min,max altitude to plot [km]


Example Command
---------------
::

    python MakeIonoEigenprofile.py -t 2013-01-31T09:00:00Z -c 65 -148 -o out.h5 -M rees

Auroral Data Files
==================
The functions in ``gridaurora/calcemissions.py``, based on work by Zettergren, computes per-wavelength volume emission rate along a flux tube as a function of altitude along the tube. 
Starting with quantities such as neutral densities computed by MSIS, differential number flux as a function of energy and altitude along the tube (this is what TRANSCAR computes), excitation cross sections as a function of energy, Franck-Condon factors and Einstein coefficients, the *prompt* volume emission rate may be computed.


precompute/vjeinfc.h5
--------------------- 
compiled from tables in Vallance Jones *Aurora* 1974 and other sources by Matthew Zettergren, and corrected and put into HDF5 format by Michael Hirsch. The information within concerns:

N2+1NG        
    N\ :sub:`2`\ :sup:`+` first negative group

N2_1PG         
    N\ :sub:`2` first positive group

N2_2PG         
    N\ :sub:`2` second positive group

N2+Meinel      
    N\ :sub:`2`\ :sup:`+` Meinel band

atomic        
    atomic oxygen

metastable     
    metastable O and O\ :sup:`+`


Einstein coefficient matrix A
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
arranged A(𝜈',𝜈'') where:

𝜈'      
    upper state vibrational levels, excited from ground state 𝜈''' by particle impact

𝜈''
    lower state vibrational levels, decayed into from the upper state

as discussed in Appendix C of Zettergren PhD thesis, Eqn. (C.2), photon volume emission rate follows the relation P\ :sub:`𝜈',𝜈''` = A(𝜈',𝜈'') n\ :sub:`𝜈'` 

lamdba
~~~~~~
wavelength in nanometers corresponding to the Einstein coefficient matrix ``A`` 
except ``atomic`` that uses the reaction rates directly.

Franck-Condon factor fc
~~~~~~~~~~~~~~~~~~~~~~~
as described in Zettergren thesis Appendix C, specifically for Eqn (C.6-C.8), the Franck-Condon factors
modify the total upper state excitation cross section multiplicitively.

Function Description
====================


========        ===========
function        description
========        ===========
ztanh.py        continuously varying grid using hyperbolic tangent. Inspired by suggestion from Prof. Matt Zettergren of ERAU.
========        ===========

References
==========

.. [1] Zettergren, M. Boston University, PhD Thesis, `http://search.proquest.com/docview/304847517 <http://search.proquest.com/docview/304847517>`_
