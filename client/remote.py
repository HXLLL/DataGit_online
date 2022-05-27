import os
import socket
import pickle
import urllib.parse
import pdb
import os
import zipfile
from typing import TYPE_CHECKING, Tuple, Dict, List

from client.update import Update
from client.storage import storage
from core import utils
if TYPE_CHECKING:
    from repo import Repo
    from version import Version


def remote_add(url:str) -> None:
    '''
    将当前仓库与一个远程仓库绑定(可覆盖绑定仓库)
    push的仓库为已绑定仓库
    '''
    storage.save_remote(url)


def parse_addr(url: str) -> Tuple[str, int]:
    '''
    get a socket address pair from a url
    '''
    target = urllib.parse.urlparse(url)
    hp = target.netloc.split(':')
    assert len(hp) == 1 or len(hp) == 2
    if len(hp) == 2:
        hostname, port = hp
    else:
        hostname, port = hp[0], '9999'
    return (hostname, int(port))

def parse_uri(url: str) -> str:
    '''
    get uri from a url
    '''
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
        4. version list from init to the branch
        5. wait the server's response required version
        6. send all files of required version
        7. wait the server's response required file
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
    required_version: List['Version'] = pickle.load(f)

    flist = []
    for v in required_version:
        flist.extend(v.get_hash_list())
    pickle.dump(flist, f)
    f.flush()
    required_files: List[str] = pickle.load(f)

    wd = utils.get_working_dir()
    for file_hash in required_files:
        filename = storage.get_file(file_hash)
        filename = os.path.join(wd, filename)
        with open(filename, "rb") as g:
            c = g.read()
            pickle.dump(c, f)
    f.flush()
    
    for v in required_version:
        pickle.dump(v.to_dict(), f)
    f.flush()

def clone(url: str):
    working_dir = os.getcwd()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = parse_addr(url)
    uri = parse_uri(url)

    import pdb
    pdb.set_trace()
    s.connect(addr)
    f = s.makefile("rwb")
    f.write("clone\n".encode('utf-8'))
    f.write(f"{uri}\n".encode('utf-8'))
    f.flush()           

    repo_name = f.readline()
    if os.path.exists(os.path.join(working_dir, repo_name)):
        f.write("repo_exist\n".encode('utf-8'))
    else:
        f.write("OK\n".encode('utf-8'))

    # recieve .datagit/repo
    os.makedir(repo_name)
    os.chdir(os.path.join(working_dir, repo_name))
    repo = storage.load_repo()
    working_dir = os.path.join(working_dir, repo_name, '.datagit')
    repo.load_from_dict( pickle.load(f) )
    storage.save_repo()
    
    # recieve .datagit/programs
    with open(os.path.join(working_dir, 'tmp.zip'), 'wb') as prog_file:
        prog_file.write( pickle.load(f) )
    
    dst_dir = os.path.join(working_dir, 'programs')
    zf = zipfile.ZipFile(os.path.join(working_dir, 'tmp.zip'), 'r')
    for f in zf.namelist():
        zf.extract(f, dst_dir)
    zf.close()
    os.remove(os.path.join(working_dir, 'tmp.zip'))

    # recieve .datagit/data
    file_name_list = pickle.load(f)
    for file_name in file_name_list:
        with open(os.path.join(working_dir, 'data', file_name), 'wb') as afile:
            afile.write(pickle.load(f))

    
