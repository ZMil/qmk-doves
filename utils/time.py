from datetime import datetime
try:
    from utils import worker
except:
    pass

class TimeSignal(worker.WorkerSignals):
    pass

class TimeWorker(worker.Worker):
    def __init__(self, signals):   
        super(TimeWorker, self).__init__(signals, self._run)

    def _run(self):
        now = datetime.now().strftime("%H:%M")
        return(str(now))
