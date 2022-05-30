import os
from typing import Tuple, List, Union, Dict

from core import utils
from core.types import VersionID
from server.storage import storage
from server.version import Version
from server_remote import Handler

class Repo:
    def __init__(self):
        self.init_version = Version(None, 1, [], 'init')
        self.versions: List[Version] = [self.init_version]
        self.version_map: dict[int, Version] = {1: self.init_version}  # map id to version
        self.branch_map: dict[str, VersionID] = {'main': 1}  # map branch name to version id
        self.__parent_id: str = None  # fork的id

    def parent_id_init(self, name:str):
        self.__parent_id = name
    
    def get_parent_id(self) -> str:
        return self.__parent_id
    
    def add_version(self, version: Version) -> None:
        self.versions.append(version)
        self.version_map[version.id] = version
    
    def move_branch(self, branch_name: str, version_id: VersionID):
        self.branch_map[branch_name] = version_id
    
    def comp(self, version_list) -> List[VersionID]:
        Ans = []
        for item in version_list:
            if item not in self.version_map:
                Ans.append(item)
        return Ans

    def __find_log(self, current_version: Version, prefix: str):
        cur_id = current_version.id
        cur_branches = [k for k, v in self.branch_map.items() if v == cur_id]
        if self.detached_head and self.HEAD == cur_id:
            cur_branches.append('HEAD')
        elif not self.detached_head and self.HEAD in cur_branches:
            idx = cur_branches.index(self.HEAD)
            cur_branches[idx] = "%s <- HEAD" % self.HEAD
        res_branch = "(" + ", ".join(cur_branches) + ")"
        res = prefix + "* %d %s: %s" % (current_version.id, res_branch, current_version.message)
        if current_version.id in self.saved_version:
            res += " (saved)"
        res += "\n"

        child_list = [c for c in self.versions if c.parent == cur_id]
        if len(child_list) == 0:
            return res
        for child in child_list[:-1]:
            res += prefix + '|\\\n'
            res += self.__find_log(child, prefix + "| ")
        res += prefix + ' \\\n'
        res += self.__find_log(child_list[-1], prefix + '  ')
        return res

    def log(self) -> str:
        return self.__find_log(self.init_version, "")

    def get_info(self) -> str:
        info = ""
        if self.__parent_id is None:
            info += "created by user\n"
        else:
            info += f"fork from {self.__parent_id}"
        info += self.log()
        return info

    def to_dict(self) -> dict:
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
            'version_map' : version_map_tmp,
            'branch_map' : self.branch_map
        }

        return tmp_dict

    def get(self, dst:VersionID):
        if not dst in self.version_map:
            return False
        dest_version = self.version_map[dst]
        route, v = [], dest_version
        while v.id != 1:
            route.append(v)
            pid = v.parent
            v = self.version_map[pid]
        route.reverse()
        return route
