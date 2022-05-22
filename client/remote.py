from typing import TYPE_CHECKING
import storage
import socket
import urllib.parse
if TYPE_CHECKING:
    from repo import Repo

def push(repo: Repo, branch: str, url: str) -> None:
    vs = repo.get_version_list(branch)
    target = urllib.parse.urlparse(url)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

