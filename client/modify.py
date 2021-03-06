from abc import ABC, abstractmethod
from typing import List

class Modify(ABC):
    def __init__(self):
        self.description = "error: this should not be printed"

    @abstractmethod
    def apply(self, work_path: str):
        '''
        应用update或transform到work_path目录
        '''
        pass

    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def load_from_dict(self):
        pass
