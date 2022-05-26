import os
import pathlib
import pickle
import socketserver
import urllib.parse
import zipfile
from multiprocessing import Process 
from typing import TYPE_CHECKING, Dict

from core import utils
from server import controller
from server.version import Version
from server.storage import storage
if TYPE_CHECKING:
    from server.repo import Repo

server_addr = ("localhost", 8887)

class Handler(socketserver.StreamRequestHandler):
    def push(self) -> None:
        """
        refer to client/remote.py for network communication protocol
        """

        # 2. 3.
        branch = self.rfile.readline().decode("utf-8").strip()
        uri = self.rfile.readline().decode("utf-8").strip()
        l = uri.strip('/').split('/')
        assert len(l) == 1
        repo_name = l[0]

        # 4. 5.
        msg = os.urandom(32)
        public_key = storage.get_public_key(repo_name) # TODO
        ciphertext = utils.encrypt(msg, public_key)
        pickle.dump(ciphertext, self.wfile)
        self.wfile.flush()
        resp = pickle.load(self.rfile)
        if msg != resp:
            print("Authentication Failed")
            return
        
        # 6. 7.
        version_list = pickle.load(self.rfile)
        vlist = controller.diff_version(repo_name, version_list)
        pickle.dump(vlist, self.wfile)
        self.wfile.flush()

        # 8. 9.
        file_list = pickle.load(self.rfile)
        flist = controller.diff_files(file_list)
        pickle.dump(flist, self.wfile)
        self.wfile.flush()

        # 10.
        for f in flist:
            content = pickle.load(self.rfile)
            storage.save_file(f, content)
        
        # 11.
        version_list = []
        for f in vlist:
            _version: Dict = pickle.load(self.rfile)
            version = Version(None, None, None, None)
            version.load_from_dict(_version)
            version_list.append(version)
        controller.update_repo(repo_name, branch, version_list)

    def get(self) -> None:
        pass

    def clone(self) -> None:
        uri = self.rfile.readline().decode("utf-8").strip()
        l = uri.strip('/').split('/')
        assert len(l) == 1
        repo_name = l[0]

        '''
        需要传输的数据:
            repo_name
            .datagit/repo
            .datagit/programs
            .datagit/data
        '''

        # send repo_name
        self.wfile.write((repo_name + '\n').encode('utf-8'))
        self.wfile.flush()

        if self.wfile.readline() == 'repo_exist':
            return

        # send repo
        repo = storage.load_repo(repo_name)
        pickle.dump(repo.to_dict(), self.wfile)
        self.wfile.flush()

        # send programs
        def get_zip(dir_path):
            zip = zipfile.ZipFile(os.path.dir(repo_path, 'tmp.zip'), 'w', zipfile.ZIP_DEFLATED)
            for path, _, filenames in os.walk(dir_path):
                fpath = path.replace(dir_path, '')
                for filename in filenames:
                    zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
            zip.close()
        
        get_zip(os.path.join(repo_path, 'programs'))
        with open(os.path.join(repo_path, 'tmp.zip'), 'rb') as prog_file:
            self.wfile.write(prog_file.read())
            self.wfile.flush()
        os.remove(os.path.dir(repo_path, 'tmp.zip'))

        # send data
        file_list = [] # path of files
        for v in repo.versions:
            hash_list = v.get_hash_list()
            for hash_value in hash_list:
                file_path = storage.get_file(hash_value)
                if not file_path in file_list:
                    file_list.append(file_path)
        
        for f in file_list:
            pass


    def handle(self):
        command = self.rfile.readline().decode("utf-8").strip()
        if command == "push":
            self.push()
        elif command == "get":
            pass
        elif command == "clone":
            self.clone()
        else:
            print(f"{command}: Command Not Exists!")

def main() -> None:
    with socketserver.TCPServer(server_addr, Handler) as s:
        s.serve_forever()

if __name__ == '__main__':
    main()
