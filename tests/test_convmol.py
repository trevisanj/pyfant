import pyfant as pf
import hypydrive as hpd



def test_MolConversionLog():
    app = hpd.get_QApplication()
    w = pf.convmol.MolConversionLog()


def test_WDBRegistry():
    app = hpd.get_QApplication()
    w = pf.convmol.WDBRegistry(hpd.XLogMainWindow())


def test_WDBState():
    app = hpd.get_QApplication()
    w = pf.convmol.WDBState(hpd.XLogMainWindow())


# def test_WMolConst():
#     app = hpd.get_QApplication()
#     w = pf.convmol.WMolConst(hpd.XLogMainWindow())
#
#
# def test_WStateConst():
#     app = hpd.get_QApplication()
#     w = pf.convmol.WStateConst(hpd.XLogMainWindow())


def test_XConvMol():
    app = hpd.get_QApplication()
    w = pf.convmol.XConvMol()


def test_XFileMolDB():
    app = hpd.get_QApplication()
    w = pf.convmol.XFileMolDB()

