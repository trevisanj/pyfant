import sys
if sys.version_info[0] < 3:
    print("Python version detected:\n*****\n%s\n*****\nCannot run, must be using Python 3" % sys.version)
    sys.exit()

from setuptools import setup, find_packages
from glob import glob

setup(
    name = 'pyfant',
    packages = find_packages(),
    version = '0.16.12.19',
    license = 'GNU GPLv3',
    platforms = 'any',
    description = 'Python API and Graphical applications for PFANT (github.com/trevisanj/PFANT) Spectral Synthesis Software',
    author = 'Julio Trevisan',
    author_email = 'juliotrevisan@gmail.com',
    url = 'https://github.com/trevisanj/pyfant', # use the URL to the github repo
    keywords= ['astronomy', 'spectral synthesis'],
    install_requires = ['numpy', 'scipy', 'astropy', 'matplotlib', 'fortranformat', 'bs4', 'robobrowser',
                        'tabulate', 'astroapi==0.16.12.19'],  # matplotlib never gets installed correctly by pip, but anyway...
    scripts = glob('scripts/*.py')  # Considers system scripts all .py files in 'scripts' directory
)

