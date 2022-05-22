import os
import shutil
from directory import Directory
import utils
import pickle
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from blob import Blob
    from repo import Repo


class Storage:
    def __init__(self):
        self.root_path = 'C:\\datagit'  # 暂时先写死

    def load_repo(self, repo_id: str) -> 'Repo':
        """
        load repo from root_path/repo_id/.datagit/repo
        """
        repo_path = os.path.join(self.root_path, repo_id, '.datagit', 'repo', 'repo.pk')
        with open(repo_path, 'rb') as repo_file:
            return pickle.load(repo_file)
        return None

    def save_repo(self, repo_id: str, repo: 'Repo') -> None:
        """
        save repo to .datagit/repo
        """
        repo_path = os.path.join(
            self.root_path, repo_id, '.datagit', 'repo', 'repo.pk')
        with open(repo_path, 'wb') as repo_file:
            pickle.dump(repo, repo_file)

    def create_repo(self) -> None:
        """
        Initialize a repo in current dir, 
        create all required directories for a repo
        """
        os.mkdir(".datagit")
        os.mkdir(os.path.join(".datagit", "repo"))
        os.mkdir(os.path.join(".datagit", "programs"))
        os.mkdir(os.path.join(".datagit", "versions"))

    def save_file(self, file_name: str) -> str:
        """
        save a file
        file_name -- absolute path of the file to save
        """

        h = utils.get_hash(file_name)
        dst = os.path.join(self.root_path, 'data', h)
        shutil.copy(file_name, dst)
        return h

    def get_file(self, hash_value: str) -> str:
        """
        given a file's hash value, return its path.
        return -- relative path to working dir's root
        """
        return os.path.join(self.root_path, 'data', "%s" % hash_value)

    def save_transform(self, repo_id: str, dir1: str) -> int:
        """
        save a transform program to the repo and assign an ID to it
        dir1 -- the program's absolute dir
        return -- the assigned id
        """
        program_dir = os.path.join(self.root_path, repo_id, ".datagit", "programs")
        cnt = len(os.listdir(program_dir))
        id = cnt + 1
        dst = os.path.join(program_dir, "%d" % id)
        shutil.copytree(dir1, dst)
        return id

    def get_transform(self, id: int) -> str:
        """
        given a transform program's id, return its relative path
        return -- relative path to working dir's root
        """

        return os.path.join(".datagit", "programs", "%d" % id)

storage = Storage()
