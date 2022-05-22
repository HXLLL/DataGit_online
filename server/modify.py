from abc import ABC, abstractmethod


class Modify(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def apply(self, work_path: str):
        '''
        应用update或transform到work_path目录
        '''
        pass
    
    @abstractmethod
    def to_dict(self):
        pass
