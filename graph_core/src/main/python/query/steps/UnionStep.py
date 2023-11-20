from gen.graphdb_pb2 import MiddleMostByteCode, InnerMostByteCode
from typing import List
import pprint
from utils.utils import Utilities as U


class UnionStep(object):
    UNION_FILTER = dict()
    UNION_DIRECTION = dict()
    SELECTION_BY = None
    UNION_QUERY = ""
    ERROR = "NA"
    UNION_VIEW = "union"
    INTERNAL_UNION_STEP_VIEW = "union_step"
    ITERATION_NUM = 1
    CENTRIC_QUERY = None
    NUM_UNION_QUERIES = 1

    def __init__(self, steps: List[MiddleMostByteCode]):
        print(f"Initializing union with {steps} of type {type(steps)}")
        assert type(steps[0]) == MiddleMostByteCode
        self.UNION_STEP = steps
        self.PREVIOUS_VIEW = None
        self.VCI_FILTER: dict = None

        from utils.common_resources import Commons
        self.master = Commons.MASTER_TABLE
        self.edges = Commons.EDGES_TABLE

        print(f"Prev view after initializing UNION step is {self.PREVIOUS_VIEW}")

    def get_selection_step(self):
        return self.SELECTION_BY

    def with_selection_step(self, step):
        print("Here")
        self.SELECTION_BY = step
        print(f"Select by {self.SELECTION_BY}")
        return self

    def execute(self):
        print(f"C: Executing Union step now")

        self._get_total_union_queries_()
        print("Computed the number of union to be run")

        self._get_union_direction_()
        print("Got union direction as ")
        print(self.UNION_DIRECTION)

        self._generate_union_filters_()
        print("Generated union filters")
        pprint.pprint(self.UNION_FILTER)
        print(self.ERROR)
        print(self.PREVIOUS_VIEW)

        self._generate_union_query_()
        print("Generated union query")
        print(self.CENTRIC_QUERY)

        return self

    def _get_total_union_queries_(self):
        print("Getting total union queries")
        print(self.UNION_STEP)
        print(len(self.UNION_STEP))
        self.NUM_UNION_QUERIES = len(self.UNION_STEP)
        return self

    def _generate_union_iteration_query_component_(self, curr_tbl, filter_opts, prev_view=None):
        print("Generating union query comppnnet")
        print("Passed filter options as ", filter_opts)
        print(self.VCI_FILTER)

        prev_view = prev_view if prev_view is not None else self.PREVIOUS_VIEW
        direction = filter_opts["edge"][0]["direction"] if "edges" in filter_opts else filter_opts["vertex"][0]["direction"]

        if self.VCI_FILTER is not None:
            print(f"Pre VCI Filters are {self.VCI_FILTER}")
            print("==========")
            print(filter_opts)

            self.VCI_FILTER["edge_filter"] = \
                {filter_opts["edge"][i]["property"]: ",".join([filter_opts["edge"][i]["predicate"]] + filter_opts["edge"][i]["value"])
                                    if isinstance(filter_opts["edge"][i]["value"], list) else filter_opts["edge"][i]["value"]
                                    if filter_opts["edge"][i]["value"] != "" else ""
                                    for i in range(len(filter_opts["edge"]))}
            self.VCI_FILTER["edge_filter"] = self.VCI_FILTER["edge_filter"] if self.VCI_FILTER["edge_filter"] != {"": ""} else {}

            self.VCI_FILTER["dst_filter"] = \
                {filter_opts["vertex"][i]["property"]: ",".join([filter_opts["vertex"][i]["predicate"]] + filter_opts["vertex"][i]["value"])
                            if isinstance(filter_opts["vertex"][i]["value"], list) else filter_opts["vertex"][i]["value"]
                            if filter_opts["vertex"][i]["value"] != "" else ""
                            for i in range(len(filter_opts["vertex"]))}
            self.VCI_FILTER["dst_filter"] = self.VCI_FILTER["dst_filter"] if self.VCI_FILTER["dst_filter"] != {"": ""} else {}

            print(f"Updated VCI Filters are {self.VCI_FILTER}")
            print(direction)

            if direction == "BOTH":
                select_query = f" select distinct ne.node_id as node_id, ne.map_id as map_id, '1' as lvl, ne.value_id, 'out' as direction, '{curr_tbl}' as tbl, ne.value_label, ne.value_properties    " \
                                   f"\nfrom {self.edges} ne "
                if prev_view is not None:
                    select_query += f"inner join {prev_view} m on " + "{main_out_join_condition}" + "\n{join_query_out}\n {filter} "
                select_query += " \n{join_out} \n{root_filter_out} "

                select_query += "\n\t union all \n"
                select_query += f" select distinct ne.map_id as node_id, ne.node_id as map_id, '1' as lvl, ne.value_id, 'in' as direction, '{curr_tbl}' as tbl, ne.value_label, ne.value_properties    " \
                                    f"\nfrom {self.edges} ne "
                if prev_view is not None:
                    select_query += f"inner join {prev_view} m on " + "{main_in_join_condition}" + "\n{join_query_in}\n {filter} "
                select_query += " \n{join_in} \n{root_filter_in} "

            elif direction == "OUT":
                select_query = f" select distinct ne.node_id as node_id, ne.map_id as map_id, '1' as lvl, ne.value_id, 'out' as direction, '{curr_tbl}' as tbl, ne.value_label, ne.value_properties    " \
                                   f"\nfrom {self.edges} ne "
                if prev_view is not None:
                    select_query += f"inner join {prev_view} m on " + " {main_join_condition}"

                select_query += " \n{join_out} \n{root_filter_out} "

            else:
                select_query = f" select distinct ne.map_id as node_id, ne.node_id as map_id, '1' as lvl, ne.value_id, 'in' as direction, '{curr_tbl}' as tbl, ne.value_label, ne.value_properties   " \
                                   f"\nfrom {self.edges} ne "
                if prev_view is not None:
                        select_query += f"inner join {prev_view} m on " + " {main_join_condition}"
                select_query += " \n{join_in} \n{root_filter_in} "

            filter_dict = U.generate_filter_query_for_condition(self.VCI_FILTER["root_filter"],
                                                                self.VCI_FILTER["edge_filter"],
                                                                self.VCI_FILTER["dst_filter"], direction)

            join_dict = U.generate_join_query_for_condition(direction, self.master, self.VCI_FILTER["root_filter"],
                                                            self.VCI_FILTER["dst_filter"])

            print("The join condition is ")
            print(join_dict)
            print("Select query is ")
            print(select_query)

            if direction == "OUT":
                out_query = filter_dict["OUT"]
                join_query = join_dict["OUT"]
                main_join_condition = "ne.node_id = m.map_id"

                iterate_query = select_query.format(root_filter_out=out_query, join_out=join_query, main_join_condition=main_join_condition)
            elif direction == "IN":
                in_query = filter_dict["IN"]
                join_query = join_dict["IN"]
                main_join_condition = "ne.map_id = m.map_id"

                iterate_query = select_query.format(root_filter_in=in_query, join_in=join_query, main_join_condition=main_join_condition)
            else:
                out_query = filter_dict["OUT"]
                in_query = filter_dict["IN"]
                join_out_query = join_dict["OUT"]
                join_in_query = join_dict["IN"]
                main_join_condition_out = "ne.node_id = m.map_id"
                main_join_condition_in = "ne.map_id = m.map_id"

                iterate_query = select_query.format(root_filter_out=out_query, root_filter_in=in_query, join_in=join_in_query,
                                            join_out=join_out_query, main_out_join_condition=main_join_condition_out, main_in_join_condition=main_join_condition_in)

        else:
            if direction == "OUT":
                select_step = f"select distinct ne.node_id, ne.map_id,  {self.ITERATION_NUM} as lvl, ne.value_id, 'out' as direction, '{curr_tbl}' as tbl, ne.value_label, ne.value_properties   " \
                                  f"from {self.edges} ne "
                if prev_view is not None:
                    select_step += f"inner join {prev_view} m on " + " {main_join_condition}"

                select_step = select_step + "\n {join_query} \n "

            elif direction == "IN":
                select_step = f"select distinct ne.node_id as map_id, ne.map_id as node_id, {self.ITERATION_NUM} as lvl, ne.value_id, 'in' as direction, '{curr_tbl}' as tbl, ne.value_label, ne.value_properties   " \
                                  f"from {self.edges} ne "
                if prev_view is not None:
                    select_step += f"inner join {prev_view} m on " + "{main_join_condition}"

                select_step = select_step + "\n {join_query}\n "

            else:
                select_step = f"select distinct ne.node_id, ne.map_id,  {self.ITERATION_NUM} as lvl, ne.value_id, 'out' as direction, '{curr_tbl}' as tbl, ne.value_label, ne.value_properties   " \
                                  f"from {self.edges} ne "
                if prev_view is not None:
                    select_step += f"inner join {prev_view} m on " + "{main_out_join_condition}" + "\n{join_query_out}\n {filter} "

                select_step += " \n union all \n "

                select_step += f"select distinct ne.map_id as node_id, ne.node_id as map_id, {self.ITERATION_NUM} as lvl, ne.value_id, 'in' as direction, '{curr_tbl}' as tbl, ne.value_label, ne.value_properties   " \
                                   f"from {self.edges} ne "
                if prev_view is not None:
                    select_step += f"inner join {prev_view} m on " + "{main_in_join_condition}" + "\n{join_query_in}\n {filter} "

            edge_filter_props = []
            edge_filter_vals = []
            edge_filter_predicates = []
            if "edge" in filter_opts:
                for edge_filter in filter_opts["edge"]:
                    edge_filter_props.append(edge_filter["property"] if edge_filter["property"] is not "" else None)
                    edge_filter_vals.append(edge_filter["value"] if edge_filter["value"] is not "" else None)
                    edge_filter_predicates.append(edge_filter["predicate"] if edge_filter["predicate"] is not "" else None)

            vertex_filter_props = []
            vertex_filter_vals = []
            vertex_filter_predicates = []
            if "vertex" in filter_opts:
                for vertex_filter in filter_opts["vertex"]:
                    vertex_filter_props.append(vertex_filter["property"] if vertex_filter["property"] is not "" else None)
                    vertex_filter_vals.append(vertex_filter["value"] if vertex_filter["value"] is not "" else None)
                    vertex_filter_predicates.append(vertex_filter["predicate"] if vertex_filter["predicate"] is not "" else None)

            print("Vertex filter ", vertex_filter_props, vertex_filter_vals, vertex_filter_predicates)
            print("Edge filter ", edge_filter_props, edge_filter_vals, edge_filter_predicates)

            filter_query = ""
            for i in range(len(edge_filter_props)):
                edge_filter_prop = edge_filter_props[i]
                edge_filter_val = edge_filter_vals[i]
                edge_filter_predicate = edge_filter_predicates[i]

                time_condition = "time" == edge_filter_val[0] if edge_filter_val is not None else False
                if time_condition:
                    print("There is time condition in edge filter in traversal")
                    edge_filter_val = edge_filter_val[1:]

                if (edge_filter_prop is not None and edge_filter_val is not None) and (edge_filter_prop != "" and edge_filter_val != ""):
                    filter_prefix = " where " if filter_query is "" else " and "

                    if edge_filter_prop == "label":
                        property_ = "ne.value_label"
                    elif edge_filter_prop == "id":
                        property_ = "ne.value_id"
                    else:
                        property_ = f" get(ne.value_properties:\"{edge_filter_prop}\", 0)"
                        if time_condition:
                            property_ = property_ + "::datetime"

                    if edge_filter_predicate == "eq":
                        edge_filter = f" {filter_prefix} {property_} = '{edge_filter_val}' "
                    elif edge_filter_predicate == "gt":
                        edge_filter = f" {filter_prefix} {property_} > '{edge_filter_val}' "
                    elif edge_filter_predicate == "gte":
                        edge_filter = f" {filter_prefix} {property_} >= '{edge_filter_val}' "
                    elif edge_filter_predicate == "lt":
                        edge_filter = f" {filter_prefix} {property_} < '{edge_filter_val}' "
                    elif edge_filter_predicate == "lte":
                        edge_filter = f" {filter_prefix} {property_} <= '{edge_filter_val}' "
                    elif edge_filter_predicate == "between":
                        print("Asserting value if of type list for between predicate")
                        assert type(edge_filter_val) == list
                        if time_condition:
                            edge_filter = f" {filter_prefix} {property_} >= '{edge_filter_val[0]}'::datetime and {property_} <= '{edge_filter_val[1]}'::datetime "
                        else:
                            edge_filter = f" {filter_prefix} {property_} between '{edge_filter_val[0]}' and '{edge_filter_val[1]}' "
                    elif edge_filter_predicate == "within":
                        print("Asserting value if of type list for within predicate")
                        assert type(edge_filter_val) == list
                        query_value = [f"'{x}'" for x in edge_filter_val]
                        edge_filter = f" {filter_prefix} {property_} in ({','.join(query_value)}) "
                    else:
                        print("Predicates supported are between/within/gte/lte/gt/lt/eq for edge but got " + edge_filter_predicate)
                        raise Exception()

                    filter_query += edge_filter

            for i in range(len(vertex_filter_props)):
                vertex_filter_prop = vertex_filter_props[i]
                vertex_filter_val = vertex_filter_vals[i]
                vertex_filter_predicate = vertex_filter_predicates[i]

                time_condition = "time" == vertex_filter_val[0] if vertex_filter_val is not None else False
                if time_condition:
                    print("There is time condition in vertex filter in traversal")
                    vertex_filter_val = vertex_filter_val[1:]

                if (vertex_filter_prop is not None and vertex_filter_val is not None) and (vertex_filter_prop != "" and vertex_filter_val != ""):
                    filter_prefix = " where " if filter_query is None else " and "

                    if vertex_filter_prop == "label":
                        property_ = "nm.label"
                    elif vertex_filter_prop == "id":
                        property_ = "nm.node_id"
                    else:
                        property_ = f" get(nm.properties:\"{vertex_filter_prop}\", 0)"
                        if time_condition:
                            property_ = property_ + "::datetime"

                    if vertex_filter_predicate == "eq":
                        if time_condition:
                            vertex_filter = f" {filter_prefix} {property_} = '{vertex_filter_val}'::datetime "
                        else:
                            vertex_filter = f" {filter_prefix} {property_} = '{vertex_filter_val}' "
                    elif vertex_filter_predicate == "gt":
                        vertex_filter = f" {filter_prefix} {property_} > '{vertex_filter_val}' "
                    elif vertex_filter_predicate == "gte":
                        vertex_filter = f" {filter_prefix} {property_} >= '{vertex_filter_val}' "
                    elif vertex_filter_predicate == "lt":
                        vertex_filter = f" {filter_prefix} {property_} < '{vertex_filter_val}' "
                    elif vertex_filter_predicate == "lte":
                        vertex_filter = f" {filter_prefix} {property_} <= '{vertex_filter_val}' "
                    elif vertex_filter_predicate == "between":
                        print("Asserting value if of type list for between predicate")
                        assert type(vertex_filter_val) == list
                        if time_condition:
                            vertex_filter = f" {filter_prefix} {property_} >= '{vertex_filter_val[0]}'::datetime and {property_} <= '{vertex_filter_val[1]}'::datetime "
                        else:
                            vertex_filter = f" {filter_prefix} {property_} between '{vertex_filter_val[0]}' and '{vertex_filter_val[1]}' "
                    elif vertex_filter_predicate == "within":
                        print("Asserting value if of type list for within predicate")
                        assert type(vertex_filter_val) == list
                        query_value = [f"'{x}'" for x in vertex_filter_val]
                        vertex_filter = f" {filter_prefix} {property_} in ({','.join(query_value)}) "
                    else:
                        print("Predicates supported are between/within/gte/lte/gt/lt/eq for vertex but got " + vertex_filter_predicate)
                        raise Exception()

                    filter_query += vertex_filter

            if direction == "OUT":
                join_step = ""
                if "vertex" in filter_opts:
                    join_step += f" inner join {self.master} nm on nm.node_id = ne.map_id "
                # join_step += " \n where (ne.node_id = m.map_id and ne.map_id != m.node_id) \n"

                join_info = {direction: join_step}
                main_join_condition = {direction: "ne.node_id = m.map_id and ne.map_id != m.node_id"}
                print("TODO to EDIT in Line 235 UnionStep")
                main_join_condition = {direction: "ne.node_id = m.map_id"}

            elif direction == "IN":
                join_step = ""
                if "vertex" in filter_opts:
                    join_step += f" inner join {self.master} nm on nm.node_id = ne.node_id "
                # join_step += " \n where (ne.map_id = m.map_id and ne.node_id != m.node_id) \n"

                join_info = {direction: join_step}
                print("TODO to EDIT in Line 245 UnionStep")
                main_join_condition = {direction: "ne.map_id = m.map_id and ne.node_id != m.node_id"}
                main_join_condition = {direction: "ne.map_id = m.map_id"}

            else:
                join_step = ""
                if "vertex" in filter_opts:
                    join_step += f" inner join {self.master} nm on nm.node_id = ne.map_id "
                # join_step += " \n where (ne.node_id = m.map_id and ne.map_id != m.node_id) \n"
                join_info = {"OUT": join_step}
                main_join_condition = {"OUT": "ne.node_id = m.map_id and ne.map_id != m.node_id"}
                main_join_condition = {"OUT": "ne.node_id = m.map_id"}

                join_step = ""
                if "vertex" in filter_opts:
                    join_step += f" inner join {self.master} nm on nm.node_id = ne.node_id "
                # join_step += " \n where (ne.map_id = m.map_id and ne.node_id != m.node_id) \n"
                join_info["IN"] = join_step
                print("TODO to EDIT in Line 262 UnionStep")
                main_join_condition["IN"] = "ne.map_id = m.map_id and ne.node_id != m.node_id"
                main_join_condition["IN"] = "ne.map_id = m.map_id"

            if direction in ["OUT", "IN"]:
                iterate_query = select_step.format(join_query=join_info[direction],
                                                   main_join_condition=main_join_condition[direction])
                iterate_query += filter_query
            else:
                in_join_query = join_info["IN"]
                out_join_query = join_info["OUT"]
                main_in_join = main_join_condition["IN"]
                main_out_join = main_join_condition["OUT"]
                iterate_query = select_step.format(join_query_in=in_join_query, join_query_out=out_join_query,
                                                   filter=filter_query, main_in_join_condition=main_in_join,
                                                   main_out_join_condition=main_out_join)


        # final_query = select_query + from_query + join_query + filter_query
        final_query = iterate_query

        return final_query

    def _generate_union_iteration_query_component_old_(self, curr_tbl, filter_opts, prev_view=None):
        prev_view = prev_view if prev_view is not None else self.PREVIOUS_VIEW if self.PREVIOUS_VIEW is not None else "main"

        direction = filter_opts["edge"][0]["direction"] if "edges" in filter_opts else filter_opts["vertex"][0]["direction"]

        select_query = f" select ne.node_id, ne.map_id, {self.ITERATION_NUM} as lvl, '{curr_tbl}' as tbl, ne.value_id "
        from_query = f" from {prev_view} l "

        if direction == "OUT":
            join_query = f" inner join {self.edges} ne on ne.node_id = l.map_id "
        elif direction == "IN":
            join_query = f" inner join {self.edges} ne on ne.map_id = l.node_id "
        else:
            join_query = f" inner join {self.edges} ne on (ne.node_id = l.map_id) or (ne.map_id = l.node_id) "
        join_query += f" inner join {self.master} nm on nm.node_id = ne.node_id "

        edge_filter_props = []
        edge_filter_vals = []
        edge_filter_predicates = []
        if "edge" in filter_opts:
            for edge_filter in filter_opts["edge"]:
                edge_filter_props.append(edge_filter["property"] if edge_filter["property"] is not "" else None)
                edge_filter_vals.append(edge_filter["value"] if edge_filter["value"] is not "" else None)
                edge_filter_predicates.append(edge_filter["predicate"] if edge_filter["predicate"] is not "" else None)

        vertex_filter_props = []
        vertex_filter_vals = []
        vertex_filter_predicates = []
        if "vertex" in filter_opts:
            for vertex_filter in filter_opts["vertex"]:
                vertex_filter_props.append(vertex_filter["property"] if vertex_filter["property"] is not "" else None)
                vertex_filter_vals.append(vertex_filter["value"] if vertex_filter["value"] is not "" else None)
                vertex_filter_predicates.append(vertex_filter["predicate"] if vertex_filter["predicate"] is not "" else None)

        filter_query = ""
        for i in range(len(edge_filter_props)):
            edge_filter_prop = edge_filter_props[i]
            edge_filter_val = edge_filter_vals[i]
            edge_filter_predicate = edge_filter_predicates[i]

            time_condition = "time" == edge_filter_val[0] if edge_filter_val is not None else False
            if time_condition:
                print("There is time condition in edge filter in traversal")
                edge_filter_val = edge_filter_val[1:]

            if (edge_filter_prop is not None and edge_filter_val is not None) and (edge_filter_prop != "" and edge_filter_val != ""):
                filter_prefix = " where " if filter_query is "" else " and "

                if edge_filter_prop == "label":
                    property_ = "ne.value_label"
                elif edge_filter_prop == "id":
                    property_ = "ne.value_id"
                else:
                    property_ = f" get(ne.value_properties:\"{edge_filter_prop}\", 0)"
                    if time_condition:
                        property_ = property_ + "::datetime"

                if edge_filter_predicate == "eq":
                    edge_filter = f" {filter_prefix} {property_} = '{edge_filter_val}' "
                elif edge_filter_predicate == "gt":
                    edge_filter = f" {filter_prefix} {property_} > '{edge_filter_val}' "
                elif edge_filter_predicate == "gte":
                    edge_filter = f" {filter_prefix} {property_} >= '{edge_filter_val}' "
                elif edge_filter_predicate == "lt":
                    edge_filter = f" {filter_prefix} {property_} < '{edge_filter_val}' "
                elif edge_filter_predicate == "lte":
                    edge_filter = f" {filter_prefix} {property_} <= '{edge_filter_val}' "
                elif edge_filter_predicate == "between":
                    print("Asserting value if of type list for between predicate")
                    assert type(edge_filter_val) == list

                    if time_condition:
                        edge_filter = f" {filter_prefix} {property_} >= '{edge_filter_val[0]}'::datetime and {property_} <= '{edge_filter_val[1]}'::datetime "
                    else:
                        edge_filter = f" {filter_prefix} {property_} between '{edge_filter_val[0]}' and '{edge_filter_val[1]}' "
                elif edge_filter_predicate == "within":
                    print("Asserting value if of type list for within predicate")
                    assert type(edge_filter_val) == list
                    query_value = [f"'{x}'" for x in edge_filter_val]
                    edge_filter = f" {filter_prefix} {property_} in ({','.join(query_value)}) "
                else:
                    print("Predicates supported are between/within/gte/lte/gt/lt/eq for edge but got " + edge_filter_predicate)
                    raise Exception()

                filter_query += edge_filter

        for i in range(len(vertex_filter_props)):
            vertex_filter_prop = vertex_filter_props[i]
            vertex_filter_val = vertex_filter_vals[i]
            vertex_filter_predicate = vertex_filter_predicates[i]

            time_condition = "time" == vertex_filter_val[0] if vertex_filter_val is not None else False
            if time_condition:
                print("There is time condition in vertex filter in traversal")
                vertex_filter_val = vertex_filter_val[1:]

            if (vertex_filter_prop is not None and vertex_filter_val is not None) and (vertex_filter_prop != "" and vertex_filter_val != ""):
                filter_prefix = " where " if filter_query is None else " and "

                if vertex_filter_prop == "label":
                    property_ = "nm.label"
                elif vertex_filter_prop == "id":
                    property_ = "nm.node_id"
                else:
                    property_ = f" get(nm.properties:\"{vertex_filter_prop}\", 0)"
                    if time_condition:
                        property_ = property_ + "::datetime"

                if vertex_filter_predicate == "eq":
                    vertex_filter = f" {filter_prefix} {property_} = '{vertex_filter_val}' "
                elif vertex_filter_predicate == "gt":
                    vertex_filter = f" {filter_prefix} {property_} > '{vertex_filter_val}' "
                elif vertex_filter_predicate == "gte":
                    vertex_filter = f" {filter_prefix} {property_} >= '{vertex_filter_val}' "
                elif vertex_filter_predicate == "lt":
                    vertex_filter = f" {filter_prefix} {property_} < '{vertex_filter_val}' "
                elif vertex_filter_predicate == "lte":
                    vertex_filter = f" {filter_prefix} {property_} <= '{vertex_filter_val}' "
                elif vertex_filter_predicate == "between":
                    print("Asserting value if of type list for between predicate")
                    assert type(vertex_filter_val) == list
                    if time_condition:
                        vertex_filter = f" {filter_prefix} {property_} >= '{vertex_filter_val[0]}'::datetime and {property_} <= '{vertex_filter_val[1]}'::datetime "
                    else:
                        vertex_filter = f" {filter_prefix} {property_} between '{vertex_filter_val[0]}' and '{vertex_filter_val[1]}' "
                elif vertex_filter_predicate == "within":
                    print("Asserting value if of type list for within predicate")
                    assert type(vertex_filter_val) == list
                    query_value = [f"'{x}'" for x in vertex_filter_val]
                    vertex_filter = f" {filter_prefix} {property_} in ({','.join(query_value)}) "
                else:
                    print("Predicates supported are between/within/gte/lte/gt/lt/eq for vertex but got " + vertex_filter_predicate)
                    raise Exception()

                filter_query += vertex_filter

        final_query = select_query + from_query + join_query + filter_query

        return final_query
    #
    # def case_query_gen(self, views, prev_query=""):
    #     view = views[0]
    #
    #     query = f" case (select count(*) from {self.INTERNAL_COALESCE_STEP_VIEW} c where c.tbl = '{view}') > 0 "
    #     true_query = f" when true then '{view}' "
    #     if len(views) != 1:
    #         else_query = " else \n"
    #     else:
    #         else_query = " else ''\n "
    #
    #     if len(views) == 1:
    #         final_query = prev_query + query + true_query + else_query + "end"
    #         return final_query
    #     else:
    #         final_query = prev_query + query + true_query + else_query
    #         down_query = self.case_query_gen(views[1:], final_query)
    #         return down_query + " end "

    def _generate_union_query_(self):
        print("Generating filter query for union step")

        query_skeleton = f" with {self.INTERNAL_UNION_STEP_VIEW} as \n ( \n " + " {stepQuery} \n ) " + " {unionCondition} " + " \n "

        print(query_skeleton)
        print(f"Previous view is {self.PREVIOUS_VIEW}")
        print(f"VCI Filters are {self.VCI_FILTER}")

        # Generate Union Step Query which basically iterates over the traversal passed
        union_step_queries = []
        union_step_views = []
        for idx, filter_dict in self.UNION_FILTER.items():
            if len(filter_dict) == 1:
                print(f"Generating query for idx: {idx} and filter: {filter_dict} for 1 hop traversal inside union and prev view {self.PREVIOUS_VIEW}")

                filter_opts = filter_dict[1]
                prev_view = self.PREVIOUS_VIEW
                curr_view = f"step{idx}"

                internal_union_query = self._generate_union_iteration_query_component_(curr_view, filter_opts, prev_view)

                if idx == 1:
                    query = f" with {curr_view} as \n ( \n {internal_union_query} \n ) "
                else:
                    query = f" {curr_view} as \n ( \n {internal_union_query} \n ) "

                union_step_queries.append(query)

                # self.PREVIOUS_VIEW = curr_view
                print(f"Initialized prev view as {curr_view} inside 1 hop union traversal")
                print("The query generated is ", query)

                query_for_union_step = query

                if curr_view not in union_step_views:
                    union_step_views.append(curr_view)

            else:
                print(f"Generating query for idx: {idx} and filter: {filter_dict} for > 1 hop traversal inside union and prev view {self.PREVIOUS_VIEW}")

                multi_level_union_queries = []
                curr_top_view = f"step{idx}"

                vci_filter = self.VCI_FILTER

                for lvl, filter_opts in filter_dict.items():
                    print(f"Generating query for idx: {idx} and lvl: {lvl} and filter: {filter_opts}")

                    prev_view = self.PREVIOUS_VIEW
                    curr_local_view = f"ul{lvl}"

                    internal_union_query = self._generate_union_iteration_query_component_(curr_top_view, filter_opts, prev_view)

                    if lvl == 1:
                        query = f" with {curr_local_view} as \n ( \n {internal_union_query} \n ) "
                    else:
                        query = f" {curr_local_view} as \n ( \n {internal_union_query} \n ) "

                    multi_level_union_queries.append(query)
                    self.PREVIOUS_VIEW = curr_local_view
                    self.VCI_FILTER = None
                    print(f"Initialized prev view as {curr_local_view} inside > 1 hop union traversal for hop no {lvl}")
                    print("The query generated is ", query)

                self.VCI_FILTER = vci_filter

                multi_union_iteration_query = ",\n".join(multi_level_union_queries)
                final_select_query = f"\n select * from {self.PREVIOUS_VIEW} "

                query_for_multi_union_step = multi_union_iteration_query + final_select_query

                if curr_top_view not in union_step_views:
                    union_step_views.append(curr_top_view)

                if idx == 1:
                    query_for_union_step = f" with {curr_top_view} as \n ( \n {query_for_multi_union_step} \n ) "
                else:
                    query_for_union_step = f" {curr_top_view} as \n ( \n {query_for_multi_union_step} \n ) "

                self.PREVIOUS_VIEW = curr_top_view
                print("TODO: Change in line 597 in UnionStep")
                self.PREVIOUS_VIEW = None
                print(f"Initialized prev view as {curr_top_view} inside < 1 hop union traversal after all hops are executed")

            if query_for_union_step not in union_step_queries:
                union_step_queries.append(query_for_union_step)

        print("All queries of iteration for union in list")
        print(union_step_queries)

        print("The views are ", union_step_views)

        union_step_select_queries = []
        for view in union_step_views:
            query = f"\n select * from {view} "
            union_step_select_queries.append(query)
        union_step_select_query = "\n union all ".join(union_step_select_queries)

        union_iterative_query = ",\n".join(union_step_queries)

        union_step_query = union_iterative_query + union_step_select_query

        # Not generate the coalesce condition to help me choose the traversal to select.
        # If all are true, the 1st element is selected
        # If all are false, its null set
        # Others, the 1st valid result set is returned

        col_select_query = f" select node_id, map_id, lvl, value_id, direction, value_label, value_properties   from {self.INTERNAL_UNION_STEP_VIEW} "

        print("Generating union case condition for views " , union_step_views)
        #
        # union_select_queries = []
        # for view in union_step_views:
        #     q = f" \n select node_id, map_id, lvl from {view} "
        #     union_select_queries.append(q)
        #
        # col_select_query = "\n union all ".join(union_select_queries)
        # union_case_condition = self.case_query_gen(union_step_views)
        # col_select_query = f"{col_select_query} ({union_case_condition}) "

        union_query = query_skeleton.format(stepQuery=union_step_query, unionCondition=col_select_query)
        print(union_query)
        print("============")

        if self.ITERATION_NUM == 1:
            final_query = f" with {self.UNION_VIEW} as \n ( \n {union_query} )\n "
        else:
            final_query = f" {self.UNION_VIEW} as \n ( \n {union_query} )\n "

        print("Hardcoding in line 634 TODO for UnionStep")
        if self.UNION_VIEW == "root":
            final_query += "\nselect * from root \n"

        self.UNION_QUERY = final_query

        return final_query

    def _generate_filter_for_traversal_step_(self, traversal, direction):
        traversal_filter = {}
        print(len(traversal))
        if len(traversal) == 2:
            edge_step = traversal[0]
            vertex_step = traversal[1]

            assert type(edge_step) == InnerMostByteCode and type(vertex_step) == InnerMostByteCode
            assert len(edge_step.inner_values) >= 1 and len(vertex_step.inner_values) >= 1

            edge_step = edge_step.inner_values
            vertex_step = vertex_step.inner_values

            edge_filter_values = edge_step[1:]
            edge_filters = []
            for j in range(0, len(edge_filter_values), 2):
                propname = edge_filter_values[j]
                propname = propname if "T." not in propname else propname.split("T.")[1]

                propval = edge_filter_values[j+1]
                value_step = propval.split(",")
                print("inside gen filter ", propval, value_step, len(value_step))
                if len(value_step) == 1:
                    predicate = "eq"
                    value = value_step[0]
                else:
                    print("non eq predcate")
                    predicate = value_step[0]
                    print(predicate)
                    value = value_step[1:]
                    print(value)
                    if len(value) == 1 and predicate not in ("within", "between"):
                        value = value[0]

                filter = {
                    "direction": direction,
                    "property": propname,
                    "value": value,
                    "predicate": predicate
                }
                print("filter ", filter)
                edge_filters.append(filter)
                print("edge filters ", edge_filters)

            print("vertex filter gen")
            vertex_filter_values = vertex_step[1:]
            vertex_filters = []
            print(len(vertex_filter_values), vertex_filter_values)
            for j in range(0, len(vertex_filter_values), 2):
                print(j)
                propname = vertex_filter_values[j]
                propname = propname if "T." not in propname else propname.split("T.")[1]
                print("propname", propname, vertex_filter_values, j)

                propval = vertex_filter_values[j+1]
                value_step = propval.split(",")
                if len(value_step) == 1:
                    predicate = "eq"
                    value = value_step[0]
                else:
                    predicate = value_step[0]
                    value = value_step[1:]
                    if len(value) == 1 and predicate not in ("within", "between"):
                        value = value[0]

                filter = {
                    "direction": direction,
                    "property": propname,
                    "value": value,
                    "predicate": predicate
                }
                vertex_filters.append(filter)

            traversal_filter["edge"] = edge_filters
            traversal_filter["vertex"] = vertex_filters

        elif len(traversal) == 1:
            edge_step = traversal[0]

            print("!")
            edge_step = edge_step.inner_values
            print("@")

            edge_filter_values = edge_step[1:]
            print("#")
            edge_filters = []
            for j in range(0, len(edge_filter_values), 2):
                print(f"%-{j}")
                propname = edge_filter_values[j]
                print("^")
                propname = propname if "T." not in propname else propname.split("T.")[1]
                print(f"&-{j}, {len(edge_filter_values)}, {edge_filter_values}")
                propval = edge_filter_values[j+1]
                print(f"*-{j}")
                value_step = propval.split(",")
                if len(value_step) == 1:
                    predicate = "eq"
                    value = value_step[0]
                else:
                    predicate = value_step[0]
                    value = value_step[1:]

                filter = {
                    "direction": direction,
                    "property": propname,
                    "value": value,
                    "predicate": predicate
                }
                edge_filters.append(filter)

            traversal_filter["edge"] = edge_filters

        else:
            print(traversal[0].inner_values)
            vertex_step = traversal[1]
            print("!")
            vertex_step = vertex_step.inner_values
            print("@")

            vertex_filter_values = vertex_step[1:]
            print("#")
            vertex_filters = []
            for j in range(0, len(vertex_filter_values), 2):
                print(f"%-{j}")
                propname = vertex_filter_values[j]
                print("^")
                propname = propname if "T." not in propname else propname.split("T.")[1]
                print(f"&-{j}, {len(vertex_filter_values)}, {vertex_filter_values}")
                propval = vertex_filter_values[j+1]
                print(f"*-{j}")
                value_step = propval.split(",")
                if len(value_step) == 1:
                    predicate = "eq"
                    value = value_step[0]
                else:
                    predicate = value_step[0]
                    value = value_step[1:]

                filter = {
                    "direction": direction,
                    "property": propname,
                    "value": value,
                    "predicate": predicate
                }
                vertex_filters.append(filter)

            traversal_filter["vertex"] = vertex_filters

        return traversal_filter

    def _generate_union_filters_(self):
        for i in range(self.NUM_UNION_QUERIES):
            traversal = self.UNION_STEP[i].middle_layer[1:]
            print(f"Len traversal is {len(traversal)}")
            print(f"Generating filter for {traversal}")

            if 1 <= len(traversal) < 3:
                direction = self._get_traversal_step_direction_(traversal)
                print("Going to generate filter ")
                traversal_filter = self._generate_filter_for_traversal_step_(traversal, direction)
                print(self.UNION_FILTER, len(self.UNION_FILTER))
                self.UNION_FILTER[i+1] = {1: traversal_filter}

            else:
                self.ERROR = "Logically, the traversal (union) should have been split, and we should have got < 3 elements inside"
                print("Traversal was >= 3" + self.ERROR)
                condensed_steps = self._condense_steps_(traversal)

                level_filter = {}
                for k in range(len(condensed_steps)):
                    step = condensed_steps[k]
                    direction = self._get_traversal_step_direction_(step)
                    traversal_filter = self._generate_filter_for_traversal_step_(step, direction)
                    level_filter[k+1] = traversal_filter

                self.UNION_FILTER[i+1] = level_filter

        return self

    def _condense_steps_(self, traversals):
        steps = []
        i = 0
        while i < len(traversals):
            step = traversals[i]
            traversal_step = step.inner_values[0]

            if traversal_step in ["inE", "outE", "bothE"]:
                curr_step = step
                next_step = traversals[i+1]
                i += 2
                steps.append([curr_step, next_step])
            elif traversal_step in ["in", "out", "both"]:
                steps.append([step])
                i += 1
            else:
                raise ValueError(f"Invalid step {traversal_step} encountered while condensing")

        return steps

    def _get_traversal_step_direction_(self, traversal):
        assert type(traversal) == list

        direction = traversal[0].inner_values[0]

        if direction == "out" or direction == "outE":
            return "OUT"
        elif direction == "in" or direction == "inE":
            return "IN"
        else:
            return "BOTH"

    def _get_union_direction_(self):
        for i in range(self.NUM_UNION_QUERIES):
            traversal = self.UNION_STEP[i].middle_layer[1]
            direction = traversal.inner_values[0]

            if direction == "out" or direction == "outE":
                self.UNION_DIRECTION[i+1] = "OUT"
            elif direction == "in" or direction == "inE":
                self.UNION_DIRECTION[i+1] = "IN"
            else:
                self.UNION_DIRECTION[i+1] = "BOTH"

        return self

    def __str__(self):
        return "union"
