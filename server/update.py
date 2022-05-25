import os
import shutil
from typing import List, Union, Tuple

from tqdm import tqdm

from core.directory import Directory
from core.blob import Blob
from core import utils
from server.modify import Modify
from server.storage import storage


class Update(Modify):
    
    def to_dict(self):
        tmp_dict = {
            'type' : 'update',
            'add_list' : self.__add_list,
            'remove_list' : self.__remove_list
        }

        return tmp_dict
          
    def load_from_dict(self, init_dict):
        self.__add_list = init_dict['add_list']
        self.__remove_list = init_dict['remove_list']
