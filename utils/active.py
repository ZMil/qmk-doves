from utils import worker
from win32gui import GetForegroundWindow
from win32process import GetWindowThreadProcessId
from psutil import Process


class QMKActiveSignal(worker.WorkerSignals):
    pass

class QMKActiveWorker(worker.Worker):
    def __init__(self, signals):   
        super(QMKActiveWorker, self).__init__(signals, self._run)


    def _run(self):
        active = GetForegroundWindow()
        _, pid = GetWindowThreadProcessId(active)
        try:
            name = Process(pid).name()
            return(name)
        except:
            pass