from typing import TYPE_CHECKING
import storage
import urllib.parse
from multiprocessing import Process 
import socketserver
import pickle
import os
import pathlib
import controller
if TYPE_CHECKING:
    from repo import Repo

server_addr = ("localhost", 8887)

class Handler(socketserver.StreamRequestHandler):
    def push(self) -> None:
        import pdb
        pdb.set_trace()
        branch = self.rfile.readline().decode("utf-8").strip()
        uri = self.rfile.readline().decode("utf-8").strip()
        l = uri.strip('/').split('/')
        assert len(l) == 1
        repo_name = l[0]
        version_list = pickle.load(self.rfile)
        
        dlist = controller.diff_version(repo_name, version_list)
        pickle.dump(dlist, self.wfile)
        self.wfile.flush()

    def get(self) -> None:
        pass

    def clone(self) -> None:
        pass

    def handle(self):
        command = self.rfile.readline().decode("utf-8").strip()
        if command == "push":
            self.push()
        elif command == "get":
            pass
        elif command == "clone":
            pass
        else:
            print(f"{command}: Command Not Exists!")

def main() -> None:
    with socketserver.TCPServer(server_addr, Handler) as s:
        s.serve_forever()

if __name__ == '__main__':
    main()
