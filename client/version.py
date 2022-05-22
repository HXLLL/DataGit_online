from typing import List
from modify import Modify
from typing import List
from update import Update


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
