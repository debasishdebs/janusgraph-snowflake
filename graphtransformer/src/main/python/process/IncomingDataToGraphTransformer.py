import datetime as dt
import json
import os
import uuid
from utils.DataExtractionUtilities import is_edge_empty, is_node_empty, reformat_left_or_right, clean_node
from utils.constants import Commons


class IncomingDataToGraphTransformer:
    def __init__(self, data):
        self.DATA = data

        self.WINDOWS_RECORD = []
        self.WATCHGUARD_RECORD = []
        self.MSEXCHANGE_RECORD = []
        self.SYSMON_RECORD = []
        self.SEPC_RECORD = []

        self.DATAMAPPERS = {}
        self.DM = None
        self.ROW_ID = None

        self.EMPTY_EDGES = {}
        self.TOT_EDGES = 0

    def convert(self):
        self._generate_records_per_source_()
        # print("Generated records per source")

        records = self._aggregate_data_across_sources_()
        # print("Aggregated data sources across sources")

        graphs = {}
        for ds, data in records.items():
            print("Executing ", ds)

            graph = self._convert_incoming_record_to_graph_per_ds_(ds, data)
            print(f"For DS: {ds}, data convertec to Graph")
            graphs[ds] = graph

        nodes = [x for d in graphs.values() for row in d["nodes"] for x in row]
        edges = [x for d in graphs.values() for row in d["edges"] for x in row]
        print(f"Number of nodes before deduplicating is {len(nodes)}")
        print(f"Number of edges before deduplicating is {len(edges)}")
        graph = self._merge_graphs_to_single_graph_(graphs)
        print(f"Number of nodes after deduplicating is: {len(graph['nodes'])}")
        print(f"Number of edges after deduplicating is: {len(graph['edges'])}")
        return graph

    def _generate_records_per_source_(self):
        if "windowsRecords" in self.DATA:
            self.WINDOWS_RECORD = self.DATA["windowsRecords"]

        if "exchangeRecords" in self.DATA:
            self.MSEXCHANGE_RECORD = self.DATA["exchangeRecords"]

        if "networkRecords" in self.DATA:
            self.WATCHGUARD_RECORD = self.DATA["networkRecords"]

        if "sysmonRecords" in self.DATA:
            self.SYSMON_RECORD = self.DATA["sysmonRecords"]

        if "sepcRecords" in self.DATA:
            self.SEPC_RECORD = self.DATA["sepcRecords"]
        return self

    def _aggregate_data_across_sources_(self):
        records = {
            "windows": self.WINDOWS_RECORD,
            "msexchange": self.MSEXCHANGE_RECORD,
            "watchguard": self.WATCHGUARD_RECORD,
            "sysmon": self.SYSMON_RECORD,
            "sepc": self.SEPC_RECORD
        }
        return records

    def _convert_incoming_record_to_graph_per_ds_(self, ds, data):
        dm = self.load_datamapper(ds)
        print("Loaded DM")
        print(f"Record size for {ds} is {len(data)}")
        nodes = self.generate_nodes(dm, data, ds)
        print(f"Uniquel labels for {ds} is {set([y['node_label'] for x in nodes for y in x])}")
        print(f"Generated nodes for {ds} of len {sum([len(arr) for arr in nodes])}")
        edges = self.generate_edges(dm, data, ds)
        print(f"Generated edges for {ds} of len {sum([len(arr) for arr in edges])}")
        return {"nodes": nodes, "edges": edges}

    def get_unique_label_for_ds_and_label(self, node, ds):
        label = node["node_label"]
        dm = self.load_datamapper(ds)["nodes"] if self.DATAMAPPERS is {} else self.DATAMAPPERS[ds]["nodes"]
        for type_node, mapper in dm.items():
            node_type = mapper["maps"]["node_label"].split("default=")[1]
            if label.lower() == node_type.lower():
                return mapper["constraints"]["unique"]

    def _merge_graphs_to_single_graph_(self, graphs):
        nodes_global = {}
        edges_global = []
        for ds, graph in graphs.items():
            nodes = graph["nodes"]
            edges = graph["edges"]

            for node_row in nodes:
                for node in node_row:
                    unique_prop = self.get_unique_label_for_ds_and_label(node, ds)
                    # try:
                    unique_val = node[unique_prop]
                    # except KeyError:
                    #     print(node, unique_prop)
                    #     exit(-100)

                    if isinstance(unique_val, str):
                        if unique_val not in nodes_global:
                            nodes_global[unique_val] = node
                    else:
                        assert len(unique_val) == 1
                        if unique_val[0] not in nodes_global:
                            nodes_global[unique_val[0]] = node

            for edge_row in edges:
                for edge in edge_row:
                    # edge_id = edge["edge_id"]
                    # if edge_id not in edges_global:
                    #     edges_global[edge_id] = edge
                    edges_global.append(edge)

        return {"nodes": list(nodes_global.values()), "edges": edges_global}

    def generate_edges(self, dm, data, ds=None):
        edges = []
        print(f"Len of data {len(data)}")
        empty_edges_left = {}
        empty_edges_right = {}
        empty_edges = {}
        skipped = 0
        initial_edge_count = self.TOT_EDGES
        for record in data:
            edges_in_record = []

            for label, label_map in dm["edges"].items():
                edge_for_label = dict()

                mapper = label_map["maps"]
                for graph_key, record_map in mapper.items():
                    try:
                        value = self._get_value_from_record_using_mapper_(record, record_map, dm)
                    except:
                        value = ""
                        print(f"No value found for {record_map} in {record}")

                    if value is not None:
                        edge_for_label[graph_key] = value

                constrains = label_map["constraints"]
                left = self._get_src_dst_value_for_edge_(record, constrains["left"], dm)
                right = self._get_src_dst_value_for_edge_(record, constrains["right"], dm)

                if left is not None and right is not None:
                    # One - Many
                    if len(left) == 1:
                        # print(f"I'm constructing One-Many relations with left: {len(left)} and right: {len(right)}")
                        # print(f"Values left: {left}, right: {right}")
                        edges_for_label = list()
                        # If len(right) = 1, its One-One
                        for r in right:
                            tmp_edge = edge_for_label
                            tmp_edge["left"] = clean_node(reformat_left_or_right(left))
                            tmp_edge["right"] = clean_node(reformat_left_or_right(r))
                            self.TOT_EDGES += 1
                            if not is_edge_empty(tmp_edge):
                                edges_for_label.append(tmp_edge)
                            # else:
                            #     skipped += 1
                            #     left_value = tmp_edge["left"]["value"] if tmp_edge["left"]["value"] in Commons.INVALID_EDGE_IDENTIFIERS else False
                            #     right_value = tmp_edge["right"]["value"] if tmp_edge["right"]["value"] in Commons.INVALID_EDGE_IDENTIFIERS else False
                            #     if left_value != False:
                            #         if left_value not in empty_edges:
                            #             empty_edges[left_value] = []
                            #         empty_edges[left_value].append({"edge": tmp_edge, "record": record})
                            #
                            #         if left_value not in empty_edges_left:
                            #             empty_edges_left[left_value] = []
                            #         empty_edges_left[left_value].append({"edge": tmp_edge, "record": record})
                            #
                            #     if right_value != False:
                            #         if right_value not in empty_edges:
                            #             empty_edges[right_value] = []
                            #         empty_edges[right_value].append({"edge": tmp_edge, "record": record})
                            #
                            #         if right_value not in empty_edges_right:
                            #             empty_edges_right[right_value] = []
                            #         empty_edges_right[right_value].append({"edge": tmp_edge, "record": record})

                    # Many - One
                    elif len(right) == 1:
                        # print(f"I'm constructing Many-One relations with left: {len(left)} and right: {len(right)}")
                        # print(f"Values left: {left}, right: {right}")
                        edges_for_label = list()
                        # If len(left) = 1, its One-One
                        for l in left:
                            tmp_edge = edge_for_label
                            tmp_edge["left"] = clean_node(reformat_left_or_right(l))
                            tmp_edge["right"] = clean_node(reformat_left_or_right(right))
                            self.TOT_EDGES += 1
                            if not is_edge_empty(tmp_edge):
                                edges_for_label.append(tmp_edge)
                            # else:
                            #     skipped += 1
                            #     left_value = tmp_edge["left"]["value"] if tmp_edge["left"]["value"] in Commons.INVALID_EDGE_IDENTIFIERS else False
                            #     right_value = tmp_edge["right"]["value"] if tmp_edge["right"]["value"] in Commons.INVALID_EDGE_IDENTIFIERS else False
                            #     if left_value != False:
                            #         if left_value not in empty_edges:
                            #             empty_edges[left_value] = []
                            #         empty_edges[left_value].append({"edge": tmp_edge, "record": record})
                            #         if left_value not in empty_edges_left:
                            #             empty_edges_left[left_value] = []
                            #         empty_edges_left[left_value].append({"edge": tmp_edge, "record": record})
                            #     if right_value != False:
                            #         if right_value not in empty_edges:
                            #             empty_edges[right_value] = []
                            #         empty_edges[right_value].append({"edge": tmp_edge, "record": record})
                            #         if right_value not in empty_edges_right:
                            #             empty_edges_right[right_value] = []
                            #         empty_edges_right[right_value].append({"edge": tmp_edge, "record": record})

                    else:
                        # print(f"I'm constructing Many-Many relations with left: {len(left)} and right: {len(right)}")
                        # print(f"Values left: {left}, right: {right}")

                        # Many-Many with one-one among each
                        if len(left) != len(right):
                            raise NotImplementedError("Implemented many-many relation when both left and right len are eq")
                        edges_for_label = list()
                        for i in range(len(left)):
                            tmp_edge = edge_for_label
                            tmp_edge["left"] = clean_node(reformat_left_or_right(left[i]))
                            tmp_edge["right"] = clean_node(reformat_left_or_right(right[i]))
                            self.TOT_EDGES += 1
                            if not is_edge_empty(tmp_edge):
                                edges_for_label.append(tmp_edge)
                            # else:
                            #     skipped += 1
                            #     left_value = tmp_edge["left"]["value"] if tmp_edge["left"]["value"] in Commons.INVALID_EDGE_IDENTIFIERS else False
                            #     right_value = tmp_edge["right"]["value"] if tmp_edge["right"]["value"] in Commons.INVALID_EDGE_IDENTIFIERS else False
                            #     if left_value != False:
                            #         if left_value not in empty_edges:
                            #             empty_edges[left_value] = []
                            #         empty_edges[left_value].append({"edge": tmp_edge, "record": record})
                            #         if left_value not in empty_edges_left:
                            #             empty_edges_left[left_value] = []
                            #         empty_edges_left[left_value].append({"edge": tmp_edge, "record": record})
                            #     if right_value != False:
                            #         if right_value not in empty_edges:
                            #             empty_edges[right_value] = []
                            #         empty_edges[right_value].append({"edge": tmp_edge, "record": record})
                            #     if right_value not in empty_edges_right:
                            #         empty_edges_right[right_value] = []
                            #     empty_edges_right[right_value].append({"edge": tmp_edge, "record": record})

                    # print(f"Im outside all conditional statements. Left: {left} and Right: {right}")
                    # edge_for_label["left"] = reformat_left_or_right(left)
                    # edge_for_label["right"] = reformat_left_or_right(right)

                else:
                    edges_for_label = []

                for edge in edges_for_label:
                    if len(edge) > 1 and "left" in edge and "right" in edge:
                        if not is_edge_empty(edge):
                            # edge["edge_id"] = Commons.get_edge_id(self.ROW_ID) if self.ROW_ID is not None else str(uuid.uuid4())
                            # edge["edge_id"] = str(uuid.uuid1(clock_seq=int(self.ROW_ID))) if self.ROW_ID is not None else str(uuid.uuid4())
                            edges_in_record.append(edge)

            if len(edges_in_record) > 0:
                edges.append(edges_in_record)

        # self.EMPTY_EDGES[ds] = empty_edges
        print(f"Total edges : {self.TOT_EDGES}")
        print(f"left empty edge sum: {sum(len(v) for v in empty_edges_left.values())}")
        print(f"right empty edge sum: {sum(len(v) for v in empty_edges_right.values())}")
        print(f"empty edge sum: {sum(len(v) for v in empty_edges_right.values()) + sum(len(v) for v in empty_edges_left.values())}")
        left_dist = [{k: len(v)} for k, v in empty_edges_left.items()]
        right_dist = [{k: len(v)} for k, v in empty_edges_right.items()]
        print(f"Distribution left: {left_dist} and right: {right_dist}")
        print(f"Edges skipped: {skipped}, edges added: {len(edges)} total edges frmed: {self.TOT_EDGES-initial_edge_count} and record size: {len(data)}")

        return edges

    def generate_nodes(self, dm, data, ds=None):
        nodes = []
        t = dt.datetime.now()
        # node_id_base = t.year + t.month + t.day + t.hour + t.minute + t.second + t.microsecond
        idx = 0

        for record in data:
            # print(f"For record {record}")
            nodes_in_record = []

            for label, label_map in dm["nodes"].items():
                # print(f"Starting for label {label} and map {label_map}")

                node_for_label = dict()
                list_values = dict()

                mapper = label_map["maps"]
                # print("for label ", label)
                for graph_key, record_map in mapper.items():
                    # print(f"Get value for key {graph_key} from record {record} using map {record_map}")
                    value = self._get_value_from_record_using_mapper_(record, record_map, dm, ds)
                    # print("Got value as ", value)
                    # if ds == "sysmon":
                    #     print("Key value: ", graph_key, value)
                    # print(graph_key, record_map, value)

                    if isinstance(value, list):
                        if len(value) > 1:
                            vs = []
                            for v in value:
                                if graph_key != "node_label":
                                    vs.append(v.lower() if isinstance(v, str) else v)
                                else:
                                    vs.append(v)
                            list_values[graph_key] = vs
                        else:
                            if graph_key != "node_label":
                                list_values[graph_key] = value[0].lower() if isinstance(value[0], str) else value[0]
                            else:
                                list_values[graph_key] = value[0]

                    else:
                        if value is not None or value != "None" or value != "":
                            if graph_key != "node_label":
                                node_for_label[graph_key] = value.lower() if isinstance(value, str) else value
                            else:
                                node_for_label[graph_key] = value
                # print(f"Generated node ", node_for_label)
                nodes_for_label = list()
                # if len(list_values) > 1:
                #     print(f"Multiple values how? ", list_values)
                #     raise NotImplementedError("Not implemented multiple values for multiple properties in single node")

                if list_values:
                    tmp_node = node_for_label
                    for k, v in list_values.items():
                        prop = k
                        values = v
                        values = values if isinstance(values, list) else [values]
                        # if ds == "sysmon":
                        #     print("Found list values ", values)

                        for value in values:
                            # print("For part list value ", value)
                            if prop in tmp_node:
                                tmp_node.pop(prop)
                            tmp_node[prop] = value

                    if not is_node_empty(tmp_node):
                        nodes_for_label.append(tmp_node)
                    #
                    # print("Found list values ", list_values)
                    # prop = list(list_values.keys())[0]
                    # values = list(list_values.values())[0]
                    # values = values if isinstance(values, list) else [values]
                    # for value in values:
                    #     print("For part list value ", value)
                    #     tmp_node = node_for_label
                    #     if prop in tmp_node:
                    #         tmp_node.pop(prop)
                    #     tmp_node[prop] = value
                    #
                    #     if not is_node_empty(tmp_node):
                    #         print(f"{tmp_node} isn't empty so adding")
                    #         nodes_for_label.append(tmp_node)

                if len(node_for_label) > 0:
                    # print(f"{node_for_label} isn't empty has some keys atleast")
                    if not is_node_empty(node_for_label):
                        # print("The node isn't empty with default keys ref, and adding the index")

                        idx += 1
                        # node_id = node_id_base + idx
                        # node_for_label["node_id"] = node_id

                        nodes_in_record.append(clean_node(node_for_label))

            if len(nodes_in_record) > 0:
                nodes.append(nodes_in_record)

        return nodes

    def with_datamapper(self, dm, ds):
        self.DM = dm
        self.DATAMAPPERS[ds] = dm
        return self

    def for_row_id(self, row_id):
        self.ROW_ID = row_id

    def load_datamapper(self, ds):
        if self.DM is not None:
            return self.DM

        from utils.constants import Commons, APPLICATION_PROPERTIES
        properties = Commons.load_properties(APPLICATION_PROPERTIES)
        datamapper_file = properties[f"graph.{ds}.datamapper"]
        dm = json.load(open(os.path.abspath(properties["resource.path"] + datamapper_file))) if datamapper_file != "" else {}

        if ds not in self.DATAMAPPERS:
            self.DATAMAPPERS[ds] = dm

        return dm

    def _get_value_from_record_using_mapper_(self, record, record_map, dm, ds=None):

        # default conditions
        if "default=" in record_map:
            value = record_map.split("default=")[1]
            return value

        return self._get_property_value_for_field_from_record_(record, record_map, dm, ds)

    def _get_property_value_for_field_from_record_(self, record, propMap, dm, ds=None):
        # if ds == "msexchange":
        #     print(f"For map: {propMap}, from rec: {record}")

        if "analyze" not in propMap:
            if "+" in propMap:
                appenders = propMap.split("+")
                propVal = ""
                for appender in appenders:
                    propVal += self._clean_property_from_record_(record, appender)

            else:
                propVal = self._clean_property_from_record_(record, propMap)

        else:
            if "+" in propMap or "|" in propMap:
                raise NotImplementedError("Currently not implemented mixed mapper containing "
                                          "'analyze' and '|' and '+'")

            else:
                func_map = propMap.split("analyze")[1][1:]
                func_info = dm["analyze"][func_map]

                accessor = func_info["package"]
                params = func_info["params"]
                repeat = func_info["repeat"]

                module_name = accessor.split("&")[0].split("=")[1]
                package_name = accessor.split("&")[1].split("=")[1]

                # This is customization at analyze function and how it is invoked.
                # Cam be direct as
                #   from=utils.DataExtractionUtilities&package=get_ip_for_guardduty_traffic
                # With params:
                #   from=utils.DataExtractionUtilities&package=get_ip_for_guardduty_traffic(param1)
                # With multiple params as well:
                #   from=utils.DataExtractionUtilities&package=get_ip_for_guardduty_traffic(param1|param2|param3)

                func = getattr(__import__(module_name, fromlist=[package_name]), package_name)

                params = params.split("|")
                to_pass = {
                    "params": params,
                    "record": record,
                    "repeat": repeat
                }

                ret = func(**to_pass)

                # if ds == "sysmon":
                #     print(propMap, record, module_name, package_name, ret)

                if repeat != -1:
                    assert len(ret) == repeat
                    propVal = ret
                else:
                    missing = repeat - len(ret)
                    for i in range(missing):
                        ret.append([])
                    propVal = ret

        # if ds == "msexchange":
        #     print("Value is ", propVal)

        return propVal

    def _clean_property_from_record_(self, record, propMap):
        value = self._get_property_from_map_(record, propMap)
        if isinstance(value, str):
            value.replace("\$", "")
        return value

    def _get_property_from_map_(self, record, propMap):
        """

        Args:
            record (dict):
            propMap (str):

        Returns:

        """

        if propMap in record:
            return record[propMap]

        elif propMap == "":
            return ""

        elif "|" in propMap:
            # Or condition property
            maps = propMap.split("|")
            m1 = maps[0]
            m2 = maps[1]
            if m1 in record and m2 in record:
                if record[m1] == record[m2]:
                    propVal = record[m1]
                elif record[m1] in ["-", ""]:
                    propVal = record[m2]
                elif record[m2] in ["-", ""]:
                    propVal = record[m1]
                else:
                    # Give preference to 1st property
                    propVal = record[m1]
            else:
                if m1 in record and m2 not in record:
                    propVal = record[m1]
                elif m2 in record and m1 not in record:
                    propVal = record[m2]
                else:
                    # print("Both {} and {} are missing in record. Defaulting to NA".format(m1, m2))
                    propVal = "NA"

        # TODO: Add "&" support in datamapper
        elif "&" in propMap:
            raise AttributeError("Why would you have & in mapper here? One map is supposed to return 1 value only!!")

        # elif propMap.isalpha():
        #     if propMap in record:
        #         propVal = record[propMap]
        #     else:
        #         # print("Couldn't find corresponding key {} in record. Defaulting to ''".format(propMap))
        #         propVal = ""
        #
        # elif propMap in record:
        #     propVal = record[propMap]

        else:
            if "default" in propMap:
                # When default is provided. It is of format default=something in datamapper
                val = propMap.split("default=")[1]
                propVal = val
            else:
                propVal = ""

        return propVal

    def _get_src_dst_value_for_edge_(self, record, map, dm):
        graph_key = map.split("(")[0]
        graph_label = graph_key.split(".")[0]
        graph_property = graph_key.split(".")[1]
        record_key = map.split("(")[1].split(")")[0]

        value = self._get_property_value_for_field_from_record_(record, record_key, dm)

        if value is not None:
            if isinstance(value, list):
                return [{"label": graph_label, "property_key": graph_property, "value": value[i].lower()} for i in range(len(value))]
            else:
                return [{"label": graph_label, "property_key": graph_property, "value": value.lower()}]

        return None


if __name__ == '__main__':
    from gen.graphdb_pb2 import IncomingDataFormat
    from google.protobuf.json_format import MessageToDict

    data = IncomingDataFormat()
    f = open("../../resources/dumps/Case_159892_sstech_1544.3858830928802_incoming_data.bin", "rb")
    data.ParseFromString(f.read())
    f.close()

    case_id = data.caseId

    data = MessageToDict(data)

    convertor = IncomingDataToGraphTransformer(data)
    graph = convertor.convert()
    nodes = graph["nodes"]
    edges = graph["edges"]
    print(f"Number of nodes in final: {len(nodes)} and len edges: {len(edges)}")

    json.dump(graph, open("../../resources/dumps/Case_159892_sstech_1544.3858830928802_graph_data.json", "w+"), indent=1)

    graph_proto = Commons.convert_graph_dict_to_protobuf_graph(graph, case_id)
    # print(graph_proto.nodes)
    # print("=====XXXXXXXX===========")
    # import pprint
    # pprint.pprint(MessageToDict(graph_proto)["edges"])
    # exit(-1)
    f = open(f"../../resources/dumps/Case_159892_sstech_1544.3858830928802_graph_data.bin", "wb")
    f.write(graph_proto.SerializeToString())
    f.close()
    print("Saved the incoming message as binary")
