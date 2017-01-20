import pyfant as pf
import hypydrive as hpd


def test_WFileAbXFwhm():
    app = hpd.get_QApplication()
    w = pf.WFileAbXFwhm()


def test_WFileAbonds():
    app = hpd.get_QApplication()
    w = pf.WFileAbonds()


def test_WFileMain():
    app = hpd.get_QApplication()
    w = pf.WFileMain()


def test_WOptionsEditor():
    app = hpd.get_QApplication()
    w = pf.WOptionsEditor()



def test_XFileAbonds():
    app = hpd.get_QApplication()
    w = pf.XFileAbonds()


def test_XFileAtoms():
    app = hpd.get_QApplication()
    w = pf.XFileAtoms()


def test_XFileMain():
    app = hpd.get_QApplication()
    w = pf.XFileMain()


def test_XFileMolecules():
    app = hpd.get_QApplication()
    w = pf.XFileMolecules()


def test_XMainAbonds():
    app = hpd.get_QApplication()
    w = pf.XMainAbonds()


def test_XMulti():
    app = hpd.get_QApplication()
    w = pf.XMulti()


def test_XPFANT():
    app = hpd.get_QApplication()
    w = pf.XPFANT()


def test_XRunnableManager():
    app = hpd.get_QApplication()
    rm = pf.RunnableManager()
    w = pf.XRunnableManager(None, rm)


def test_XMolLinesEditor():
    app = hpd.get_QApplication()
    w = pf.XMolLinesEditor(None)


def test_XFileAtomsHistogram():
    app = hpd.get_QApplication()
    w = pf.XFileAtomsHistogram(None)

def test_XAtomLinesEditor():
    app = hpd.get_QApplication()
    w = pf.XAtomLinesEditor(None)

