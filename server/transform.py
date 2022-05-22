from modify import Modify
from directory import Directory
from typing import List
from storage import storage
import os
import utils


class Transform(Modify):
    
    def to_dict(self):
        tmp_dict = {
            'isMap' : self.__isMap,
            'script_dir' : self.__script_dir, 
            'script_entry' : self.__script_entry, 
            'script_working_dir' : self.__script_working_dir,
            'id' : self.__id,
            'message' : self.__message
        }

        return tmp_dict
        
