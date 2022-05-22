from typing import TYPE_CHECKING
import storage
import socket
import urllib.parse
from multiprocessing import Process 
import os
import pathlib
if TYPE_CHECKING:
    from repo import Repo

def push(branch: str, uri: str) -> None:
    l = uri.strip('/').split('/')
    assert len(l) == 1
    repo_name = l[0]
    repo = storage.get_repo(repo_name)

def main() -> None:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.listen()
    while True:
        conn, address = s.accept()
        print(f"Client {address} connected, serving")
        conn.makefile()
        Process(target=push, args=[], daemon=True).start()


if __name__ == '__main__':
    main()
