import pyfant as pf
import astrogear as ag


def test_WFileAbXFwhm():
    app = ag.get_QApplication()
    w = pf.WFileAbXFwhm()


def test_WFileAbonds():
    app = ag.get_QApplication()
    w = pf.WFileAbonds()


def test_WFileMain():
    app = ag.get_QApplication()
    w = pf.WFileMain()


def test_WOptionsEditor():
    app = ag.get_QApplication()
    w = pf.WOptionsEditor()



def test_XFileAbonds():
    app = ag.get_QApplication()
    w = pf.XFileAbonds()


def test_XFileAtoms():
    app = ag.get_QApplication()
    w = pf.XFileAtoms()


def test_XFileMain():
    app = ag.get_QApplication()
    w = pf.XFileMain()


def test_XFileMolecules():
    app = ag.get_QApplication()
    w = pf.XFileMolecules()


def test_XMainAbonds():
    app = ag.get_QApplication()
    w = pf.XMainAbonds()


def test_XMulti():
    app = ag.get_QApplication()
    w = pf.XMulti()


def test_XPFANT():
    app = ag.get_QApplication()
    w = pf.XPFANT()


def test_XRunnableManager():
    app = ag.get_QApplication()
    rm = pf.RunnableManager()
    w = pf.XRunnableManager(None, rm)


def test_XMolLinesEditor():
    app = ag.get_QApplication()
    w = pf.XMolLinesEditor(None)


def test_XFileAtomsHistogram():
    app = ag.get_QApplication()
    w = pf.XFileAtomsHistogram(None)

def test_XAtomLinesEditor():
    app = ag.get_QApplication()
    w = pf.XAtomLinesEditor(None)

