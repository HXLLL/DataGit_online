from abc import ABC, abstractmethod


class Modify(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def load_from_dict(self):
        pass
