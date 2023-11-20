from gen.graphdb_pb2 import Time
from dateutil import parser
from gen.graphdb_pb2 import GeoLocation
import datetime as dt
from gen.graphdb_pb2 import CaseLoadingProperties, StructureValue, GenericStructure, ListValue, CaseNode


# APPLICATION_PROPERTIES = "../../resources/application.properties"
APPLICATION_PROPERTIES = "/app/src/main/resources/application.properties"
TIME_PROPERTIES = ["eventTime", "parsingTime", "datetime", "EventTime", "EventReceivedTime", "emailTime"]
GEO_PROPERTIES = ["srcLocation", "dstLocation"]
BATCH_SIZE = 500
ADD_OR_UPDATE_NODE = True
ADD_OR_UPDATE_EDGE = True


class Commons:
    @staticmethod
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

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
    def time_string_to_time_protobuf(time_str):
        python_time = parser.isoparse(time_str)

        protobuf_time = Time(year=python_time.year, month=python_time.month, day=python_time.day,
                             hour=python_time.hour, minutes=python_time.minute, seconds=python_time.second)

        return protobuf_time

    @staticmethod
    def convert_python_time_to_proto_time(time: dt.datetime):
        # time = parser.parse(time, fuzzy=True)

        t = Time()
        t.year = time.year
        t.month = time.month
        t.day = time.day
        t.hour = time.hour
        t.minutes = time.minute
        t.seconds = time.second
        return t

    @staticmethod
    def protobuf_time_to_datetime(time):
        year = time["year"]
        month = time["month"]
        day = time["day"]
        hour = time["hour"] if "hour" in time else 0
        minutes = time["minute"] if "minute" in time else 0
        second = time["second"] if "second" in time else 0

        return dt.datetime(year=year, month=month, day=day, hour=hour, minute=minutes, second=second)

    @staticmethod
    def geo_string_to_geo_protobuf(geo_str):
        return GeoLocation()

    @staticmethod
    def node_list_to_case_node_iterator(nodes, caseid):
        print("Converting nodes minimal to CaseLoadingProperties")
        print(f"Num nodes are {len(nodes)}")
        for node in nodes:
            node = node["properties"]
            node_id = int(node["node_id"]["stringValue"])
            label = node["node_label"]["stringValue"]
            prop = "ip" if label == "IP" else "userName" if label == "user" else "fileName" if label == "process" else "URL" if label == "URLs" else "emailSubject" if label == "email" else "hostname"
            val = node[prop]["stringValue"]

            g = GenericStructure()
            g.fields["node_id"].CopyFrom(StructureValue(int_value=node_id))
            g.fields["property"].CopyFrom(StructureValue(string_value=prop))
            g.fields["value"].CopyFrom(StructureValue(string_value=val))

            s = StructureValue(struct_value=g)
            n = CaseNode(caseId=caseid, node=s)
            yield n

    @staticmethod
    def node_list_to_update_case_properties(nodes, caseid):
        print("Converting nodes minimal to CaseLoadingProperties")
        print(f"Num nodes are {len(nodes)}")

        nodes_struct_list = []
        for node in nodes:
            node_id = node["node_id"]
            prop = [x for x in node.keys() if x != "node_id"][0]
            val = node[prop]

            g = GenericStructure()
            g.fields["node_id"].CopyFrom(StructureValue(int_value=node_id))
            g.fields["property"].CopyFrom(StructureValue(string_value=prop))
            g.fields["value"].CopyFrom(StructureValue(string_value=val))

            # print("Generic str created")

            s = StructureValue(struct_value=g)
            nodes_struct_list.append(s)
            # print("Struct value appended")

        list_val = ListValue(values=nodes_struct_list)
        # print("List value created")
        node_struct = StructureValue(list_value=list_val)
        print("Final struct value created")

        case = CaseLoadingProperties(caseId=caseid)
        print("Case loading properties created")
        case.property["nodes"].CopyFrom(node_struct)
        print("Copied into caseloading properties")
        return case
