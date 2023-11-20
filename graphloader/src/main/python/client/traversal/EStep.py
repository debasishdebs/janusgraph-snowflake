from abc import ABC, abstractmethod
from client.traversal import Traversal


class EStep(Traversal.Traversal):
    def __init__(self):
        super().__init__()
        pass

    @abstractmethod
    def inV(self):
        pass

    @abstractmethod
    def outV(self):
        pass

    @abstractmethod
    def otherV(self):
        pass

    def properties(self):
        # self.byte_rep = [self.byte_rep]
        self.byte_rep.append([["properties", str(False)]])
        from client.traversal.PropertiesStep import PropertiesStep
        return PropertiesStep(self.byte_rep)

    def id(self):
        return

    def label(self):
        return
