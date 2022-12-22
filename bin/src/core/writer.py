from abc import ABC, abstractmethod

class Writer:
    args = None
    
    def __init__(self, args):
        self.args = args

    @abstractmethod
    def write(self, distribution, mem_systems):
        pass
