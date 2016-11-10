__all__ = ["get_QApplication", "_ThreadsafeTimer", "SignalProxy", "get_pyfant_icon"]


from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time
from threading import Lock
from .fileio import get_pyfant_path


def get_pyfant_icon(keyword):
    """
    Transforms a PNG file in a QIcon

    Looks for a file named <keyword>.png in the "icons" directory
    """

    filename = get_pyfant_path("data", "icons", keyword+".png")
    ret = QIcon(filename)
    return ret


# #################################################################################################
# # PyQt-related routines

_qapp = None
def get_QApplication(args=[]):
    """Returns the QApplication instance, creating it is does not yet exist."""
    global _qapp
    if _qapp is None:
        _qapp = QApplication(args)
    return _qapp


class _ThreadsafeTimer(QObject):
    """
    Thread-safe replacement for QTimer.

    Original author: Luke Campagnola -- pyqtgraph package
    """

    timeout = pyqtSignal()
    sigTimerStopRequested = pyqtSignal()
    sigTimerStartRequested = pyqtSignal(object)

    def __init__(self):
        QObject.__init__(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timerFinished)
        self.timer.moveToThread(QCoreApplication.instance().thread())
        self.moveToThread(QCoreApplication.instance().thread())
        self.sigTimerStopRequested.connect(self.stop, Qt.QueuedConnection)
        self.sigTimerStartRequested.connect(self.start, Qt.QueuedConnection)


    def start(self, timeout):
        isGuiThread = QThread.currentThread() == QCoreApplication.instance().thread()
        if isGuiThread:
            #print "start timer", self, "from gui thread"
            self.timer.start(timeout)
        else:
            #print "start timer", self, "from remote thread"
            self.sigTimerStartRequested.emit(timeout)

    def stop(self):
        isGuiThread = QThread.currentThread() == QCoreApplication.instance().thread()
        if isGuiThread:
            #print "stop timer", self, "from gui thread"
            self.timer.stop()
        else:
            #print "stop timer", self, "from remote thread"
            self.sigTimerStopRequested.emit()

    def timerFinished(self):
        self.timeout.emit()


class SignalProxy(QObject):
    """Object which collects rapid-fire signals and condenses them
    into a single signal or a rate-limited stream of signals.
    Used, for example, to prevent a SpinBox from generating multiple
    signals when the mouse wheel is rolled over it.

    Emits sigDelayed after input signals have stopped for a certain period of time.

    Note: *queued* connection is made to slot.

    Original author: Luke Campagnola -- pyqtgraph package

    Arguments:
      signals -- a list of bound signals or pyqtSignal instance
      delay=0.3 -- Time (in seconds) to wait for signals to stop before emitting
      slot -- Optional function to connect sigDelayed to.
      rateLimit=0 -- (signals/second) if greater than 0, this allows signals to
       stream out at a steady rate while they are being received.
      flag_connect=True -- whether or not to start with the connections already
       made. If False, the signals and slots can be connected by calling
       connect_all()
    """

    __sigDelayed = pyqtSignal(object)

    def __init__(self, signals, delay=0.3, rateLimit=0, slot=None,
                 flag_connect=True):
        QObject.__init__(self)
        # for signal in signals:
        #     self.__connect_signal(signal)
        self.__signals = signals
        self.__delay = delay
        self.__rateLimit = rateLimit
        self.__args = None
        self.__timer = _ThreadsafeTimer()
        self.__timer.timeout.connect(self.__flush)
        self.__disconnecting = False
        self.__slot = slot
        self.__lastFlushTime = None
        self.__lock = Lock()
        # State: connected/disconnected
        self.__connected = False
        if flag_connect:
            self.connect_all()
        # if slot is not None:
        #     self.__sigDelayed.connect(slot, Qt.QueuedConnection)

    def add_signal(self, signal):
        """Adds "input" signal to connected signals.
        Internally connects the signal to a control slot."""
        self.__signals.append(signal)
        if self.__connected:
            # Connects signal if the current state is "connected"
            self.__connect_signal(signal)

    def connect_all(self):
        """[Re-]connects all signals and slots.

        If already in "connected" state, ignores the call.
        """
        if self.__connected:
            return  # assert not self.__connected, "connect_all() already in \"connected\" state"
        with self.__lock:
            for signal in self.__signals:
                self.__connect_signal(signal)
            if self.__slot is not None:
                self.__sigDelayed.connect(self.__slot, Qt.QueuedConnection)
            self.__connected = True

    def disconnect_all(self):
        """Disconnects all signals and slots.

        If already in "disconnected" state, ignores the call.
        """
        if not self.__connected:
            return  # assert self.__connected, "disconnect_all() already in \"disconnected\" state"
        self.__disconnecting = True
        try:
            for signal in self.__signals:
                signal.disconnect(self.__signalReceived)
            if self.__slot is not None:
                self.__sigDelayed.disconnect(self.__slot)
            self.__connected = False
        finally:
            self.__disconnecting = False

    def __signalReceived(self, *args):
        """Received signal. Cancel previous timer and store args to be forwarded later."""
        if self.__disconnecting:
            return
        with self.__lock:
            self.__args = args
            if self.__rateLimit == 0:
                self.__timer.stop()
                self.__timer.start((self.__delay * 1000) + 1)
            else:
                now = time.time()
                if self.__lastFlushTime is None:
                    leakTime = 0
                else:
                    lastFlush = self.__lastFlushTime
                    leakTime = max(0, (lastFlush + (1.0 / self.__rateLimit)) - now)

                self.__timer.stop()
                # Note: original was min() below.
                timeout = (max(leakTime, self.__delay) * 1000) + 1
                self.__timer.start(timeout)

    def __flush(self):
        """If there is a signal queued up, send it now."""
        if self.__args is None or self.__disconnecting:
            return False
        #self.emit(self.signal, *self.args)
        self.__sigDelayed.emit(self.__args)
        self.__args = None
        self.__timer.stop()
        self.__lastFlushTime = time.time()
        return True

    def __connect_signal(self, signal):
        signal.connect(self.__signalReceived, Qt.QueuedConnection)
