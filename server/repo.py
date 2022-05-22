from typing import Tuple, List, Union, Dict
from client.repo import VersionID
from storage import storage
from version import Version
from typing import List
import os
import utils

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
        lst=[]
        init_version_tmp = self.init_version.to_dict()
        versions_tmp = []
        for item in self.versions:
            versions_tmp.append(item.to_dict())
        
        version_map_tmp=dict()
        for item in self.version_map.keys():
            version_map_tmp[item] = self.version_map[item].to_dict()
        
        tmp_dict = {
            'init_version' : init_version_tmp,
            'versions' : versions_tmp,
            'saved_version' : self.saved_version,
            'HEAD' : self.HEAD,
            'detached_head' : self.detached_head,
            'branch_map' : self.branch_map,
            'version_map' : version_map_tmp
        }

        return tmp_dict
