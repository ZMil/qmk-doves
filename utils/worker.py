from PyQt6.QtCore import QRunnable, QObject, pyqtSignal

class WorkerSignals(QObject):
    '''
    pyqtSignal can be overwritten to return other types
    '''
    result = pyqtSignal(str)

class Worker(QRunnable):
    def __init__(self, signals, func):
        super(Worker, self).__init__()
        self.signals = signals
        self.func = func
    
    def run(self):
        result = self._run()
        self.signals.result.emit(result)
    
    def _run(self):
        '''
        empty function where user should put code to execute
        '''
        pass