import os
from typing import List

from core.directory import Directory
from core import utils
from modify import Modify
from storage import storage

class Transform(Modify):

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
    
    def load_from_dict(self, init_dict):
        self.__isMap = init_dict['isMap']
        self.__script_dir = init_dict['script_dir']
        self.__script_entry = init_dict['script_entry']
        self.__script_working_dir = init_dict['script_working_dir']
        self.__id = init_dict['id']
        self.__message = init_dict['message']
        
