from typing import List
from modify import Modify
from typing import List


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
            modify_sequence_tmp.append(item.to_dict)
        
        tmp_dict = {
            'id' : self.id,
            'parent' : self.parent,
            'modify_sequence' : modify_sequence_tmp,
            'message' : self.message
        }

        return tmp_dict
