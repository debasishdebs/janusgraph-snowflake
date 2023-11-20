from typing import List
from client.structure.Edge import Edge
from client.structure.Vertex import Vertex


class SnowGraph(object):

    def __init__(self, vertices: List[Vertex], edges: List[Edge]):
        self.VERTICES = vertices
        self.EDGES = edges

    def to_json(self):
        graph = {
            "nodes": [x.to_dict() for x in self.VERTICES],
            "edges": [x.to_dict() for x in self.EDGES]
        }
        print(f"Nodes: {len(graph['nodes'])}, Edges: {len(graph['edges'])}")
        return graph

    def vertices(self):
        return self.VERTICES

    def edges(self):
        return self.EDGES

    def size(self):
        return f"[nodes: {len(self.VERTICES)}, edges: {len(self.EDGES)}]"
