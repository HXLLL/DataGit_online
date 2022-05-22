import hashlib
import os.path
import signal


def get_working_dir() -> str:
    """
    get working directory's root
    return -- absolute dir of working dir's root
    """

    if hasattr(get_working_dir, 'cache'):
        return get_working_dir.cache

    d = os.getcwd()
    while os.path.dirname(d) != d:
        if os.path.isdir(os.path.join(d, ".datagit")):
            break
        d = os.path.dirname(d)

    if os.path.dirname(d) != d:
        get_working_dir.cache = d
        return d
    else:
        return None


def get_hash(file: str) -> str:
    data = ""
    with open(file, 'rb') as f:
        data = f.read()
    return hashlib.sha1(data).hexdigest()


def in_working_dir(dir: str) -> bool:
    working_dir = get_working_dir()
    working_dir = os.path.abspath(working_dir)
    dir = os.path.abspath(dir)
    if len(working_dir) > len(dir):
        return False
    dir = dir[:len(working_dir)]
    if dir != working_dir:
        return False
    return True


def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)