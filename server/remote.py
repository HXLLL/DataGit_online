from typing import TYPE_CHECKING, Dict
from storage import storage
import urllib.parse
from version import Version
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
        vlist = controller.diff_version(repo_name, version_list)
        pickle.dump(vlist, self.wfile)
        self.wfile.flush()

        file_list = pickle.load(self.rfile)
        flist = controller.diff_files(file_list) # TODO
        pickle.dump(flist, self.wfile)
        self.wfile.flush()

        for f in flist:
            content = pickle.load(self.rfile)
            storage.save_file()                 # TODO save file content
        
        for f in vlist:
            _version: Dict = pickle.load(self.rfile)
            version = Version(None, None, None, None)
            version.load_from_dict(_version)
            repo.add_version(version)           # TODO: add version

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
