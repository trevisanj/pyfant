import pyfant
import a99


def test_MolConversionLog():
    app = a99.get_QApplication()
    w = pyfant.MolConversionLog()


def test_WDBRegistry():
    app = a99.get_QApplication()
    w = a99.WDBRegistry(a99.XLogMainWindow())


def test_WMolecularConstants():
    app = a99.get_QApplication()
    w = pyfant.WMolecularConstants(a99.XLogMainWindow())


# def test_XConvMol():
#     app = a99.get_QApplication()
#     w = pyfant.XConvMol()


def test_XFileMolDB():
    app = a99.get_QApplication()
    w = pyfant.XFileMolDB()

