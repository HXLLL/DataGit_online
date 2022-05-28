from typing import List, Dict

from client.modify import Modify
from client.transform import Transform
from client.update import Update


class Version():
    def __init__(self, parent: int, id: int, modify_sequence: List[Modify],
                 message: str) -> None:
        '''
        parent以VersionID的形式保存
        '''
        self.id = id
        self.parent = parent
        self.modify_sequence = modify_sequence
        self.message = message

    def get_hash_list(self) -> List:
        hash_list = []
        for item in self.modify_sequence:
            if isinstance(item, Update):
                hash_list += item.load_hash()
        return hash_list
    
    def to_dict(self):
        modify_sequence_tmp = []
        for item in self.modify_sequence:
            modify_sequence_tmp.append(item.to_dict)
        
        tmp_dict = {
            'id' : self.id,
            'parent' : self.parent,
            'modify_sequence' : modify_sequence_tmp,
            'message' : self.message
        }

        return tmp_dict

    def load_from_dict(self, d: Dict):
        print('version__from_dict: ', d)
        self.id = d['id']
        self.parent = d['parent']
        self.message = d['message']

        self.modify_sequence = []
        seq = d['modify_sequence']
        for item in seq:
            t = None
            if item['type'] == 'transform':
                t = Transform(None, None, None, None, None)
            elif item['type'] == 'update':
                t = Update(None, None)
            t.load_from_dict(item)
            self.modify_sequence.append(t)