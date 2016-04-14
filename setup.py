#!/usr/bin/env python3
import os,sys
from setuptools import setup
import subprocess

exepath = os.path.dirname(sys.executable)
try:
    subprocess.call([os.path.join(exepath,'conda'),'install','--yes','--file','requirements.txt'])
except Exception as e:
    print('tried conda in {}, but you will need to install packages in requirements.txt  {}'.format(exepath,e))


with open('README.rst','r') as f:
	long_description = f.read()

setup(name='gridaurora',
      version='0.1.1',
	  description='utilities for ionospheric gridding, particularly for the aurora',
	  long_description=long_description,
	  author='Michael Hirsch',
	  url='https://github.com/scienceopen/gridaurora',
    data_files=[('gridaurora/data',['gridaurora/data/RecentIndices.txt'])],
	  install_requires=['histutils'],
   extras_require={'lowtran':'lowtran'}, #optional
   dependency_links = ['https://github.com/scienceopen/lowtran/tarball/master#egg=lowtran',
                     'https://github.com/scienceopen/histutils/tarball/master#egg=histutils'],
   packages=['gridaurora'],
   package_data={'gridaurora.precompute': ['*.h5']},
	  )
