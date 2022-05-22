from modify import Modify
from directory import Directory
from typing import List
from storage import storage
import os
import utils


class Transform(Modify):
    def __init__(self, isMap: int, script_dir: str, script_entry: str, script_working_dir: str, message: str) -> None:
        super().__init__()
        self.__isMap = isMap
        self.__script_dir = script_dir  # 绝对
        self.__script_entry = script_entry  # 相对
        self.__script_working_dir = script_working_dir  # 相对
        self.__id: int = storage.save_transform(script_dir)
        self.__message = message

    def info(self) -> str:
        return f"    transform in directory[{self.__script_working_dir}]: {self.__message}"
