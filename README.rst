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

Eigenprofiles
=============
Currently GLOW and Rees-Sergienko-Ivanov are available (Transcar in future).
You will need to separately install scienceopen/reesaurora and scienceopen/glowaurora 
This is too keep the install process from becoming gigantic when you just want some of the models.

Once installed, select model by:

=========  ==========
-M option  Model used
=========  ==========
-M rees     Rees-Sergienko-Ivanov
-M glow    Stan Solomon's GLOW model
=========  ==========


========        ===========
function        description
========        ===========
ztanh.py        continuously varying grid using hyperbolic tangent. Inspired by suggestion from Prof. Matt Zettergren of ERAU.
========        ===========
