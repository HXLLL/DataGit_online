from typing import List
from modify import Modify
from directory import Directory
from transform import Transform
from update import Update
from version import Version
from typing import Tuple
import os
import utils
import shutil


class Stage():
    def __init__(self):
        self.__modify_sequence: List[Modify] = []
        root_dirname: str = os.path.split(utils.get_working_dir())[1]
        self.__dir_tree: Directory = Directory(root_dirname)

    def __scan_update(self, dir: str) -> Tuple[list, list]:
        '''
        功能:扫描dir文件夹里的修改。如果dir或dir的几层父目录之前不存在,那么也要放到Dir里面
        参数:dir是绝对路径
        返回值:返回改动的add_list和remove_list
            add_list的元素都是元组(path:str,file:Directory/Blob)
            remove_list的元素是path:str
            path是从工作区的根目录开始的
        '''

        '''
        dir文件夹在工作区内一定存在
        如果Dir的父文件夹不存在,要把dir的新增父文件夹的Dir构造出来
        '''
        assert(os.path.exists(dir))

        new_dir_tree = Directory()
        new_dir_tree.construct(dir)  # new_dir_tree是工作区内dir的目录树
        dir_relpath = os.path.relpath(dir, utils.get_working_dir())  # 转为相对路径
        dir_relpath = os.path.normpath(dir_relpath)  # 转为标准格式
        dirs = dir_relpath.split(os.sep)  # 路径拆分
        if dirs[0] == '.':
            del dirs[0]

        u = self.__dir_tree
        cur_path = '.'
        stop = -1
        for i, dirname in enumerate(dirs):
            v = u.enter(dirname)
            if not v:
                stop = i
                break
            u = v
            cur_path = os.path.join(cur_path, dirname)

        add_list = []
        remove_list = []
        if stop == -1:
            '''
            dir在stage中存在
            此时cur_path是到dir的相对路径
            u是self.dir_tree的子孙结点,是dir的目录树
            '''
            add_list, remove_list = new_dir_tree.get_update_list(u, cur_path)
            u.copy(new_dir_tree)
        elif stop == len(dirs) - 1:
            '''
            dir在stage中不存在,但dir的上一级目录在stage中存在
            此时cur_path是到dir上一级目录的相对路径
            u是self.dir_tree的子孙结点,是dir的上一级目录的目录树
            '''
            u.set_dir(new_dir_tree)
            add_list = [(cur_path, new_dir_tree)]
        else:
            '''
            dir和上面的某几级目录在stage中都不存在
            '''
            fa_dir_tree = Directory(dirs[stop])  # 最上层的原本不存在的目录的树结构
            v = fa_dir_tree
            for dirname in dirs[stop+1:-1]:
                w = Directory(dirname)
                v.set_dir(w)
                v = w
            # v现在是dir的上级目录的目录树
            v.set_dir(new_dir_tree)
            add_list = [(cur_path, fa_dir_tree)]

        return add_list, remove_list

    def update(self, dir: str, report_empty=True) -> None:
        '''
        参数是绝对路径
        '''
        # print(dir)
        if not utils.in_working_dir(dir):
            raise ValueError('path not in a valid repo')
        add_list, del_list = self.__scan_update(dir)
        if not add_list and not del_list:
            if report_empty:
                print('Nothing to update')
        else:
            # print('add_list:', add_list)
            # for item in add_list:
            #     print(item[1].get_name())
            # print('del_list:', del_list)
            # for item in del_list:
            #     print(item[1].get_name())
            upd = Update(add_list, del_list)
            self.__modify_sequence.append(upd)

    def add(self, src: str, dst: str) -> None:
        '''
        参数都是绝对路径
        '''

        '''
        1.建dst文件夹
        2.把src里面的东西扔到dst里面,若重名直接覆盖
        3.建立dst文件夹的Directory结构
        4.把dir结构扔到modify_sequence里面
        '''
        if not utils.in_working_dir(dst):
            raise ValueError('dst path not in a valid repo')
        src = os.path.normpath(src)
        dst = os.path.normpath(dst)
        if src.startswith(dst) or dst.startswith(src):
            raise ValueError('Paths cannot contain each other')
        if not os.path.exists(src):
            raise ValueError('src not a valid path')
        if not os.path.exists(dst):
            os.makedirs(dst)

        # 把src里的所有东西复制到dst
        for src_dir, dirnames, filenames in os.walk(src):
            # print('a:', src_dir, dirnames, filenames)
            for filename in filenames:
                rel_dir = os.path.relpath(src_dir, src)
                dst_dir = os.path.join(dst, rel_dir)
                src_file = os.path.join(src_dir, filename)
                dst_file = os.path.join(dst_dir, filename)
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                shutil.copy(src_file, dst_file)

        self.update(dst)

    def transform(self, code_dir: str, entry: str, isMap: int, data_dir: str, message: str):
        '''
        新建一个Transform实例,添加到modify_sequnece中,并应用到工作目录
        dir1是代码目录,dir2是数据目录,都是绝对路径
        '''
        if not os.path.exists(code_dir):
            raise ValueError('code directory not exist')
        if not os.path.exists(data_dir):
            raise ValueError('data directory not exist')
        relpath = os.path.relpath(data_dir, utils.get_working_dir())
        relpath = os.path.normpath(relpath)  # 转为标准格式

        # 在transform前进行update ./data_dir, 保存文件变化
        self.update(data_dir, report_empty=False)

        m = Transform(isMap, code_dir, entry, relpath, message)
        self.__modify_sequence.append(m)
        m.apply(utils.get_working_dir())
        dirs = relpath.split(os.sep)  # 路径拆分
        if dirs[0] == '.':
            del dirs[0]
        u = self.__dir_tree
        for dirname in dirs[:-1]:
            u = u.enter(dirname)
        if os.path.exists(data_dir):
            new_dir_tree = Directory()
            new_dir_tree.construct(data_dir)
            # 更新transform的目录的状态到目录树上
            if len(dirs) == 0:  # 如果transform的是根目录
                self.__dir_tree = new_dir_tree
            else:
                u.set_dir(new_dir_tree)
        else:
            u.del_dir(os.path.split(data_dir)[1])  # 目录没了
        # print('transform finished')
        # print(self.__dir_tree.unfold('transform_test'))

    def commit(self, parentID: int, id: int, message: str) -> Version:
        '''
        新建并返回一个Version实例
        '''
        new_version = Version(parentID, id, self.__modify_sequence.copy(), message)
        self.__modify_sequence.clear()
        return new_version

    def status(self) -> str:
        # print(self.__dir_tree.unfold('test'))
        res = ""
        for i, m in enumerate(self.__modify_sequence):
            res += ("Modify %d:\n" % i) + m.info() + "\n"
        if res == "":
            return "The working tree is clean."
        else:
            return res

    def reset(self) -> None:
        # TODO: prompt user when modify_sequence is not empty
        self.__dir_tree = Directory(self.__dir_tree.get_name())
        self.__dir_tree.construct(utils.get_working_dir())

        self.__modify_sequence = []

    def empty(self) -> None:
        return len(self.__modify_sequence) == 0
