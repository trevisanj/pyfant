import os
import pyfant


def test_FileModTXT():
    f = pyfant.FileModTxt()
    f.load("sun.mod")


def test_FileOpa(tmpdir):
    f = pyfant.FileOpa()
    f.load("sun.opa")
