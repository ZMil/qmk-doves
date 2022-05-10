import os
from utils.qmkhid import QMKDevice
if os.name == 'nt':
    # If windows
    from utils.active import *
from utils.time import *
from utils import worker
from utils.weather import *