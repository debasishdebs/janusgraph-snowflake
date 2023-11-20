from client.traversal import Traversal


class PropertiesStep(Traversal.Traversal):
    def __init__(self, byte_arr=None):
        super().__init__()
        if byte_arr is None:
            self.byte_rep = []
        else:
            self.byte_rep = byte_arr

    def __str__(self):
        return str(self.byte_rep)
