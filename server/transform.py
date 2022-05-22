from modify import Modify
from directory import Directory
from typing import List
from storage import storage
import os
import utils


class Transform(Modify):
    def info(self) -> str:
        return f"    transform in directory[{self.__script_working_dir}]: {self.__message}"
