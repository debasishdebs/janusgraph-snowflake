from gen.graphdb_pb2 import MiddleMostByteCode, InnerMostByteCode
from typing import List


class TraversalStep(object):
    TRAVERSAL_STEPS = None
    TRAVERSAL_FILTER = dict()
    DIRECTION = "NA"
    SELECTION_BY = None
    TRAVERSAL_QUERY = ""
    ERROR = "NA"
    TRAVERSAL_VIEW = "level"
    ITERATION_NUM = 1
    PREVIOUS_VIEW = None

    def __init__(self, steps: List[MiddleMostByteCode]):
        # print(f"Initializing traversal with {steps} of type {type(steps)}")
        assert len(steps) == 2
        assert type(steps[0]) == MiddleMostByteCode
        self.TRAVERSAL_STEPS = steps

        from utils.common_resources import Commons
        self.master = Commons.MASTER_TABLE
        self.edges = Commons.EDGES_TABLE

    def get_selection_step(self):
        return self.SELECTION_BY

    def with_selection_step(self, step):
        # print("Here")
        self.SELECTION_BY = step
        # print(f"Select by {self.SELECTION_BY}")
        return self

    def execute(self):
        self._get_traversal_direction_()
        print("Got traversal direction")

        self._generate_traversal_filters_()
        print("Generated traversal filters")
        print(self.TRAVERSAL_FILTER)

        self._generate_traversal_query_()
        print("Generated trversal query with")
        print(f"iter: {self.ITERATION_NUM}, view: {self.TRAVERSAL_VIEW}, filter: {self.TRAVERSAL_FILTER}, dir: {self.DIRECTION}")

        return self

    def _generate_traversal_query_(self):
        edge_filters = self.TRAVERSAL_FILTER["edge"]
        vertex_filters = self.TRAVERSAL_FILTER["vertex"]
        edge_direction = edge_filters[0]["direction"]
        vertex_direction = vertex_filters[0]["direction"]

        assert edge_direction == vertex_direction
        print("Asserted the equality of vertex & edge filter direction")

        print("Generating traversal query for edge filter ")
        print(edge_filters)
        print("Generating vertex traversal query for filter")
        print(vertex_filters)

        edge_filter_props = []
        edge_filter_vals = []
        edge_filter_predicates = []
        for edge_filter in edge_filters:
            edge_filter_props.append(edge_filter["property"] if edge_filter["property"] is not "" else None)
            edge_filter_vals.append(edge_filter["value"] if edge_filter["value"] is not "" else None)
            edge_filter_predicates.append(edge_filter["predicate"] if edge_filter["predicate"] is not "" else None)

        vertex_filter_props = []
        vertex_filter_vals = []
        vertex_filter_predicates = []
        for vertex_filter in vertex_filters:
            vertex_filter_props.append(vertex_filter["property"] if vertex_filter["property"] is not "" else None)
            vertex_filter_vals.append(vertex_filter["value"] if vertex_filter["value"] is not "" else None)
            vertex_filter_predicates.append(vertex_filter["predicate"] if vertex_filter["predicate"] is not "" else None)

        print("Edge filters are ", edge_filter_props, edge_filter_vals, edge_filter_predicates)
        print("Vertex filters are ", vertex_filter_props, vertex_filter_vals, vertex_filter_predicates)

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
                # filter_prefix = " and "

                if edge_filter_prop == "label":
                    property_ = "ne.value_label"
                elif edge_filter_prop == "id":
                    property_ = "ne.value_id"
                else:
                    property_ = f" get(ne.value_properties:\"{edge_filter_prop}\", 0)"
                    property_ = f" ne.value_properties:\"{edge_filter_prop}\""
                    if time_condition:
                        property_ = property_ + "::datetime"

                if edge_filter_predicate == "eq":
                    edge_filter = f" {filter_prefix} {property_} = '{edge_filter_val}' "
                elif edge_filter_predicate == "neq":
                    edge_filter = f" {filter_prefix} {property_} != '{edge_filter_val}' "
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
                        edge_filter = f" {filter_prefix} {property_} between '{edge_filter_val[0]}'::datetime and '{edge_filter_val[1]}'::datetime "
                    else:
                        edge_filter = f" {filter_prefix} {property_} between '{edge_filter_val[0]}' and '{edge_filter_val[1]}' "
                elif edge_filter_predicate == "within":
                    print("Asserting value if of type list for within predicate")
                    assert type(edge_filter_val) == list

                    query_value = [f"'{x}'" for x in edge_filter_val]
                    edge_filter = f" {filter_prefix} {property_} in ({','.join(query_value)}) "
                else:
                    print("Predicates supported are between/within/gte/lte/gt/lt/eq for edge but got in traversal edge " + edge_filter_predicate)
                    raise Exception()

                filter_query += edge_filter

        print("Edge filter query is ", filter_query)

        for i in range(len(vertex_filter_props)):
            vertex_filter_prop = vertex_filter_props[i]
            vertex_filter_val = vertex_filter_vals[i]
            vertex_filter_predicate = vertex_filter_predicates[i]

            time_condition = "time" == vertex_filter_val[0] if vertex_filter_val is not None else False
            if time_condition:
                print("There is time condition in vertex filter in traversal")
                vertex_filter_val = vertex_filter_val[1:]

            if (vertex_filter_prop is not None and vertex_filter_val is not None) and (vertex_filter_prop != "" and vertex_filter_val != ""):
                filter_prefix = " where " if filter_query is "" else " and "
                # filter_prefix = " and "

                CASE_CONDITION = False

                if vertex_filter_prop == "label":
                    property_ = "nm.label"
                elif vertex_filter_prop == "id":
                    property_ = "nm.node_id"
                elif vertex_filter_prop == "caseId":
                    property_ = "nm.node_id"
                    CASE_CONDITION = True
                else:
                    property_ = f" get(nm.properties:\"{vertex_filter_prop}\", 0)"
                    property_ = f" nm.properties:\"{vertex_filter_prop}\""
                    if time_condition:
                        property_ = property_ + "::datetime"

                print(f"Property: {property_}, case_condition: {CASE_CONDITION}")

                if vertex_filter_predicate == "eq":
                    if CASE_CONDITION:
                        CASE_ALL_HANDLER = "case when lower(q.value:\"propertyValue\") = 'all' \
                                                then lower(n.value:value) != lower(q.value:\"propertyValue\") \
                                                else lower(n.value:value) = lower(q.value:\"propertyValue\") \
                                            end"
                        case_criteria = "select n.value:node_id::numeric as node_id \n" \
                        "from case_metadata c, lateral flatten(input => nodes) n, lateral flatten(input => query) q \n" \
                                        f"where c.case_id = '{vertex_filter_val}' \n" \
                            f"and n.value:property = q.value:\"propertyKey\" \n" \
                                        f"and {CASE_ALL_HANDLER}"
                        vertex_filter = f" {filter_prefix} {property_} = ({case_criteria}) "
                    else:
                        vertex_filter = f" {filter_prefix} {property_} = '{vertex_filter_val}' "
                elif vertex_filter_predicate == "neq":
                    vertex_filter = f" {filter_prefix} {property_} != '{vertex_filter_val}' "
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
                        vertex_filter = f" {filter_prefix} {property_} between '{vertex_filter_val[0]}'::datetime and '{vertex_filter_val[1]}'::datetime "
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

        print("Vertex filter query is ", filter_query)

        if edge_direction == "OUT":
            if self.ITERATION_NUM == 2:
                select_step = f"select distinct ne.node_id, ne.map_id, {self.ITERATION_NUM} as lvl, ne.value_id, 'out' as direction, ne.value_label, ne.value_properties  " \
                    f" from {self.edges} ne " \
                    "inner join main m on {main_join_condition}"
            else:
                if self.PREVIOUS_VIEW is not None:
                    select_step = f"select distinct ne.node_id, ne.map_id,  {self.ITERATION_NUM} as lvl, ne.value_id, 'out' as direction, ne.value_label, ne.value_properties  " \
                        f"from {self.edges} ne " \
                        f"inner join {self.PREVIOUS_VIEW} m on " + " {main_join_condition}"
                else:
                    select_step = f"select distinct ne.node_id, ne.map_id,  {self.ITERATION_NUM} as lvl, ne.value_id, 'out' as direction, ne.value_label, ne.value_properties  " \
                        f"from {self.edges} ne " \
                        f"inner join level{self.ITERATION_NUM-1} m on " + "{main_join_condition}"

            select_step = select_step + "\n {join_query} \n"

        elif edge_direction == "IN":
            if self.ITERATION_NUM == 2:
                select_step = f"select distinct ne.node_id as map_id, ne.map_id as node_id, {self.ITERATION_NUM} as lvl, ne.value_id, 'in' as direction, ne.value_label, ne.value_properties  " \
                    f"from {self.edges} ne " \
                    "inner join main m on {main_join_condition} "
            else:
                if self.PREVIOUS_VIEW is not None:
                    select_step = f"select distinct ne.node_id as map_id, ne.map_id as node_id, {self.ITERATION_NUM} as lvl, ne.value_id, 'in' as direction, ne.value_label, ne.value_properties  " \
                        f"from {self.edges} ne " \
                        f"inner join {self.PREVIOUS_VIEW} m on " + "{main_join_condition}"
                else:
                    select_step = f"select distinct ne.node_id as map_id, ne.map_id as node_id,  {self.ITERATION_NUM} as lvl, ne.value_id, 'in' as direction, ne.value_label, ne.value_properties  " \
                        f"from {self.edges} ne " \
                        f"inner join level{self.ITERATION_NUM-1} m on " + "{main_join_condition}"

            select_step = select_step + "\n {join_query}\n "

        else:
            if self.ITERATION_NUM == 2:
                select_step = f"select distinct ne.node_id, ne.map_id, {self.ITERATION_NUM} as lvl, ne.value_id, 'out' as direction, ne.value_label, ne.value_properties  " \
                    f"from {self.edges} ne " + "inner join main m on {main_out_join_condition}" + "\n{join_query_out}\n {filter} "
                select_step += " \n union all \n "
                select_step += f"select distinct ne.map_id as node_id, ne.node_id as map_id, {self.ITERATION_NUM} as lvl, ne.value_id, 'in' as direction, ne.value_label, ne.value_properties  " \
                    f"from {self.edges} ne " + "inner join main m on {main_in_join_condition}" + "\n{join_query_in}\n {filter} "

            else:
                if self.PREVIOUS_VIEW is not None:
                    select_step = f"select distinct ne.node_id, ne.map_id,  {self.ITERATION_NUM} as lvl, ne.value_id, 'out' as direction, ne.value_label, ne.value_properties  " \
                        f"from {self.edges} ne inner join {self.PREVIOUS_VIEW} m on " + "{main_out_join_condition}" + "\n{join_query_out}\n {filter} "
                    select_step += " \n union all \n "
                    select_step += f"select distinct ne.map_id as node_id, ne.node_id as map_id, {self.ITERATION_NUM} as lvl, ne.value_id, 'in' as direction, ne.value_label, ne.value_properties  " \
                       f"from {self.edges} ne inner join {self.PREVIOUS_VIEW} m on " + "{main_in_join_condition}" + "\n{join_query_in}\n {filter} "

                else:
                    select_step = f"select distinct ne.node_id, ne.map_id,  {self.ITERATION_NUM} as lvl, ne.value_id, 'out' as direction, ne.value_label, ne.value_properties  " \
                          f"from {self.edges} ne inner join level{self.ITERATION_NUM-1} m on " + "{main_out_join_condition}" + "\n{join_query_out}\n {filter} "
                    select_step += " \n union all \n "
                    select_step += f"select distinct ne.map_id as node_id, ne.node_id as map_id,  {self.ITERATION_NUM} as lvl, ne.value_id, 'in' as direction, ne.value_label, ne.value_properties  " \
                           f"from {self.edges} ne inner join level{self.ITERATION_NUM-1} m on " + "{main_in_join_condition}" + "\n{join_query_in}\n {filter} "

        if edge_direction == "OUT":
            join_step = ""
            if len(vertex_filters) > 0:
                join_step += f" inner join {self.master} nm on nm.node_id = ne.map_id "
            # join_step += " \n where (ne.node_id = m.map_id and ne.map_id != m.node_id) \n"

            join_info = {edge_direction: join_step}
            print("Todo line 261 in TraversalStep")
            main_join_condition = {edge_direction: "ne.node_id = m.map_id and ne.map_id != m.node_id"}
            main_join_condition = {edge_direction: "ne.node_id = m.map_id"}

        elif edge_direction == "IN":
            join_step = ""
            if len(vertex_filters) > 0:
                join_step += f" inner join {self.master} nm on nm.node_id = ne.node_id "
            # join_step += " \n where (ne.map_id = m.map_id and ne.node_id != m.node_id) \n"

            join_info = {edge_direction: join_step}
            print("Todo line 271 in TraversalStep")
            main_join_condition = {edge_direction: "ne.map_id = m.map_id and ne.node_id != m.node_id"}
            main_join_condition = {edge_direction: "ne.map_id = m.map_id"}

        else:
            join_step = ""
            if len(vertex_filters) > 0:
                join_step += f" inner join {self.master} nm on nm.node_id = ne.map_id "
            # join_step += " \n where (ne.node_id = m.map_id and ne.map_id != m.node_id) \n"
            join_info = {"OUT": join_step}
            print("Todo line 282 in TraversalStep")
            main_join_condition = {"OUT": "ne.node_id = m.map_id and ne.map_id != m.node_id"}
            main_join_condition = {"OUT": "ne.node_id = m.map_id"}

            join_step = ""
            if len(vertex_filters) > 0:
                join_step += f" inner join {self.master} nm on nm.node_id = ne.node_id "
            # join_step += " \n where (ne.map_id = m.map_id and ne.node_id != m.node_id) \n"
            join_info["IN"] = join_step
            print("Todo line 292 in TraversalStep")
            main_join_condition["IN"] = "ne.map_id = m.map_id and ne.node_id != m.node_id"
            main_join_condition["IN"] = "ne.map_id = m.map_id"

        if edge_direction in ["OUT", "IN"]:
            iterate_query = select_step.format(join_query=join_info[edge_direction],
                                               main_join_condition=main_join_condition[edge_direction])
            iterate_query += filter_query
        else:
            in_join_query = join_info["IN"]
            out_join_query = join_info["OUT"]
            main_in_join = main_join_condition["IN"]
            main_out_join = main_join_condition["OUT"]
            iterate_query = select_step.format(join_query_in=in_join_query, join_query_out=out_join_query,
                                               filter=filter_query, main_in_join_condition=main_in_join,
                                               main_out_join_condition=main_out_join)

        #
        # if self.ITERATION_NUM == 2:
        #     if edge_direction == "OUT":
        #         join_step = f" inner join {self.edges} ne on ne.node_id = main.map_id " \
        #             f"inner join {self.master} nm on nm.node_id = ne.node_id"
        #
        #     elif edge_direction == "IN":
        #         join_step = f" inner join {self.edges} ne on ne.map_id = main.node_id " \
        #             f"inner join {self.master} nm on nm.node_id = ne.node_id"
        #
        #     else:
        #         join_step = f" inner join {self.edges} ne on ne.map_id = main.node_id or ne.node_id = main.map_id " \
        #                     f"inner join {self.master} nm on nm.node_id = ne.node_id"
        #
        # else:
        #     if edge_direction == "OUT":
        #         join_step = f" inner join {self.edges} ne on ne.node_id = nm.node_id "
        #         if self.PREVIOUS_VIEW is None:
        #             join_step += f" inner join level{self.ITERATION_NUM - 1} l on nm.node_id = l.map_id "
        #         else:
        #             join_step += f" inner join {self.PREVIOUS_VIEW} l on nm.node_id = l.map_id "
        #
        #     elif edge_direction == "IN":
        #         join_step = f" inner join {self.edges} ne on ne.node_id = nm.node_id "
        #         if self.PREVIOUS_VIEW is None:
        #             join_step += f" inner join level{self.ITERATION_NUM - 1} l on ne.map_id = l.node_id "
        #         else:
        #             join_step += f" inner join {self.PREVIOUS_VIEW} l on ne.map_id = l.map_id "
        #
        #     else:
        #         join_step = f" inner join {self.edges} ne on ne.node_id = nm.node_id "
        #         if self.PREVIOUS_VIEW is None:
        #             join_step += f"inner join level{self.ITERATION_NUM-1} l on ne.map_id = l.node_id or ne.node_id = l.map_id"
        #         else:
        #             join_step += f"inner join {self.PREVIOUS_VIEW} l on ne.map_id = l.node_id or ne.node_id = l.map_id"
        #
        # query = select_step + join_step + filter_query

        print("The final generated query is ")
        print(iterate_query)
        print("===== END QUERY GEN IN TRAVERSAL =====")
        tbl_prefix = "with" if self.ITERATION_NUM == 0 else ""
        self.TRAVERSAL_QUERY = f"{tbl_prefix} {self.TRAVERSAL_VIEW} as ({iterate_query})"
        print("The final traversal query is ")
        print(self.TRAVERSAL_QUERY)
        return self

    def _generate_traversal_filters_(self):
        # traversal = self.REPEAT_STEP.middle_layer[1:]
        #
        edge_step = self.TRAVERSAL_STEPS[0]
        vertex_step = self.TRAVERSAL_STEPS[1]

        assert type(edge_step) == MiddleMostByteCode and type(vertex_step) == MiddleMostByteCode
        print("==== DETERMINING THE EDGE DIRECTION START ====")
        print(f"edge step if \n{edge_step} {type(edge_step)} {len(edge_step.middle_layer)}and vertex step \n{vertex_step} {type(vertex_step)} {len(vertex_step.middle_layer)}")
        print("==== DETERMINING THE EDGE DIRECTION END ====")

        edge_step = edge_step.middle_layer[1:] if len(edge_step.middle_layer) > 1 else []
        vertex_step = vertex_step.middle_layer[1:] if len(vertex_step.middle_layer) > 1 else []

        # print(edge_step)
        # print("-----")
        # print(vertex_step)
        filter_vertex = False
        filter_edge = False
        for s in vertex_step:
            if len(s.inner_values) != 0:
                filter_vertex = True
        for s in edge_step:
            if len(s.inner_values) != 0:
                filter_edge = True

        # print(filter_edge)
        # print(filter_vertex)

        if filter_edge:
            edge_filters = []
            for step in edge_step:
                for j in range(0, len(step.inner_values), 2):
                    propname = step.inner_values[j]
                    propname = propname if "T." not in propname else propname.split("T.")[1]

                    propval = step.inner_values[j+1]
                    value_step = propval.split(",")
                    # print("inside traversal gen filter ", propval, value_step, len(value_step))

                    # print("Filter edge ", value_step)
                    if len(value_step) == 1:
                        predicate = "eq"
                        value = value_step[0]
                    else:
                        predicate = value_step[0]
                        value = value_step[1:]
                        if len(value) == 1 and predicate not in ("within", "between"):
                            value = value[0]

                    filter = {
                        "direction": self.DIRECTION,
                        "property": propname,
                        "value": value,
                        "predicate": predicate
                    }
                    # print(filter)
                    edge_filters.append(filter)

            self.TRAVERSAL_FILTER["edge"] = edge_filters
            print(self.TRAVERSAL_FILTER)

        else:
            self.TRAVERSAL_FILTER["edge"] = [{
                "direction": self.DIRECTION,
                "property": "",
                "value": "",
                "predicate": ""
            }]

        if filter_vertex:
            vertex_filters = []
            # print("Vertex step ", vertex_step)
            for step in vertex_step:
                # print("Each step ", step)
                for j in range(0, len(step.inner_values), 2):
                    propname = step.inner_values[j]
                    propname = propname if "T." not in propname else propname.split("T.")[1]

                    propval = step.inner_values[j+1]
                    value_step = propval.split(",")
                    # print("inside traversal gen filter ", j, propname, propval, value_step, len(value_step))

                    # print("Filter vertex ", value_step)
                    if len(value_step) == 1:
                        predicate = "eq"
                        value = value_step[0]
                    else:
                        predicate = value_step[0]
                        value = value_step[1:]
                        if len(value) == 1 and predicate not in ("within", "between"):
                            value = value[0]

                    filter = {
                        "direction": self.DIRECTION,
                        "property": propname,
                        "value": value,
                        "predicate": predicate
                    }
                    print(filter)
                    vertex_filters.append(filter)

            self.TRAVERSAL_FILTER["vertex"] = vertex_filters

        else:
            print("Only direction for vertex filter")
            self.TRAVERSAL_FILTER["vertex"] = [{
                "direction": self.DIRECTION,
                "property": "",
                "value": "",
                "predicate": ""
            }]
            print(self.TRAVERSAL_FILTER)
        #
        # if len(vertex_step) > 0:
        #     if vertex_step[0] == "as":
        #         vertex_filter = False
        #     else:
        #         vertex_filter = True
        #
        #     if vertex_filter:
        #         if vertex_step[1] not in ["within", "between", "gte", "lte", "gt", "lt", "eq"]:
        #             value = vertex_step[1]
        #         else:
        #             value = vertex_step[1:]
        #
        #         self.TRAVERSAL_FILTER["vertex"] = {
        #             "direction": self.DIRECTION,
        #             "property": vertex_step[0] if vertex_step[0] not in ["T.id", "T.label"] else vertex_step[0].split("T.")[1],
        #             "value": value
        #         }
        #     else:
        #         self.TRAVERSAL_FILTER["vertex"] = {
        #             "direction": self.DIRECTION,
        #         }
        # else:
        #     self.TRAVERSAL_FILTER["vertex"] = {
        #         "direction": self.DIRECTION,
        #     }
        #
        # print("The filters are \n", self.TRAVERSAL_FILTER)
        #
        # if 1 < len(traversal) <= 3:
        #     if len(traversal) == 3:
        #         print("1")
        #         print(traversal)
        #         edge_step = traversal[0]
        #         vertex_step = traversal[1]
        #
        #         print(f"edge step if \n{edge_step} {type(edge_step)} {len(edge_step.inner_values)}and vertex step \n{vertex_step} {type(vertex_step)} {len(vertex_step.inner_values)}")
        #
        #         assert type(edge_step) == InnerMostByteCode and type(vertex_step) == InnerMostByteCode
        #         assert len(edge_step.inner_values) == 3 and len(vertex_step.inner_values) == 3
        #         print("2")
        #         edge_step = edge_step.inner_values
        #         vertex_step = vertex_step.inner_values
        #         print("3")
        #
        #         self.REPEAT_FILTER["edge"] = {
        #             "direction": self.DIRECTION,
        #             "property": edge_step[1] if edge_step[1] not in ["T.id", "T.label"] else edge_step[1].split("T.")[1],
        #             "value": edge_step[2]
        #         }
        #
        #         self.REPEAT_FILTER["vertex"] = {
        #             "direction": self.DIRECTION,
        #             "property": vertex_step[1] if vertex_step[1] not in ["T.id", "T.label"] else vertex_step[1].split("T.")[1],
        #             "value": vertex_step[2]
        #         }
        #         print("4")
        #
        #     else:
        #         print("5")
        #         vertex_step = traversal[1]
        #         assert type(vertex_step) == InnerMostByteCode
        #         assert len(vertex_step.inner_values) == 3
        #         vertex_step = vertex_step.inner_values
        #         print("6")
        #
        #         self.REPEAT_FILTER["vertex"] = {
        #             "direction": self.DIRECTION,
        #             "property": vertex_step[1] if vertex_step[1] not in ["T.id", "T.label"] else vertex_step[1].split("T.")[1],
        #             "value": vertex_step[2]
        #         }
        #         print("7")
        # else:
        #     self.ERROR = "Current the Graph supports only 1 hop traversal within REPEAT whereas got more than 1"

        return self

    def _get_traversal_direction_(self):
        # print("Getting traversal direction ", self.TRAVERSAL_STEPS[0])
        # print("And the middle later is ", self.TRAVERSAL_STEPS[0].middle_layer)
        # print(type(self.TRAVERSAL_STEPS[0].middle_layer))
        # print(len(self.TRAVERSAL_STEPS[0].middle_layer))
        # print(type(self.TRAVERSAL_STEPS[0].middle_layer[1]))
        # print(self.TRAVERSAL_STEPS[0].middle_layer[1], " 1")
        # print(self.TRAVERSAL_STEPS[0].middle_layer[0], " 0")

        traversal = self.TRAVERSAL_STEPS[0].middle_layer[0]
        direction = traversal.inner_values[0]
        print(direction, " is the direction for traversal")

        if direction == "out" or direction == "outE":
            self.DIRECTION = "OUT"
        elif direction == "in" or direction == "inE":
            self.DIRECTION = "IN"
        else:
            self.DIRECTION = "BOTH"
        return self

    def __str__(self):
        return "traversal"
