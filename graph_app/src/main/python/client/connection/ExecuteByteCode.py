from gen.graphdb_pb2 import ByteCode, InnerMostByteCode, MiddleMostByteCode, ListFormat, GenericStructure, ListValue
from client.structure.Edge import Edge
from client.structure.Vertex import Vertex
from client.structure.SnowGraph import SnowGraph
import grpc
import uuid
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
        print(f"Rows: {len(responses)}")
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
            updated_src_prop["lvl"] = row["lvl"]

            dst_properties = row["dst_properties"] if "dst_properties" in row else {}
            updated_dst_prop = {}
            for prop, val in dst_properties.items():
                if prop not in ["node_id", "node_label"]:
                    updated_dst_prop[prop] = val
            updated_dst_prop["lvl"] = row["lvl"]

            edge_properties = row["value_properties"] if "value_properties" in row else {}
            updated_edge_prop = {}
            for prop, val in edge_properties.items():
                if prop not in ["edge_id", "edge_label"]:
                    updated_edge_prop[prop] = val
            updated_edge_prop["lvl"] = row["lvl"]

            src_node = {
                "node_id": row["src_id"] if "src_id" in row else None,
                "label": row["src_label"] if "src_label" in row else row["label"] if "label" in row else None,
                "properties": updated_src_prop,
            }
            dst_node = {
                "node_id": row["dst_id"] if "dst_id" in row else None,
                "label": row["dst_label"] if "dst_label" in row else None,
                "properties": updated_dst_prop
            }
            edge = {
                "edge_id": row["value_id"] if "value_id" in row else uuid.uuid4(),
                "label": row["value_label"],
                "properties": updated_edge_prop,
                "src_id": row["src_id"] if "src_id" in row else None,
                "dst_id": row["dst_id"] if "dst_id" in row else None
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
            if str(type(value)) == str(GenericStructure):
                item[k] = self._parse_generic_structure_to_python_dict_(value)

            elif str(type(value)) == str(ListValue):
                list_vals = []
                for val in value.values:
                    vv = getattr(val, val.WhichOneof('kind'))
                    list_vals.append(vv)
                item[k] = list_vals if len(list_vals) > 1 else list_vals[0]

            else:
                item[k] = value

            # # if not isinstance(value, GenericStructure):
            # if str(type(value)) != str(GenericStructure):
            #     item[k] = value
            # else:
            #     # item[k] = self._parse_generic_structure_to_python_dict_(MessageToDict(value))
            #     item[k] = MessageToDict(value)["fields"]
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
                    if str(type(value)) != str(GenericStructure):
                        item[k] = value
                    else:
                        item[k] = self._parse_generic_structure_to_python_dict_(value)

            values.append(item)
        return values

    def _execute_bytecode_(self, bytecode):

        stub = ServicesToGraphCoreStub(channel=self.channel)
        results = stub.ExecuteByteCode(bytecode)

        return results

    def _generate_bytecode_(self):
        print("genrating protobuf for")
        print(self.byte_code)

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
                print(f"Contains list in gen protobuf {contains_list} for value {inner}")
                if contains_list:
                    if inner[0] == "project":
                        inner_msg.inner_values.append(inner[0])
                        inner_msg.inner_values.extend(*inner[1:])

                    else:
                        raise ValueError(f"List inner message is expected only during project but got {inner}")

                else:
                    print(f"This is TODO place I need to recheck this {inner_msg.inner_values} and value {inner}")
                    if isinstance(inner, list):
                        for i in inner:
                            inner_msg.inner_values.append(i)
                            print(f"Got {inner} and list so iterating over {i} and appending it and got {inner_msg.inner_values}")
                    else:
                        inner_msg.inner_values.append(inner)
                        print(f"Got {inner} as not list so extending it so got {inner_msg.inner_values}")

                inner_msgs.append(inner_msg)

            middle_msg = MiddleMostByteCode()
            middle_msg.middle_layer.extend(inner_msgs)

            middles.append(middle_msg)

        code = ByteCode()
        code.steps.extend(middles)

        print(code)

        return code
