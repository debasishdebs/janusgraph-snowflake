from gen.graphdb_pb2 import ByteCode, InnerMostByteCode, MiddleMostByteCode, ListFormat, GenericStructure
from client.structure.Edge import Edge
from client.structure.Vertex import Vertex
from client.structure.SnowGraph import SnowGraph
import grpc
from client.utils.common_resources import Commons
from gen.graphdb_pb2_grpc import ServicesToGraphCoreStub
from google.protobuf.json_format import MessageToDict


class ExecuteByteCode:
    def __init__(self, byte_code):
        self.byte_code = byte_code

        connection = Commons.get_connection()

        graph_core_port = connection.PORT
        host = connection.HOST

        url = f'{host}:{graph_core_port}'

        MAX_MESSAGE_LENGTH = 100 * 1024 * 1024
        options=[
            ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            ('grpc.max_metadata_size', 10*1024*1024)
        ]
        self.channel = grpc.insecure_channel(url, options=options)

    @staticmethod
    def dump_object(obj):
        return MessageToDict(obj)

    def execute(self):
        bytecode = self._generate_bytecode_()
        results = self._execute_bytecode_(bytecode)

        print("Results are")
        # print(results)
        response = getattr(results, results.WhichOneof('response'))

        field_name = [x for x in response.DESCRIPTOR.fields][0]

        responses = self._parse_result(response, field_name.name)
        print("parsed result")
        graph = self._convert_response_to_graph_(responses)
        print("convertex to snowgraph")

        return graph

    def _convert_response_to_graph_(self, responses):
        vertices = dict()
        edges = dict()
        print("snowgraph conversion started")

        for row in responses:

            src_properties = row["src_properties"] if "src_properties" in row else row["properties"] if "properties" in row else {}

            updated_src_prop = {}
            for prop, val in src_properties.items():
                if prop not in ["node_id", "node_label"]:
                    updated_src_prop[prop] = val

            dst_properties = row["dst_properties"] if "dst_properties" in row else {}
            updated_dst_prop = {}
            for prop, val in dst_properties.items():
                if prop not in ["node_id", "node_label"]:
                    updated_src_prop[prop] = val

            edge_properties = row["value_properties"] if "value_properties" in row else {}
            updated_edge_prop = {}
            for prop, val in edge_properties.items():
                if prop not in ["edge_id", "edge_label"]:
                    updated_src_prop[prop] = val

            src_node = {
                "node_id": row["node_id"] if "node_id" in row else None,
                "label": row["src_label"] if "src_label" in row else row["label"] if "label" in row else None,
                "properties": updated_src_prop
            }
            dst_node = {
                "node_id": row["map_id"] if "map_id" in row else None,
                "label": row["dst_label"] if "dst_label" in row else None,
                "properties": updated_dst_prop
            }
            edge = {
                "edge_id": row["value_id"] if "value_id" in row else None,
                "label": row["value_label"] if "value_label" in row else None,
                "properties": updated_edge_prop,
                "src_id": row["node_id"] if "node_id" in row else None,
                "dst_id": row["map_id"] if "map_id" in row else None
            }

            src_vertex = Vertex(src_node)
            dst_vertex = Vertex(dst_node)
            connection = Edge(edge)

            if src_vertex.is_valid():
                if src_vertex.id() not in vertices:
                    vertices[src_vertex.id()] = src_vertex
                else:
                    src_vertex = vertices[src_vertex.id()]

            if dst_vertex.is_valid():
                if dst_vertex.id() not in vertices:
                    vertices[dst_vertex.id()] = dst_vertex
                else:
                    dst_vertex = vertices[dst_vertex.id()]

            if connection.is_valid():
                src_vertex.add_edge(connection)
                dst_vertex.add_edge(connection)
                if connection.id() not in edges:
                    edges[connection.id()] = connection

        graph = SnowGraph(list(vertices.values()), list(edges.values()))

        return graph

    def _parse_result(self, result, field):

        if str(type(result)) == str(ListFormat):
            print("Parsing listformat")
            # print(result)
            print("parse start")
            return self._parse_list_value_to_list(result)
        else:
            print("parsing mapformat")
            return self._parse_map_value(result, field)

    def _parse_map_value(self, map_val, field):
        dictified = MessageToDict(map_val)[field]

        response = {k: list(v.values()) for k, v in dictified.items()}

        # return {str(k): str(v).strip().split(";")[0].split(":")[1].strip() for k, v in dictified.items()}
        return response

    def _parse_generic_structure_to_python_dict_(self, element):
        item = dict()

        for k, v in element.fields.items():
            value = getattr(v, v.WhichOneof('kind'))
            # if not isinstance(value, GenericStructure):
            if str(type(value)) != str(GenericStructure):
                item[k] = value
            else:
                # item[k] = self._parse_generic_structure_to_python_dict_(MessageToDict(value))
                item[k] = MessageToDict(value)["fields"]
        return item

    def _parse_list_value_to_list(self, list_val):
        values = []
        for row in list_val.rows:
            assert str(type(row)) == str(GenericStructure)

            item = dict()
            for k, v in row.fields.items():
                field = v.WhichOneof('kind')
                if field is not None:
                    value = getattr(v, field)
                    # if not isinstance(value, GenericStructure):
                    if str(type(value)) != str(GenericStructure):
                        item[k] = value
                    else:
                        item[k] = self._parse_generic_structure_to_python_dict_(value)
                        # item[k] = MessageToDict(value)

            values.append(item)
            # for row in val.list_value.values:
            #     key = step_metadata.WhichOneof('kind')
            #     value = getattr(step_metadata, key)
            #     int_vals.append({key: value})
            #
            # values.append(int_vals)

        return values

    def _execute_bytecode_(self, bytecode):

        stub = ServicesToGraphCoreStub(channel=self.channel)
        results = stub.ExecuteByteCode(bytecode)

        return results

    def _generate_bytecode_(self):
        # print("genrating protobuf for")
        # print(self.byte_code)

        # Actual:
        # [[['V'], ['p1', 'v1'], ['as', 'a']], [['outE'], [], ['ep1', 'ep2']], [['inV'], ['T.label', 'v2']], [['inE'], ['T.label', 'e2']], [['outV'], [], ['p2', 'v2'], ['as', 'b']], [['project'], ['by', 'a'], ['by', 'b']]]
        # Expected
        # [[[V], [p1, p2], [as, A]], [[outE, testEdge]], [[inV, label1], [prop1, between(x1, x2)]], [[project], [by, A]]]

        middles = []
        for middle in self.byte_code:
            inner_msgs = []
            # print(f"Middle: {middle}")
            for inner in middle:
                # print(f"Inner: {inner}")

                inner_msg = InnerMostByteCode()

                contains_list = any(isinstance(el, list) for el in inner)
                if contains_list:
                    if inner[0] == "project":
                        inner_msg.inner_values.append(inner[0])
                        inner_msg.inner_values.extend(*inner[1:])

                    else:
                        raise ValueError(f"List inner message is expected only during project but got {inner}")

                else:
                    # print("This is TODO place I need to recheck this ")
                    inner_msg.inner_values.extend(inner)

                inner_msgs.append(inner_msg)

            middle_msg = MiddleMostByteCode()
            middle_msg.middle_layer.extend(inner_msgs)

            middles.append(middle_msg)

        code = ByteCode()
        code.steps.extend(middles)

        # print(code)

        return code

# select a.*, bce.value:properties as b_c_outprop, bce.value:id::string as b_c_id, bce.value:label::string as b_c_label, bce.value:target:id as cID, bce.value:target:label::string as cLabel, bce.value:target as cprop
# from nodes as c,
# lateral(
#     select a.srcId as aId, a.srcLabel as aLabel, a.srcProp as aProp, a.outEdgeProp as a_b_outProp, a.outEdgeLabel::string as a_b_label, a.outEdgeId::string as a_b_Id, a.targetId as bId, a.targetLabel as bLabel, a.targetProp as bProp
# from edges as e ,
#     lateral(select n."NODE_ID" as srcId, n.LABEL as srcLabel, n.PROPERTIES as srcProp, o.value:properties as outEdgeProp, o.value:id as outEdgeId, o.value:label as outEdgeLabel, o.value:target:id as targetId, o.value:target:label::string as targetLabel, o.value:target as targetProp from nodes n, lateral flatten(n."outEdges") o where n.properties:userName='userName_0') as a
# where e.edge_id = to_binary(a_b_Id, 'hex')
# ) as a,
# lateral flatten(c."outEdges") bce
# where a.bprop:id = c.node_id ;

# Select ****** generate based on number of hops required
# Get number of hops. If 2, then nodes as c, if 3 then nodes as d and so on [ from nodes as <> ]
# lateral (goto previous level. If remaining hops == 1 {meaning 2 inc src} then execute inner query as above) else keep adding lateral and select previous level like above select stmt
# close out the innermost query
# keep adding condition as e.edge_id = a_b_id or b_c_id or c_d_id and so on
# by flattening out outEdges
# iterate
# TEST ABOVE
