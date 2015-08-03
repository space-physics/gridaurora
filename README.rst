.. image:: https://travis-ci.org/scienceopen/gridaurora.svg?branch=master
    :target: https://travis-ci.org/scienceopen/gridaurora 
.. image:: https://codeclimate.com/github/scienceopen/gridaurora/badges/gpa.svg
   :target: https://codeclimate.com/github/scienceopen/gridaurora
   :alt: Code Climate
.. image:: https://coveralls.io/repos/scienceopen/gridaurora/badge.svg?branch=master&service=github 
    :target: https://coveralls.io/github/scienceopen/gridaurora?branch=master

==========
gridaurora
==========
Discretizations of space (grids) and time conversions useful for aeronomy and auroral modeling

Install
=======
from Terminal::
	
    git clone --depth 1 https://github.com/scienceopen/gridaurora
    conda install --file requirements.txt
    python setup.py install

Note: you will need a Fortran compiler on your system so that f2py can 
work. Yes, it's `possible on Windows too 
<https://scivision.co/f2py-running-fortran-code-in-python-on-windows/>`_ 
.


========        ===========
function        description
========        ===========
ztanh.py        continuously varying grid using hyperbolic tangent. Inspired by suggestion from Prof. Matt Zettergren of ERAU.
fortrandates.py utility conversions between oddball date formats used by classical aeronomy programs in FORTRAN to Python datetime
========        ===========
