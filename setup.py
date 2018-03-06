import sys
import os

if sys.version_info[0] < 3:
    print("Python version detected:\n*****\n{0!s}\n*****\nCannot run, must be using Python 3".format(sys.version))
    sys.exit()

from setuptools import setup, find_packages
from glob import glob


def find_scripts(pkgnames):
    ret = []
    for pkgname in pkgnames:
        for item in os.walk(pkgname):
            _, last = os.path.split(item[0])
            if last == "scripts":
                ret.extend(glob(os.path.join(item[0], '*.py')))
    return ret


PACKAGE_NAME = "pyfant"

pkgs = find_packages()
scripts = find_scripts([PACKAGE_NAME])

setup(
    name=PACKAGE_NAME,
    packages=find_packages(),
    include_package_data=True,
    version='18.3.6.0',
    license='GNU GPLv3',
    platforms='any',
    description='Python interface to the PFANT spectral synthesis code, with a varied set of extra tools',
    author='Julio Trevisan',
    author_email='juliotrevisan@gmail.com',
    url='https://github.com/trevisanj/pyfant',
    keywords= ['astronomy', "stellar", "spectroscopy", "spectral", "synthesis",
               "honl-london", "nist", "hitran", "multiplicity", "line strength", "kovacs", "franck-condon"],
    install_requires=["numpy", "scipy", "matplotlib", "astropy", "configobj", "bs4", "lxml",
                      "robobrowser", "requests", "fortranformat", "tabulate", "rows", "pyqt5",
                      "f311>=18.3.1.0", "airvacuumvald"],
    scripts=scripts
)


# TODO later install_requires=['numpy', 'matplotlib', 'pyqt5'],  # matplotlib never gets installed correctly by pip, but anyway...
