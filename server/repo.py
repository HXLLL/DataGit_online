from typing import Tuple, List, Union, Dict
from storage import storage
from version import Version
from stage import Stage
from typing import List
import os
import utils


class Repo:
    def __init__(self):
        self.init_version = Version(None, 1, [], 'init')
        self.versions: List[Version] = [self.init_version]
        self.saved_version: List[int] = []
        self.HEAD: Union[str, int] = 'main'
        self.detached_head: bool = False
        self.branch_map: dict[str, int] = {'main': 1}  # map branch name to version id
        self.version_map: dict[int, Version] = {1: self.init_version}  # map hash to version

    def init(self) -> None:
        storage.create_repo()
        storage.save_empty_version(1)
        self.saved_version = [1]

    def __new_version_id(self) -> int:
        return len(self.versions) + 1

    def commit(self, stage: Stage, message: str) -> None:
        """
        commit the stage, create a version with the stage
        save a stage to the repo's data structures
        """

        pid = None
        if not self.detached_head:
            b = self.HEAD
            assert type(b).__name__ == 'str'
            pid = self.branch_map[b]
        else:
            raise ValueError("can't commit in detached HEAD mode")

        id = self.__new_version_id()
        v = stage.commit(pid, id, message)
        self.version_map[id] = v
        self.versions.append(v)
        if not self.detached_head:
            b = self.HEAD
            assert type(b).__name__ == 'str'
            self.branch_map[b] = id

    def __find_saved_dataSet(self, dest_version: Version) -> Tuple[Version, List[Version]]:
        """
        given a version *dest*, find the nearest saved version in *dest*'s ancestors,
        return that ancestor and the route from that ancestor to *dest*
        """

        route = []
        v = dest_version
        while not v.id in self.saved_version:
            route.append(v)
            pid = v.parent
            v = self.version_map[pid]
        route.reverse()
        return v, route

    def checkout(self, dst: Union[int, str], to_branch: bool) -> None:  # op指示VersionID or branch_name
        """
        given a version ID or branch name, replace contents of the working dir with files of that branch
        """

        if to_branch:
            if not dst in self.branch_map:
                raise ValueError("Invalid branch name %s" % dst)
            self.HEAD = dst
            self.detached_head = False
            dst = self.branch_map[dst]
        else:
            if not dst in self.version_map:
                raise ValueError("Invalid version ID %d" % dst)
            self.detached_head = True
            self.HEAD = dst

        dest_version = self.version_map[dst]
        src_version, route = self.__find_saved_dataSet(dest_version)
        working_dir = utils.get_working_dir()
        storage.update_workingdir(src_version.id, working_dir)  # 以存储版本的复原

        modify_sequence = []
        for v in route:
            modify_sequence += v.modify_sequence
        for m in modify_sequence:
            m.apply(working_dir)

    def save(self, VersionID: int) -> None:
        """
        save a version.
        """
        if not VersionID in self.version_map:
            raise ValueError("Version not exists")
        if VersionID in self.saved_version:
            raise ValueError("This version has already been saved")

        dest_version = self.version_map[VersionID]  # exit if VersionID not exists
        src_version, route = self.__find_saved_dataSet(dest_version)
        tmp_dir = storage.create_tmp_dir()
        storage.update_workingdir(src_version.id, tmp_dir)  # 在某个位置将版本变换出来

        modify_sequence = []
        for v in route:
            modify_sequence += v.modify_sequence
        for m in modify_sequence:
            m.apply(tmp_dir)

        storage.save_version(dest_version.id, tmp_dir)
        self.saved_version.append(VersionID)

    def unsave(self, VersionID: int) -> None:
        """
        unsave a version.
        """
        if not VersionID in self.version_map:
            raise ValueError("Version not exists")
        if not VersionID in self.saved_version:
            raise ValueError("This version has not been saved")

        storage.delete_version(VersionID)
        self.saved_version.remove(VersionID)

    # TODO: adjust
    def find_suitable_versions(self, current_version: Version, flag: bool):
        cur_id = current_version.id
        if flag:
            self.save(cur_id)
        else:
            self.unsave(cur_id)
        child_list = [c for c in self.versions if c.parent == cur_id]
        for child in child_list:
            self.find_suitable_versions(self, child, not flag)
        return

    def adjust(self) -> None:
        self.find_suitable_versions(self.init_version, True)

#         suitable_versions = find_suitable_versions()
#         for Version in suitable_versions:
#             self.save(Version)/self.unsave(Version)

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

    def status(self) -> str:
        cur_branch = ""
        if self.detached_head:
            cur_branch = "Detached HEAD, at version %d" % self.HEAD
        else:
            cur_branch = "HEAD at branch %s" % self.HEAD

        stage = storage.load_stage()
        return cur_branch + "\n" + stage.status()

    def branch(self, branch_name) -> None:
        if branch_name in self.branch_map:
            raise ValueError("Branch already exists")

        if self.detached_head:
            self.branch_map[branch_name] = self.HEAD
        else:
            self.branch_map[branch_name] = self.branch_map[self.HEAD]

    def is_detached_head(self) -> bool:
        return self.detached_head
