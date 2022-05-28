import os
import socket
import pickle
import urllib.parse
import pdb
import zipfile
import tempfile
from typing import TYPE_CHECKING, Tuple, Dict, List

from tqdm import tqdm

from client.repo import Repo
from client.update import Update
from client.storage import storage
from client.stage import Stage
from core import directory, utils
from core.types import VersionID
if TYPE_CHECKING:
    from client.version import Version


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
    network communication protocol
        1. send 'push'
        2. send branch name
        3. send uri
        4. wait for authentication message (an encrypted random number)
        5. send the decrypted random number
        6. send version list from init to the branch
        7. wait the server's response for required version
        8. send file list of required versions
        9. wait the server's response for required file
        10. send program list of required versions
        11. send full contents of all files
        12. send struct for all versions
        13. send all required programs
    """
    s.connect(addr)
    f = s.makefile("rwb")

    # 1. 2. 3.
    f.write("push\n".encode('utf-8'))
    f.write(f"{branch}\n".encode('utf-8'))
    f.write(f"{uri}\n".encode('utf-8'))
    f.flush()

#     # 4. 5.
#     ciphertext = pickle.load(f)
#     private_key = storage.load_private_key()
#     msg = utils.decrypt(ciphertext, private_key)
#     f.write(msg)
#     f.flush()

    pdb.set_trace()
    # 6. 7.
    vs = repo.get_version_list(
        repo.get_init_version_id(), repo.branch_map[branch])
    pickle.dump(vs, f)
    f.flush()
    required_version: List[VersionID] = pickle.load(f)
    required_version = list(map(lambda v: repo.version_map[v], required_version))

    # 8. 9.
    flist = []
    for v in required_version:
        flist.extend(v.get_hash_list())
    pickle.dump(flist, f)
    f.flush()
    required_files: List[str] = pickle.load(f)

    # 10.
    plist = []
    for v in required_version:
        plist.extend(v.get_program_list())
    pickle.dump(plist, f)
    f.flush()

    # 11.
    wd = utils.get_working_dir()
    for file_hash in tqdm(required_files, desc="Uploading Files"):
        filename = storage.get_file(file_hash)
        filename = os.path.join(wd, filename)
        with open(filename, "rb") as g:
            c = g.read()
            pickle.dump(c, f)
    f.flush()
    
    # 12.
    for v in required_version:
        pickle.dump(v.to_dict(), f)
    f.flush()

    # 13.
    with tempfile.TemporaryDirectory() as tmp_dir:
        for p in plist:
            program_dir = os.path.join(wd, storage.get_transform(p))
            tmpzip = os.path.join(tmp_dir, 'tmp.zip')
            utils.get_zip(program_dir, tmpzip) # TODO
            with open(tmpzip, 'rb') as prog_file:
                content = prog_file.read()
                pickle.dump(content, f)

def clone(url: str):
    working_dir = os.getcwd()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addr = parse_addr(url)
    uri = parse_uri(url)

    s.connect(addr)
    f = s.makefile("rwb")
    f.write("clone\n".encode('utf-8'))
    f.write(f"{uri}\n".encode('utf-8'))
    f.flush()           

    repo_name = f.readline().decode('utf-8').strip()
    if os.path.exists(os.path.join(working_dir, repo_name)):
        f.write("repo_exist\n".encode('utf-8'))
    else:
        f.write("OK\n".encode('utf-8'))

    f.flush()
    # recieve .datagit/repo
    print('recieve_repo')
    if os.path.exists(os.path.join(working_dir, repo_name)):
        raise ValueError('Directory already exist.')
    else:
        os.makedirs(repo_name)
    os.chdir(os.path.join(working_dir, repo_name))

    repo = Repo()
    repo.init()

    stage = Stage()
    storage.save_stage(stage)
    working_dir = os.path.join(working_dir, repo_name, '.datagit')
    repo.load_from_dict( pickle.load(f) )
    storage.save_repo(repo)
    
    # recieve .datagit/programs
    print('recieve_programs')
    with open(os.path.join(working_dir, 'tmp.zip'), 'wb') as prog_file:
        prog_file.write( pickle.load(f) )
    
    dst_dir = os.path.join(working_dir, 'programs')
    zf = zipfile.ZipFile(os.path.join(working_dir, 'tmp.zip'), 'r')
    for af in zf.namelist():
        zf.extract(af, dst_dir)
    zf.close()
    os.remove(os.path.join(working_dir, 'tmp.zip'))

    # recieve .datagit/data
    print('recieve_data')
    file_name_list = pickle.load(f)
    for file_name in tqdm(file_name_list, desc="Downloading Files"):
        with open(os.path.join(working_dir, 'data', file_name), 'wb') as afile:
            afile.write(pickle.load(f))
