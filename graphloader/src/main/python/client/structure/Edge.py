class Edge:
    def __init__(self, edge: dict):
        self.EDGE = edge

    def id(self):
        return self.EDGE["edge_id"]

    def label(self):
        return self.EDGE["label"]

    def src_id(self):
        return self.EDGE["src_id"]

    def dst_id(self):
        return self.EDGE["dst_id"]

    def properties(self, property_name=None):
        if property_name is None:
            return self.EDGE["properties"]
        else:
            return self.EDGE[property_name] if property_name in self.EDGE else ""

    def is_valid(self):
        return True if self.EDGE["src_id"] is not None and self.EDGE["dst_id"] is not None else False

    def __str__(self):
        return f"[E{self.id()}]"

    def to_dict(self):
        x = {
            "edge_id": self.id(),
            "label": self.label(),
            "source": self.src_id(),
            "target": self.dst_id()
        }
        for k, v in self.properties().items():
            x[k] = v
        return x
