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
    def info(self) -> str:
        def file2str(f):
            return os.path.join(f[0], f[1].get_name())
        res = '    add files: \n        ' \
            + '\n        '.join(map(file2str, self.__add_list[:10])) \
            + ('\n        ......' if len(self.__add_list) > 10 else '') + '\n' \
            + '    del files: \n        ' \
            + '\n        '.join(map(file2str, self.__remove_list[:10])) \
            + ('\n        ......' if len(self.__remove_list) > 10 else '')
        return res
