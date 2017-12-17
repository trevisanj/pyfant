import os
import pyfant

# Solution to find data files:
# https://stackoverflow.com/questions/29627341/pytest-where-to-store-expected-data

def test_FileModTXT(request):
    dir_with_file = os.path.split(request.module.__file__)[0]
    f = pyfant.FileModTxt()
    f.load(os.path.join(dir_with_file, "sun.mod"))


def test_FileOpa(request):
    dir_with_file = os.path.split(request.module.__file__)[0]
    f = pyfant.FileOpa()
    f.load(os.path.join(dir_with_file, "sun.opa"))
