import pyfant as pf
import astrogear as ag



def test_MolConversionLog():
    app = ag.get_QApplication()
    w = pf.convmol.MolConversionLog()


def test_WDBRegistry():
    app = ag.get_QApplication()
    w = pf.convmol.WDBRegistry(ag.XLogMainWindow())


def test_WDBState():
    app = ag.get_QApplication()
    w = pf.convmol.WDBState(ag.XLogMainWindow())


# def test_WMolConst():
#     app = ag.get_QApplication()
#     w = pf.convmol.WMolConst(ag.XLogMainWindow())
#
#
# def test_WStateConst():
#     app = ag.get_QApplication()
#     w = pf.convmol.WStateConst(ag.XLogMainWindow())


def test_XConvMol():
    app = ag.get_QApplication()
    w = pf.convmol.XConvMol()


def test_XFileMolDB():
    app = ag.get_QApplication()
    w = pf.convmol.XFileMolDB()

