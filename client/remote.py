from storage import storage
from typing import TYPE_CHECKING
import socket
import urllib.parse
if TYPE_CHECKING:
    from repo import Repo

def remote_add(url:str) -> None:
    '''
    将当前仓库与一个远程仓库绑定(可覆盖绑定仓库)
    push的仓库为已绑定仓库
    '''
    storage.save_remote(url)

def push(repo: Repo, branch: str, url: str) -> None:
    vs = repo.get_version_list(branch)
    target = urllib.parse.urlparse(url)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

