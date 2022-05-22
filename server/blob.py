from typing import List, Tuple
import os
import utils


class Blob:
    def __init__(self, name, hash=None) -> None:
        self.__name = name  # 文件名称
        self.__hash = hash  # 文件哈希值

    def get_name(self) -> str:
        return self.__name

    def get_hash(self) -> str:
        return self.__hash

    def set_hash(self, hash: str) -> None:
        self.__hash = hash

    def get_type(self) -> str:
        return "blob"

    def unfold(self, root_path: str) -> List[Tuple[str, 'Blob']]:
        return [(os.path.join(root_path, self.__name), self)]

    def size(self) -> int:
        return 1
