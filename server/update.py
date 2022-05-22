from modify import Modify
from typing import List, Union, Tuple
from storage import storage
from directory import Directory
from blob import Blob
import utils
import os
import shutil
from tqdm import tqdm
from multiprocessing import Pool


class Update(Modify):
    
    def to_dict(self):
        tmp_dict = {
            'type' : 'update',
            'add_list' : self.__add_list,
            'remove_list' : self.__remove_list
        }

        return tmp_dict