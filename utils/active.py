from win32gui import GetForegroundWindow
from win32process import GetWindowThreadProcessId
from psutil import Process

def qmkactive():
    active = GetForegroundWindow()
    _, pid = GetWindowThreadProcessId(active)
    try:
        name = Process(pid).name()
        return(name)
    except:
        pass
