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
    def __init__(self, add_list: List, remove_list: List):
        '''
        两个list的元素都是元组(path:str,file:Directory/Blob)
        path是从工作区的根目录开始的
        '''
        super().__init__()
        self.__add_list: List[Tuple[str, Union[Directory, Blob]]] = add_list
        self.__remove_list: List[Tuple[str, Union[Directory, Blob]]] = remove_list
        # 保存add_list内的文件
        files_n = 0
        for item in self.__add_list:
            files_n += len(item[1].unfold(os.path.join(utils.get_working_dir(), item[0])))

        with Pool(8, utils.init_worker) as p, tqdm(total=files_n, desc="Copy files") as pbar:
            res = []
            for item in self.__add_list:
                Files = item[1].unfold(os.path.join(utils.get_working_dir(), item[0]))
                for atuple in Files:
                    def error():
                        print("Error")
                        raise
                    def init_callback(res, blob=atuple[1]):
                        pbar.update(1)
                        blob.set_hash(res)
                    res.append(p.apply_async(storage.save_file, [
                               atuple[0]], callback=init_callback, error_callback=error))
            for a in res:
                a.wait()
    
    def to_dict(self):
        tmp_dict = {
            'add_list' : self.__add_list,
            'remove_list' : self.__remove_list
        }

        return tmp_dict
    
