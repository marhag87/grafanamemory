import psutil
from pyyamlconfig import load_config
import socket
import time
import graphyte

hostname = socket.gethostname()
config = load_config('config.yaml')
whitelist = config.get('whitelist')
carbon = config.get('carbon', {})
graphyte.init(
    carbon.get('hostname', 'localhost'),
    prefix=f'gm.{hostname}',
)


def get_memory():
    """Get a per process summary of all memory used by all processes in the whitelist"""
    procs = {}
    for program in [x for x in psutil.process_iter() if x.name() in whitelist]:
        if program.name() in procs:
            procs[program.name()] += program.memory_info().rss
        else:
            procs[program.name()] = program.memory_info().rss
    return procs


while True:
    """Send date to grafite every X seconds"""
    memory = get_memory()
    for name in memory.keys():
        graphyte.send(name, memory[name])
    time.sleep(5)
