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

    def apply(self, working_dir):
        '''
        将Update对应文件增删应用到working_dir目录下
        '''
        # print('apply:')
        # for a in self.__add_list:
        #     print(a[0], a[1].unfold('add_test'))
        # for a in self.__remove_list:
        #     print(a[0], a[1].unfold('del_test'))

        total = sum([x[1].size() for x in self.__add_list])
        with Pool(8, utils.init_worker) as p, tqdm(total=total, desc="Apply update") as bar:
            res = []

            def move_file(base_path, afile) -> None:
                '''
                还原单个文件
                '''
                git_file_name_0 = utils.get_working_dir()
                git_file_name_1 = storage.get_file(afile.get_hash())
                filename = os.path.join(git_file_name_0, git_file_name_1)

                def error():
                    print("Error")
                    raise
                def move_file_callback(res):
                    bar.update(1)
                res.append(p.apply_async(shutil.copyfile, [
                           filename, base_path], callback=move_file_callback, error_callback=error))

            def move_dir(base_path, adir) -> None:
                '''
                将dir类下的目录结构还原,文件加入working_dir目录下
                '''
                if not os.path.exists(base_path):
                    os.makedirs(base_path)

                for item in adir.get_dirs().values():
                    move_dir(os.path.join(base_path, item.get_name()), item)

                for item in adir.get_files().values():
                    move_file(os.path.join(base_path, item.get_name()), item)

            for item in self.__remove_list:
                path = os.path.join(working_dir, item[0], item[1].get_name())
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)

            for item in self.__add_list:
                item_abs_path = os.path.join(working_dir, item[0], item[1].get_name())
                if item[1].get_type() == 'directory':
                    move_dir(item_abs_path, item[1])
                else:
                    move_file(item_abs_path, item[1])
            
            for r in res:
                r.wait()

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
