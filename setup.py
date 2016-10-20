#!/usr/bin/env python3

from setuptools import setup, find_packages
from glob import glob

setup(
    name = 'pyfant',
    packages = find_packages(),
    version = '0.16.10.13',
    license = 'GNU GPLv3',
    platforms = 'any',
    description = 'Tools for Astronomy: Spectral Synthesis; Spectrograph Simulation Support; FITS files editors; and more.\n(1) Python interface for the PFANT spectral synthesis software (github.com/trevisanj/PFANT);\n (2) Support tools for Websim-Compass MOSAIC-E-ELT web-based simulator',
    author = 'Julio Trevisan',
    author_email = 'juliotrevisan@gmail.com',
    url = 'https://github.com/trevisanj/pyfant', # use the URL to the github repo
    keywords= ['astronomy', 'spectral synthesis', 'e-elt', 'mosaic', 'stars', 'websim-compass', 'simulator', 'learning astronomy'],
    install_requires = ['numpy', 'scipy', 'astropy', 'matplotlib', 'fortranformat'],  # matplotlib never gets installed correctly by pip, but anyway...
    scripts = glob('scripts/*.py')  # Considers system scripts all .py files in 'scripts' directory
)

