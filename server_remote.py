import os
import pathlib
import pickle
import socketserver
import urllib.parse
from multiprocessing import Process 
from typing import TYPE_CHECKING, Dict

from server import controller
from server.version import Version
from server.storage import storage
if TYPE_CHECKING:
    from server.repo import Repo

server_addr = ("localhost", 8887)

class Handler(socketserver.StreamRequestHandler):
    def push(self) -> None:
        branch = self.rfile.readline().decode("utf-8").strip()
        uri = self.rfile.readline().decode("utf-8").strip()
        l = uri.strip('/').split('/')
        assert len(l) == 1
        repo_name = l[0]
        
        version_list = pickle.load(self.rfile)
        vlist = controller.diff_version(repo_name, version_list)
        pickle.dump(vlist, self.wfile)
        self.wfile.flush()

        file_list = pickle.load(self.rfile)
        flist = controller.diff_files(file_list)
        pickle.dump(flist, self.wfile)
        self.wfile.flush()

        for f in flist:
            content = pickle.load(self.rfile)
            storage.save_file(f, content)
        
        for f in vlist:
            _version: Dict = pickle.load(self.rfile)
            version = Version(None, None, None, None)
            version.load_from_dict(_version)
            controller.add_version(repo_name, version)

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
