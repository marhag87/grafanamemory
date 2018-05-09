import psutil
from pyyamlconfig import load_config
import socket
import time
import graphyte
import sys

hostname = socket.gethostname()
config = load_config('config.yaml')
if config is None:
    sys.exit('Config is empty, please supply a whitelist')

whitelist = config.get('whitelist')
if whitelist is None or whitelist == []:
    sys.exit('Whitelist is empty, exiting')

carbon = config.get('carbon', {})
graphyte.init(
    carbon.get('hostname', 'localhost'),
    prefix=f'gm.{hostname}',
)


def get_memory():
    """Get a per process summary of all memory used by all processes in the whitelist"""
    procs = {}
    for program, rss in [(x.name(), x.memory_info().rss) for x in psutil.process_iter() if x.name() in whitelist]:
        if program in procs:
            procs[program] += rss
        else:
            procs[program] = rss
    return procs


while True:
    """Send date to grafite every X seconds"""
    for name, memory in get_memory().items():
        graphyte.send(name, memory)
    time.sleep(5)
