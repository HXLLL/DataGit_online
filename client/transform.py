import os
from typing import List, Dict

from core import utils
from core.directory import Directory
from client.modify import Modify
from client.storage import storage


class Transform(Modify):
    def __init__(self, isMap: int, script_dir: str, script_entry: str, script_working_dir: str, message: str) -> None:
        super().__init__()
        self.__isMap = isMap
        self.__script_dir = script_dir  # 绝对
        self.__script_entry = script_entry  # 相对
        self.__script_working_dir = script_working_dir  # 相对
        if script_dir != None:
            self.__id: int = storage.save_transform(script_dir)
        self.__message = message

    def apply(self, working_dir):
        '''
        将Transform对应脚本应用到working_dir目录下
        '''
        git_script_dir = os.path.join(utils.get_working_dir(), storage.get_transform(self.__id))
        git_script_entry = os.path.join(git_script_dir, self.__script_entry)
        # .datagit内script_entry的绝对路径

        if self.__isMap == 0:
            cmd = git_script_entry + " " + os.path.join(working_dir, self.__script_working_dir)
            save_dir = os.getcwd()
            os.chdir(git_script_dir)
            if os.system(cmd) != 0:
                raise RuntimeError('Transfomer exited abnormally')
            os.chdir(save_dir)
        else:
            working_dir = os.path.join(working_dir, self.__script_working_dir)
            save_dir = os.getcwd()
            os.chdir(git_script_dir)
            try:
                for root, adir, files in os.walk(working_dir):
                    if os.path.split(root)[1] == '.datagit':
                        adir[:] = []
                        files[:] = []
                    for afile in files:
                        cmd = git_script_entry + " " + os.path.join(root, afile)
                        os.system(cmd)
            except Exception as e:
                raise e
            finally:
                os.chdir(save_dir)

    def info(self) -> str:
        return f"    transform in directory[{self.__script_working_dir}]: {self.__message}"

    def to_dict(self):
        tmp_dict = {
            'type': 'transform',
            'isMap' : self.__isMap,
            'script_dir' : self.__script_dir, 
            'script_entry' : self.__script_entry, 
            'script_working_dir' : self.__script_working_dir,
            'id' : self.__id,
            'message' : self.__message
        }

        return tmp_dict
    
    def load_from_dict(self, d: Dict):
        self.__isMap = d['isMap']
        self.__script_dir = d['script_dir']
        self.__script_entry = d['script_entry']
        self.__script_working_dir = d['script_working_dir']
        self.__id = d['id']
        self.__message = d['message']

    def get_id(self):
        return self.__id