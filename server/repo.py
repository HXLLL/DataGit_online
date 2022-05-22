from typing import Tuple, List, Union, Dict
# from client.repo import VersionID
from storage import storage
from version import Version
from typing import List
import os
import utils

VersionID=int

class Repo:
    def __init__(self):
        self.init_version = Version(None, 1, [], 'init')
        self.versions: List[Version] = [self.init_version]
        self.saved_version: List[int] = []
        self.branch_map: dict[str, int] = {'main': 1}  # map branch name to version id
        self.version_map: dict[int, Version] = {1: self.init_version}  # map hash to version
        self.__parent_id: str = None  # fork的id

    def parent_id_init(self, name:str):
        self.__parent_id = name
    
    def get_parent_id(self) -> str:
        return self.__parent_id

    def init(self) -> None:
        storage.create_repo()
        storage.save_empty_version(1)
        self.saved_version = [1]
    
    def comp(self, version_list) -> List[VersionID]:
        Ans = []
        for item in version_list:
            if item not in self.version_map:
                Ans.append(item)
        return Ans

    def to_dict(self):
        List=[]
        List.append(('init_version', self.init_version))
        List.append(('versions', self.versions))
        List.append(('saved_version', self.saved_version))
        List.append(('branch_map', self.branch_map))
        List.append(('version_map', self.version_map))
        return dict(List)