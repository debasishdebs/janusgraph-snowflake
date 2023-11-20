from gen.graphdb_pb2 import Time
from dateutil import parser
from gen.graphdb_pb2 import GraphFormat, Node, Edge
from gen.graphdb_pb2 import StructureValue, ListValue, CaseNode
from gen.graphdb_pb2 import GenericStructure
import datetime as dt
import os, sys
import json


# APPLICATION_PROPERTIES = "../../resources/application.properties"
APPLICATION_PROPERTIES = "/app/src/main/resources/application.properties"
TIME_PROPERTIES = ["eventTime", "parsingTime", "datetime", "EventTime", "EventReceivedTime"]
GEO_PROPERTIES = ["srcLocation", "dstLocation"]
DATAMAPPERS = {}
import random
import uuid


class Commons:

    @staticmethod
    def get_node_id(row_id: int):
        mills_since_epoch = dt.datetime.now().timestamp() * 1000
        random.seed(mills_since_epoch)
        offset = random.randint() + mills_since_epoch
        offset += row_id
        return offset

    @staticmethod
    def get_edge_id(row_id: int):
        mills_since_epoch = int(dt.datetime.now().timestamp() * 10000)
        random.seed(mills_since_epoch)
        upper_range = mills_since_epoch*mills_since_epoch
        max_int = sys.maxsize

        if upper_range > max_int:
            q = int(upper_range/max_int)
            r = int(upper_range % max_int)
            upper_range = q*((q*max_int) + r)
        offset = random.randint(0, upper_range) + mills_since_epoch
        offset += int(row_id)

        while offset >= max_int:
            q = int(offset/max_int)
            r = int(offset % max_int)
            offset = q+r
        offset = int(offset/1000)
        #
        # if offset > max_int:
        #     q = int(offset/max_int)
        #     r = int(offset % max_int)
        #     offset = (q*max_int) + r
        eid = uuid.UUID(int=random.getrandbits(offset))
        return eid

    @staticmethod
    def get_datamapper(ds):
        print(f"Getting datamapper for {ds}")
        if ds not in DATAMAPPERS:
            print(f"DS: {ds} not in datamappers so reading and adding to global list")
            properties = Commons.load_properties(APPLICATION_PROPERTIES)
            print("Read properties file")
            datamapper_file = properties[f"graph.{ds}.datamapper"]
            print("Identified datamapper file name")
            dm = json.load(open(os.path.abspath(properties["resource.path"] + datamapper_file))) if datamapper_file != "" else {}
            print("read in datamapper json")
            DATAMAPPERS[ds] = dm
            print("assigned to datamapper global object")
        print(DATAMAPPERS)
        return DATAMAPPERS[ds]

    INVALID_EDGE_IDENTIFIERS = ["", "-", "NA", "::1", "localhost", ".", "127.0.0.1", "system", "EXCHSRVRTPA03".lower(),
                                "fe80::819f:69f6:ffae:90ca%10", "ff02:0:0:0:0:0:1:2", None, "null", "sstechgcdc01",
                                "administrator"]

    @staticmethod
    def load_properties(filepath, sep='=', comment_char='#'):
        """
        Read the file passed as parameter as a properties file.
        """
        props = {}
        with open(filepath, "rt") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith(comment_char):
                    key_value = l.split(sep)
                    key = key_value[0].strip()
                    value = sep.join(key_value[1:]).strip().strip('"')
                    props[key] = value
        return props

    @staticmethod
    def node_list_to_case_node_iterator(nodes, caseid):
        print("Converting nodes minimal to CaseLoadingProperties")
        print(f"Num nodes are {len(nodes)}")

        for node in nodes:
            node_id = node["node_id"]
            prop = [x for x in node.keys() if x != "node_id"][0]
            val = node[prop]

            g = GenericStructure()
            g.fields["node_id"].CopyFrom(StructureValue(int_value=node_id))
            g.fields["property"].CopyFrom(StructureValue(string_value=prop))
            g.fields["value"].CopyFrom(StructureValue(string_value=val))

            s = StructureValue(struct_value=g)

            n = CaseNode(caseId=caseid, node=s)
            yield n

    @staticmethod
    def convert_graph_dict_to_protobuf_graph(graph, caseid):
        nodes_proto = []
        edges_proto = []

        nodes = graph["nodes"]
        edges = graph["edges"]

        nodes = nodes
        edges = edges

        for node in nodes:
            n = Node()
            for k, v in node.items():
                vv = Commons._convert_value_to_struct_value_(v)
                n.properties[k].CopyFrom(vv)
            nodes_proto.append(n)

        for edge in edges:
            e = Edge()
            for k, v in edge.items():
                vv = Commons._convert_value_to_struct_value_(v)
                e.properties[k].CopyFrom(vv)
            edges_proto.append(e)

        graph_proto = GraphFormat(caseId=caseid, nodes=nodes_proto, edges=edges_proto)
        return graph_proto

    @staticmethod
    def _convert_value_to_struct_value_(v):
        if isinstance(v, str):
            s = StructureValue(string_value=v)
        elif isinstance(v, int):
            s = StructureValue(int_value=v)
        elif isinstance(v, float):
            s = StructureValue(number_value=v)
        elif isinstance(v, dict):
            s = Commons._python_dict_to_proto_generic_struct_value_(v)
            s = StructureValue(struct_value=s)
        elif isinstance(v, list):
            l = ListValue()
            for vv in v:
                ss = Commons._convert_value_to_struct_value_(vv)
                l.values.append(ss)
            s = StructureValue(list_value=l)
        else:
            ERROR = f"Supports only str/int/float/dict in response element type got{type(v)}  " \
                f"for {str(v)}"
            return ERROR
        return s

    @staticmethod
    def _python_dict_to_proto_generic_struct_value_(d: dict):
        value = GenericStructure()
        for k, v in d.items():
            value.fields[k].CopyFrom(Commons._convert_value_to_struct_value_(v))
        return value

    @staticmethod
    def convert_python_time_to_proto_time(time: dt.datetime):
        t = Time()
        t.year = time.year
        t.month = time.month
        t.day = time.day
        t.hour = time.hour
        t.minutes = time.minute
        t.seconds = time.second
        return t

    @staticmethod
    def time_string_to_time_protobuf(time_str):
        python_time = parser.isoparse(time_str)

        protobuf_time = Time(year=python_time.year, month=python_time.month, day=python_time.day,
                             hour=python_time.hour, minutes=python_time.minute, seconds=python_time.second)

        return protobuf_time

    @staticmethod
    def geo_string_to_geo_protobuf(geo_str):
        from gen.graphdb_pb2 import GeoLocation
        return GeoLocation()
