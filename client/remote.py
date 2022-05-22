from typing import TYPE_CHECKING, Tuple, Dict
import storage
import socket
import pickle
import urllib.parse
if TYPE_CHECKING:
    from repo import Repo
import pdb

def remote_add(url:str) -> None:
    '''
    将当前仓库与一个远程仓库绑定(可覆盖绑定仓库)
    push的仓库为已绑定仓库
    '''
    storage.save_remote(url)

def parse_addr(url: str) -> Tuple[str, int]:
    target = urllib.parse.urlparse(url)
    hp = target.netloc.split(':')
    assert len(hp) == 1 or len(hp) == 2
    if len(hp) == 2:
        hostname, port = hp
    else:
        hostname, port = hp[0], '9999'
    return (hostname, int(port))

def parse_uri(url: str) -> str:
    target = urllib.parse.urlparse(url)
    return target.path
    

def push(repo: 'Repo', branch: str, url: str) -> None:
    """
    push a branch to the remote repository
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = parse_addr(url)
    uri = parse_uri(url)
    
    """
    start network communication
        1. 'push'
        2. branch name
        3. uri
    """
    import pdb
    pdb.set_trace()
    s.connect(addr)
    f = s.makefile("rwb")
    f.write("push\n".encode('utf-8'))
    f.write(f"{branch}\n".encode('utf-8'))
    f.write(f"{uri}\n".encode('utf-8'))
    vs = repo.get_version_list(branch)
    pickle.dump(vs, f)
    f.flush()
    dlist = pickle.load(f)
