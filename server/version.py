from typing import List

from server.modify import Modify
from server.update import Update
from server.transform import Transform


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
    
    def to_dict(self):
        modify_sequence_tmp = []
        for item in self.modify_sequence:
            modify_sequence_tmp.append(item.to_dict())
        
        tmp_dict = {
            'id' : self.id,
            'parent' : self.parent,
            'modify_sequence' : modify_sequence_tmp,
            'message' : self.message
        }

        return tmp_dict
    
    def load_from_dict(self, init_dict):
        self.id = init_dict['id']
        self.parent = init_dict['parent']
        self.modify_sequence = []
        for item in init_dict['modify_sequence']:
            if item['type'] == 'update':
                tmp = Update()
                tmp.load_from_dict(item)
                self.modify_sequence.append(tmp)
            else:
                tmp = Transform()
                tmp.load_from_dict(item)
                self.modify_sequence.append(tmp)
        
        self.message = init_dict['message']

    def get_hash_list(self) -> List:
        hash_list = []
        for item in self.modify_sequence:
            if isinstance(item, Update):
                hash_list += item.load_hash()
        return hash_list
