import pyfant
import a99


def test_XMulti():
    app = a99.get_QApplication()
    w = pyfant.XMulti()


def test_XPFANT():
    app = a99.get_QApplication()
    w = pyfant.XPFANT()


def test_XRunnableManager():
    app = a99.get_QApplication()
    rm = pyfant.RunnableManager()
    w = pyfant.XRunnableManager(None, rm)

