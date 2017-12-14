import os
import pyfant


def test_FileAbXFwhm(tmpdir):
    os.chdir(str(tmpdir))
    obj = pyfant.FileAbXFwhm()
    obj.init_default()
    obj.save_as()


def test_FileAbonds(tmpdir):
    os.chdir(str(tmpdir))
    obj = pyfant.FileAbonds()
    obj.init_default()
    obj.save_as()


def test_FileDissoc(tmpdir):
    os.chdir(str(tmpdir))
    obj = pyfant.FileDissoc()
    obj.init_default()
    obj.save_as()


def test_FileHitranDB(tmpdir):
    os.chdir(str(tmpdir))
    obj = pyfant.FileHitranDB()
    obj.init_default()
    obj.save_as("another")


def test_FileHmap(tmpdir):
    os.chdir(str(tmpdir))
    obj = pyfant.FileHmap()
    obj.init_default()
    obj.save_as()


def test_FileMain(tmpdir):
    os.chdir(str(tmpdir))
    obj = pyfant.FileMain()
    obj.init_default()
    obj.save_as()


def test_FileMolDB(tmpdir):
    os.chdir(str(tmpdir))
    obj = pyfant.FileMolDB()
    obj.init_default()
    obj.save_as("another")


def test_FileOptions(tmpdir):
    os.chdir(str(tmpdir))
    obj = pyfant.FileOptions()
    obj.init_default()
    obj.save_as()

