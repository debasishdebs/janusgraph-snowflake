from client.structure.Edge import Edge
from typing import Dict


class Vertex:
    def __init__(self, node: dict):
        self.NODE = node
        self.EDGES: Dict[str, Edge] = dict()

    def properties(self, property_name=None):
        if property_name is None:
            return self.NODE["properties"]
        else:
            return self.NODE[property_name] if property_name in self.NODE else ""

    def is_valid(self):
        return True if self.NODE["node_id"] is not None else False

    def id(self):
        return self.NODE["node_id"]

    def label(self):
        return self.NODE["label"]

    def add_edge(self, edge: Edge):
        if edge.id() not in self.EDGES:
            self.EDGES[edge.id()] = edge
        return self

    def edges(self):
        return list(self.EDGES.values())

    def outEdges(self):
        return [x for x in self.EDGES.values() if x.src_id() == self.id()]

    def inEdges(self):
        return [x for x in self.EDGES.values() if x.dst_id() == self.id()]

    def __str__(self):
        return f"[V{self.id()}]"

    def to_dict(self, edges=False):
        x = {
            "node_id": self.id(),
            "label": self.label(),
        }
        for k, v in self.properties().items():
            x[k] = v
        if edges:
            x["edges"] = []
            for e in self.edges():
                x["edges"].append(e)
        return x
