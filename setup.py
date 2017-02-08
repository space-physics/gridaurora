#!/usr/bin/env python
from setuptools import setup

try:
    import conda.cli
    conda.cli.main('install','--file','requirements.txt')
except Exception as e:
    print(e)
    import pip
    pip.main(['install','-r','requirements.txt'])


setup(name='gridaurora',
      packages=['gridaurora'],
      author='Michael Hirsch, Ph.D.',
      url='https://github.com/scienceopen/gridaurora',
      data_files=[('gridaurora/data',['gridaurora/data/RecentIndices.txt'])],
	  install_requires=['sciencedates','pathvalidate'],
      extras_require={'lowtran':'lowtran'}, #optional
      dependency_links = [
      'https://github.com/scienceopen/lowtran/tarball/master#egg=lowtran',],
      package_data={'gridaurora.precompute': ['*.h5']},
	  )

