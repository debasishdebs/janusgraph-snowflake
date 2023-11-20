from utils.constants import BATCH_SIZE, ADD_OR_UPDATE_EDGE, ADD_OR_UPDATE_NODE
from loader.VertexLoader import VertexLoader
from loader.EdgeLoader import EdgeLoader
from utils.constants import Commons


class GraphLoader:
    def __init__(self, graph):
        self.GRAPH = graph
        self.TRAVERSAL = None

        self.BATCH_SIZE = BATCH_SIZE
        self.UPDATE_NODE = ADD_OR_UPDATE_NODE
        self.UPDATE_EDGE = ADD_OR_UPDATE_EDGE

        self.NODES_IN_CASE = []

    def with_traversal(self, tr):
        self.TRAVERSAL = tr
        return self
    #
    # def _convert_value_to_struct_value_(self, v):
    #     if list(v.keys())[0] == "stringValue":
    #         s = str(list(v.values())[0])
    #     elif isinstance(v, int):
    #         s = StructureValue(int_value=v)
    #     elif isinstance(v, float):
    #         s = StructureValue(number_value=v)
    #     elif isinstance(v, dict):
    #         s = self._python_dict_to_proto_generic_struct_value_(v)
    #     elif isinstance(v, list):
    #         if len(v) > 1:
    #             l = ListValue()
    #             for vv in v:
    #                 ss = self._convert_value_to_struct_value_(vv)
    #                 l.values.append(ss)
    #             s = StructureValue(list_value=l)
    #         else:
    #             s = self._convert_value_to_struct_value_(v[0])
    #     else:
    #         self.ERROR["ResponseConverter"] = f"Supports only str/int/float/dict in response element type got{type(v)}  " \
    #             f"for {str(v)}"
    #         print(self.ERROR)
    #         return self

    def convert(self):
        nodes_new = []
        nodes_old = self.GRAPH["nodes"]
        for node_old in nodes_old:
            node_properties = node_old["properties"]
            node_new = {}
            for k, v in node_properties.items():
                for value_type, value in v.items():
                    if value_type == "stringValue":
                        # print(f"Encountered stringValue for val: {value} with key {k} or dict {v}")
                        value_f = str(value)
                        value_f = value_f.replace("$", "")
                    elif value_type == "intValue":
                        value_f = int(value)
                    elif value_type == "bytesValue":
                        value_f = value
                    elif value_type == "listValue":
                        # print(f"Encountered listValue for val: {value} with key {k} or dict {v}")
                        values = []
                        for vv in value["values"]:
                            values.append(list(vv.values())[0].replace("$", ""))
                        value_f = values if len(values) > 1 else values[0]
                        # print(f"listValue after conversion is {value_f}")
                    elif value_type == "structValue":
                        value_f = self.proto_struct_dict_to_python_dict(value)
                    else:
                        print("Not implemented " + value_type + " datatype conversion from server for " + k + " and " + str(v) + " and " + str(node_properties))
                        # raise NotImplementedError("Not implemented " + value_type + " datatype conversion from server for " + k + " and " + str(v) + " and " + str(node_properties))
                        continue

                    node_new[k] = value_f
            nodes_new.append(node_new)

        edges_new = []
        edges_old = self.GRAPH["edges"]
        for edge_old in edges_old:
            edge_properties = edge_old["properties"]
            edge_new = {}
            for k, v in edge_properties.items():
                for value_type, value in v.items():
                    if value_type == "stringValue":
                        value_f = str(value)
                        value_f = value_f.replace("$", "")
                    elif value_type == "intValue":
                        value_f = int(value)
                    elif value_type == "bytesValue":
                        value_f = value
                    elif value_type == "listValue":
                        values = []
                        for vv in value["values"]:
                            values.append(list(vv.values())[0].replace("$", ""))
                        value_f = values if len(values) > 1 else values[0]
                    # elif value_type == "number_value":
                    #     value_f = float(value)
                    elif value_type == "structValue":
                        value_f = self.proto_struct_dict_to_python_dict(value)
                    else:
                        raise NotImplementedError("Not implemented " + value_type + " datatype conversion from server")

                    edge_new[k] = value_f
            edges_new.append(edge_new)

        self.GRAPH["nodes"] = nodes_new
        self.GRAPH["edges"] = edges_new
        return self

    def proto_struct_dict_to_python_dict(self, value):
        struct_val = {}
        for k, v in value["fields"].items():
            for value_type, value_a in v.items():
                if value_type == "stringValue":
                    value_f = str(value_a)
                    value_f = value_f.replace("$", "")
                elif value_type == "intValue":
                    value_f = int(value_a)
                elif value_type == "bytesValue":
                    value_f = value
                    # elif value_type == "number_value":
                    #     value_f = float(value)
                elif value_type == "structValue":
                    value_f = self.proto_struct_dict_to_python_dict(value_a)
                else:
                    raise NotImplementedError("Not implemented " + value_type + " datatype conversion from server")
                struct_val[k] = value_f
        return struct_val

    def _get_node_key_value_pair_(self, node):
        node_prop = "ip" if "ip" in node else "hostname" if "hostname" in node \
            else "emailSubject" if "emailSubject" in node else "userName" if "userName" in node \
            else "fileName" if "fileName" in node else "URL" if "URL" in node else "INVALID"
        return node_prop, node[node_prop] if node_prop is not "INVALID" else "INVALID"

    def load(self):
        import copy

        if self.TRAVERSAL is None:
            raise AttributeError("Please initialize the traversal first before executing load() using with_traversal()")

        nodes = self.GRAPH["nodes"]
        edges = self.GRAPH["edges"]

        node_responses = []
        traversal = copy.deepcopy(self.TRAVERSAL)

        status_nodes = []
        node_tracker = {"ip": [], "hostname": [], "emailSubject": [], "userName": [], "fileName": [], "URL": [], "INVALID": []}
        node_batches = list(Commons.chunks(nodes, self.BATCH_SIZE))
        for batch in node_batches:
            for i in range(len(batch)):
                node = batch[i]
                node_prop, node_val = self._get_node_key_value_pair_(node)
                if node_val not in node_tracker[node_prop]:
                    loader = VertexLoader(node, self.UPDATE_NODE, traversal)
                    loader.IDX = i
                    loader.load()

                    if i == len(batch) - 1:
                        o = loader.commit(True)
                    else:
                        o = loader.commit(False)

                    node_id = node["node_id"]

                    node_responses.append(o)
                    status_nodes.append({"node_id": node_id, node_prop: node_val})
                    node_tracker[node_prop].append(node_val)
                else:
                    print(f"Duplicate node found for {node}")

        #
        #
        # for i in range(len(nodes)):
        #     node = nodes[i]
        #     node_prop, node_val = self._get_node_key_value_pair_(node)
        #     print(node_prop, node_val, node_tracker)
        #     if node_val not in node_tracker[node_prop]:
        #         loader = VertexLoader(node, self.UPDATE_NODE, traversal)
        #         loader.IDX = i
        #         loader.load()
        #
        #         if (i % self.BATCH_SIZE) == 0:
        #             o = loader.commit(True)
        #         else:
        #             o = loader.commit(False)
        #
        #         if i == len(nodes) - 1:
        #             o = loader.commit(True)
        #
        #         node_responses.append(o)
        #
        #         node_id = node["node_id"]
        #         status_nodes.append({"node_id": node_id, node_prop: node_val})
        #
        #         node_tracker[node_prop].append(node_val)
        #     else:
        #         print(f"Duplicate node found for {node}")
        #
        #     #
        #     # try:
        #     #     if (i % self.BATCH_SIZE) == 0:
        #     #         o = loader.commit(True)
        #     #     else:
        #     #         o = loader.commit(False)
        #     #
        #     #     node_responses.append(o)
        #     # except Exception:
        #     #     print(f"Error in loading node : {node}")
        #     #     node_responses.append({"ERROR": node.__str__()})

        print("Nodes loaded")
        self.NODES_IN_CASE = status_nodes

        edge_responses = []
        traversal = copy.deepcopy(self.TRAVERSAL)

        edge_batches = list(Commons.chunks(edges, self.BATCH_SIZE))
        for batch in edge_batches:
            for i in range(len(batch)):
                edge = batch[i]

                loader = EdgeLoader(edge, self.UPDATE_EDGE, traversal)
                loader.load()

                if i == len(batch) - 1:
                    o = loader.commit(True)
                else:
                    o = loader.commit(False)
                #
                # if (i % self.BATCH_SIZE) == 0:
                #     o = loader.commit(True)
                # else:
                #     o = loader.commit(False)
                #
                # if i == len(edges) - 1:
                #     o = loader.commit(True)

                edge_responses.append(o)

        print("Edges loaded")

        return {"nodes": node_responses, "edges": edge_responses}


if __name__ == '__main__':
    from gen.graphdb_pb2 import GraphFormat
    from google.protobuf.json_format import MessageToDict
    from utils.constants import APPLICATION_PROPERTIES
    import grpc
    from client.connection.SnowGraphConnection import SnowGraphConnection
    from client.traversal.GraphTraversal import GraphTraversal
    from gen.graphdb_pb2_grpc import ServicesToGraphCoreStub

    data = GraphFormat()
    # f = open("../../resources/dumps/Case_159892_sstech_1544.3858830928802_graph_data.bin", "rb")
    # data.ParseFromString(f.read())
    # f.close()

    print("Read graphformat")

    case_id = data.caseId

    graph_data = MessageToDict(data)

    print("graph format to dict")

    resource_properties = Commons.load_properties(APPLICATION_PROPERTIES)
    core_host = resource_properties["grpc.core.server.host"]
    core_port = int(resource_properties["grpc.core.server.port"])
    url = f'{core_host}:{core_port}'

    core_channel = grpc.insecure_channel(url)
    CORE_CLIENT = ServicesToGraphCoreStub(channel=core_channel)
    print(f"Initialized connection to core client to URL: {url} in constructor")

    print("connected to snowgraph server")

    conn = SnowGraphConnection()
    conn.set_host(core_host)
    conn.set_port(core_port)
    traversal = GraphTraversal(conn)

    print("created traversal")

    loader = GraphLoader(graph_data)
    loader.with_traversal(traversal)
    loader.convert()
    loader.load()

    print("Loaded")
