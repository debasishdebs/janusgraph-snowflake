from utils.constants import TIME_PROPERTIES, Commons
from random import randint


class VertexLoader:
    def __init__(self, vertex, update, traversal):
        from client.traversal.GraphTraversal import GraphTraversal
        self.VERTEX = vertex
        self.UPDATE = update
        self.tr: GraphTraversal = traversal
        self.QUERY = None
        self.IDX = 0

    def load(self):
        ID = randint(90000+self.IDX, 1000000) if "node_id" not in self.VERTEX else 0
        if self.UPDATE:
            if ID == 0:
                self.QUERY = self.tr.addOrUpdateV()
            else:
                self.QUERY = self.tr.addOrUpdateV(ID)
        else:
            self.QUERY = self.tr.addV()

        for prop, val in self.VERTEX.items():
            if prop == "node_id":
                self.QUERY = self.QUERY.withId(int(val))
            elif prop == "node_label":
                self.QUERY = self.QUERY.withLabel(val)
            else:
                if prop in TIME_PROPERTIES:
                    self.QUERY = self.QUERY.property(prop, Commons.protobuf_time_to_datetime(val))
                else:
                    if isinstance(val, list):
                        for v in val:
                            self.QUERY = self.QUERY.property(prop, v)
                    else:
                        self.QUERY = self.QUERY.property(prop, val)

        return self

    def commit(self, persist=True):
        if persist:
            # print(f"Persisting {self.QUERY}")
            return self.QUERY.next()
        else:
            # print(f"Holding {self.QUERY}")
            return self.QUERY.hold()
