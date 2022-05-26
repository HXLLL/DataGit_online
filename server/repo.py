import os
from typing import Tuple, List, Union, Dict

from core import utils
from core.types import VersionID
from server.storage import storage
from server.version import Version

class Repo:
    def __init__(self):
        self.init_version = Version(None, 1, [], 'init')
        self.versions: List[Version] = [self.init_version]
        self.version_map: dict[int, Version] = {1: self.init_version}  # map id to version
        self.__parent_id: str = None  # fork的id

    def parent_id_init(self, name:str):
        self.__parent_id = name
    
    def get_parent_id(self) -> str:
        return self.__parent_id

    def init(self) -> None:
        storage.create_repo()
        storage.save_empty_version(1)
    
    def add_version(self, version: Version) -> None:
        self.versions.append(version)
        self.version_map[version.id] = version
    
    def comp(self, version_list) -> List[VersionID]:
        Ans = []
        for item in version_list:
            if item not in self.version_map:
                Ans.append(item)
        return Ans

    def to_dict(self):
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
            'version_map' : version_map_tmp
        }

        return tmp_dict
