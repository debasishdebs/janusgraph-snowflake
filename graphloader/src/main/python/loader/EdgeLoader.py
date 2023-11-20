from utils.constants import TIME_PROPERTIES, Commons
import uuid


class EdgeLoader:
    def __init__(self, edge, update, traversal):
        from client.traversal.GraphTraversal import GraphTraversal

        self.EDGE = edge
        self.UPDATE = update
        self.tr: GraphTraversal = traversal
        self.QUERY = None

    def load(self):
        if self.UPDATE:
            if "edge_id" in self.EDGE:
                self.QUERY = self.tr.addOrUpdateE()
            else:
                self.QUERY = self.tr.addOrUpdateE(uuid.uuid4())
        else:
            self.QUERY = self.tr.addE()

        for prop, val in self.EDGE.items():
            if prop == "edge_id":
                self.QUERY = self.QUERY.withId(uuid.UUID('{' + val + '}'))
            elif prop == "edge_label":
                self.QUERY = self.QUERY.withLabel(val)

            elif prop == "left":
                # print(f"Left: {val}")
                if isinstance(val, dict):
                    self.QUERY = self.QUERY.from_(val["property_key"], val["value"])
                else:
                    self.QUERY = self.QUERY.from_(int(val))

            elif prop == "right":
                # print(f"Right: {val}")
                if isinstance(val, dict):
                    self.QUERY = self.QUERY.to(val["property_key"], val["value"])
                else:
                    self.QUERY = self.QUERY.to(int(val))
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
            return self.QUERY.next()
        else:
            return self.QUERY.hold()
