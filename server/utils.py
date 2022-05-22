import hashlib
import os.path
import signal

def get_working_dir():
    pass

def get_hash(file: str) -> str:
    data = ""
    with open(file, 'rb') as f:
        data = f.read()
    return hashlib.sha1(data).hexdigest()

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)