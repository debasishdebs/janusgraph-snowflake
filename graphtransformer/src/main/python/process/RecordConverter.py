from utils.constants import APPLICATION_PROPERTIES
import json, os
from typing import Dict, List, Union
from utils.DataExtractionUtilities import is_node_empty, is_edge_empty, reformat_left_or_right


class RecordConverter:
    PROPERTIES = None
    sep = '='
    comment_char = '#'
    data_source = None

    def __init__(self, data, ds):
        self.DATA: List[Dict[str, str]] = data
        self._load_properties_()
        self.with_source(ds)

        self.SCHEMA: Dict = self._load_schema_()
        self.MAPPER: Dict[str, Union[str, Dict[str, Dict]]] = self._load_datamapper_()

    def with_source(self, ds):
        self.data_source = ds
        return self

    def _load_properties_(self) -> None:
        props = {}
        with open(APPLICATION_PROPERTIES, "rt") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith(self.comment_char):
                    key_value = l.split(self.sep)
                    key = key_value[0].strip()
                    value = self.sep.join(key_value[1:]).strip().strip('"')
                    props[key] = value
        self.PROPERTIES = props

    def _load_schema_(self) -> Dict:
        schema_file = self.PROPERTIES["graph.schema"] if "graph.schema" in self.PROPERTIES else None
        return json.load(open(schema_file)) if schema_file is not None else {}

    def _load_datamapper_(self) -> Dict[str, Dict[str, Dict]]:
        datamapper_file = self.PROPERTIES[f"graph.{self.data_source}.datamapper"]
        return json.load(open(os.path.abspath(self.PROPERTIES["resource.path"] + datamapper_file))) if datamapper_file != "" else {}

    def _get_value_from_record_using_mapper_(self, record, record_map):

        # default conditions
        if "default=" in record_map:
            value = record_map.split("default=")[1]
            return value

        return self.get_property_value_for_field_from_record(record, record_map)

    def clean_property_from_record(self, record, propMap):
        value = self.get_property_from_map(record, propMap)
        if isinstance(value, str):
            value.replace("\$", "")
        return value

    def get_property_from_map(self, record, propMap):
        """

        Args:
            record (dict):
            propMap (str):

        Returns:

        """

        if "|" in propMap:
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

        elif propMap.isalpha():
            if propMap in record:
                propVal = record[propMap]
            else:
                # print("Couldn't find corresponding key {} in record. Defaulting to ''".format(propMap))
                propVal = ""

        elif propMap in record:
            propVal = record[propMap]

        else:
            if "default" in propMap:
                # When default is provided. It is of format default=something in datamapper
                val = propMap.split("default=")[1]
                propVal = val
            else:
                propVal = ""

        return propVal

    def get_property_value_for_field_from_record(self, record, propMap):
        propVal = None

        if "analyze" not in propMap:
            if "+" in propMap:
                appenders = propMap.split("+")
                propVal = ""
                for appender in appenders:
                    propVal += self.clean_property_from_record(record, appender)

            else:
                propVal = self.clean_property_from_record(record, propMap)

        else:
            if "+" in propMap or "|" in propMap:
                raise NotImplementedError("Currently not implemented mixed mapper containing "
                                          "'analyze' and '|' and '+'")

            else:
                func_map = propMap.split("analyze")[1][1:]
                func_info = self.MAPPER["analyze"][func_map]

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

                if repeat != -1:
                    assert len(ret) == repeat
                    propVal = ret
                else:
                    missing = repeat - len(ret)
                    for i in range(missing):
                        ret.append([])
                    propVal = ret

        return propVal

    def _get_src_dst_value_for_edge_(self, record, map):
        graph_key = map.split("(")[0]
        graph_label = graph_key.split(".")[0]
        graph_property = graph_key.split(".")[1]
        record_key = map.split("(")[1].split(")")[0]

        value = self.get_property_value_for_field_from_record(record, record_key)

        if value is not None:
            if isinstance(value, list):
                return [{"label": graph_label, "property_key": graph_property, "value": value[i]} for i in range(len(value))]
            else:
                return [{"label": graph_label, "property_key": graph_property, "value": value}]

        return None

    def _generate_nodes_(self):
        nodes = []
        for record in self.DATA:
            nodes_in_record = []

            for label, label_map in self.MAPPER["nodes"].items():
                node_for_label = dict()
                list_values = dict()

                mapper = label_map["maps"]
                for graph_key, record_map in mapper.items():
                    value = self._get_value_from_record_using_mapper_(record, record_map)

                    if isinstance(value, list) and len(value) > 1:
                        list_values[graph_key] = value

                    else:
                        if value is not None:
                            node_for_label[graph_key] = value

                nodes_for_label = list()
                if len(list_values) > 1:
                    raise NotImplementedError("Not implemented multiple values for multiple properties in single node")

                if list_values:
                    prop = list(list_values.keys())[0]
                    values = list(list_values.values())[0]
                    for value in values:
                        tmp_node = node_for_label
                        tmp_node.pop(prop)
                        tmp_node[prop] = value

                        if not is_node_empty(tmp_node):
                            nodes_for_label.append(tmp_node)

                if len(node_for_label) > 0:
                    if not is_node_empty(node_for_label):
                        nodes_in_record.append(node_for_label)

            nodes.append(nodes_in_record)

        return nodes

    def _generate_edges_(self):
        edges = []
        for record in self.DATA:
            edges_in_record = []

            for label, label_map in self.MAPPER["edges"].items():
                edge_for_label = dict()

                mapper = label_map["maps"]
                for graph_key, record_map in mapper.items():
                    value = self._get_value_from_record_using_mapper_(record, record_map)

                    if value is not None:
                        edge_for_label[graph_key] = value

                constrains = label_map["constraints"]
                left = self._get_src_dst_value_for_edge_(record, constrains["left"])
                right = self._get_src_dst_value_for_edge_(record, constrains["right"])

                if left is not None and right is not None:
                    # One - Many
                    if len(left) == 1:
                        edges_for_label = list()
                        # If len(right) = 1, its One-One
                        for r in right:
                            tmp_edge = edge_for_label
                            tmp_edge["left"] = reformat_left_or_right(left)
                            tmp_edge["right"] = reformat_left_or_right(r)

                            if not is_edge_empty(tmp_edge):
                                edges_for_label.append(tmp_edge)

                    elif len(right) == 1:
                        edges_for_label = list()
                        # If len(left) = 1, its One-One
                        for l in left:
                            tmp_edge = edge_for_label
                            tmp_edge["left"] = reformat_left_or_right(l)
                            tmp_edge["right"] = reformat_left_or_right(right)

                            if not is_edge_empty(tmp_edge):
                                edges_for_label.append(tmp_edge)
                    else:
                        # Many-Many with one-one among each
                        if len(left) != len(right):
                            raise NotImplementedError("Implemented many-many relation when both left and right len are eq")
                        edges_for_label = list()
                        for i in range(len(left)):
                            tmp_edge = edge_for_label
                            tmp_edge["left"] = reformat_left_or_right(left[i])
                            tmp_edge["right"] = reformat_left_or_right(right[i])

                            if not is_edge_empty(tmp_edge):
                                edges_for_label.append(tmp_edge)

                    edge_for_label["left"] = reformat_left_or_right(left)
                    edge_for_label["right"] = reformat_left_or_right(right)

                else:
                    edges_for_label = []

                for edge in edges_for_label:
                    if len(edge) > 1 and "left" in edge and "right" in edge:
                        if not is_edge_empty(edge):
                            edges_in_record.append(edge)

            edges.append(edges_in_record)

        return edges

    def convert(self):
        if self.data_source is None:
            raise AttributeError("Please set data source before starting conversion")

        nodes = self._generate_nodes_()
        edges = self._generate_edges_()
        graph = {
            "nodes": nodes,
            "edges": edges
        }
        return graph
