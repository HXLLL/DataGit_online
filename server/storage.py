import os
import shutil
import pickle
import platform
from cryptography.hazmat.primitives.asymmetric import rsa
from typing import TYPE_CHECKING, List

from core.directory import Directory
from core import utils
if TYPE_CHECKING:
    from core.blob import Blob
    from server.repo import Repo


class Storage:
    def __init__(self):
        self.root_path = 'C:\\datagit'  # 暂时先写死
        if platform.system() == 'Linux':
            self.root_path = '/var/datagit'
        if not os.path.exists(os.path.join(self.root_path, 'data')):
            os.makedirs(os.path.join(self.root_path, 'data'))
        if not os.path.exists(os.path.join(self.root_path, 'repo')):
            os.makedirs(os.path.join(self.root_path, 'repo'))

    def load_repo(self, repo_name: str) -> 'Repo':
        """
        load repo
        """
        repo_path = os.path.join(self.get_repo_path(repo_name), 'repo', 'repo.pk')
        with open(repo_path, 'rb') as repo_file:
            return pickle.load(repo_file)
        return None

    def save_repo(self, repo_name: str, repo: 'Repo') -> None:
        """
        save repo
        """
        repo_path = os.path.join(self.get_repo_path(repo_name), 'repo', 'repo.pk')
        with open(repo_path, 'wb') as repo_file:
            pickle.dump(repo, repo_file)

    def save_file(self, filename: str, data: bytes) -> None:
        """
        保存文件
        filename: 文件名，即哈希值
        data: 文件数据
        调用者需要保证该文件原本没有保存
        """
        file_path = os.path.join(self.root_path, 'data', filename)
        with open(file_path, 'wb') as fout:
            fout.write(data)

    def get_file(self, hash_value: str) -> str:
        """
        given a file's hash value, return its path.
        return -- relative path to working dir's root
        """
        return os.path.join(self.root_path, 'data', "%s" % hash_value)

    def save_transform(self, repo_name: str, dir1: str) -> int:
        """
        save a transform program to the repo and assign an ID to it
        dir1 -- the program's absolute dir
        return -- the assigned id
        """
        program_dir = os.path.join(self.get_repo_path(repo_name), "programs")
        cnt = len(os.listdir(program_dir))
        id = cnt + 1
        dst = os.path.join(program_dir, "%d" % id)
        shutil.copytree(dir1, dst)
        return id
    
    def copy_repo(self, old_name: str, new_name: str) -> None:
        # 假设调用方保证new_name不是已有的仓库名字
        src = os.path.join(self.get_repo_path(old_name))
        dst = os.path.join(self.get_repo_path(new_name))
        for src_dir, dirnames, filenames in os.walk(src):
            rel_dir = os.path.relpath(src_dir, src)
            dst_dir = os.path.join(dst, rel_dir)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for filename in filenames:
                src_file = os.path.join(src_dir, filename)
                dst_file = os.path.join(dst_dir, filename)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                shutil.copy(src_file, dst_file)
        key_path = os.path.join(self.get_repo_path(new_name), 'ssh', 'public_key')
        os.remove(key_path)
    
    def create_repo(self, repo_name: str) -> None:
        os.makedirs(os.path.join(self.get_repo_path(repo_name), 'repo'))
        os.makedirs(os.path.join(self.get_repo_path(repo_name), 'programs'))
        os.makedirs(os.path.join(self.get_repo_path(repo_name), 'ssh'))
    
    def get_repo_name(self) -> List[str]:
        return os.listdir(os.path.join(self.root_path, 'repos'))

    def exist_file(self, hash: str) -> bool:
        return os.path.exists(os.path.join(self.root_path, 'data', hash))
    
    def get_repo_path(self, repo_name: str) -> str:
        return os.path.join(self.root_path, 'repos', repo_name)
    
    def exist_repo(self, repo_name: str) -> bool:
        return os.path.exists(self.get_repo_path(repo_name))
    
    def save_public_key(self, repo_name: str, file_path: str) -> None:
        dst_path = os.path.join(self.get_repo_path(repo_name), 'ssh', 'public_key')
        shutil.copy(file_path, dst_path)
    
    def load_public_key(self, repo_name: str) -> rsa.RSAPublicKey:
        key_path = os.path.join(self.get_repo_path(repo_name), 'ssh', 'public_key')
        if os.path.exists(key_path):
            return utils.load_public_key(key_path)
        return None

storage = Storage()
