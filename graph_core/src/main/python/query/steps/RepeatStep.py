from gen.graphdb_pb2 import MiddleMostByteCode, InnerMostByteCode
from typing import List


class RepeatStep(object):
    REPEAT_STEP = None
    REPEAT_FILTER = dict()
    SNOWFLAKE_FN = " call something_here()"
    DIRECTION = "NA"
    SELECTION_BY = None
    REPEAT_QUERY = ""
    REPEAT_TIMES = None
    ERROR = "NA"
    RCTE_MAIN_VIEW = "edges"
    RCTE_REPEAT_VIEW = "edges_rcte"
    ITERATION_NUM = 1
    CENTRIC_QUERY = None

    def __init__(self, steps: List[MiddleMostByteCode]):
        print(f"Initializing repeat with {steps} of type {type(steps)}")
        assert type(steps[0]) == MiddleMostByteCode
        self.REPEAT_STEP = steps[0]

        from utils.common_resources import Commons
        self.master = Commons.MASTER_TABLE
        self.edges = Commons.EDGES_TABLE

    def get_selection_step(self):
        return self.SELECTION_BY

    def with_selection_step(self, step):
        print("Here")
        self.SELECTION_BY = step
        print(f"Select by {self.SELECTION_BY}")
        return self

    def execute(self):
        print(f"C: Executing Repeat step now")

        # assert self._number_of_traversals_in_repeat_() == 1
        # print("Asserted number of traversals")

        self._get_repeat_times_()
        print("Computed the number of times repeat to be run")

        self._get_repeat_direction_()
        print("Got repeat direction")

        self._generate_repeat_filters_()
        print("Generated repeat filters")
        print(self.REPEAT_FILTER)
        print(self.ERROR)

        self._generate_filter_query_()
        print("Generated repeat query")
        print(self.CENTRIC_QUERY)

        if self.CENTRIC_QUERY is not None:
            print("Generating aggregated query for repeat")
            self._combine_rcte_query_components_()
            print("Combined the components of various RCTE sub queries")
        return self

    def _get_repeat_times_(self):
        repeat_times_step = self.REPEAT_STEP.middle_layer[-1]
        times = repeat_times_step.inner_values[1]
        self.REPEAT_TIMES = int(times)
        return self

    def _generate_sql_for_given_traversal_direction_(self):
        if self.DIRECTION == "OUT":
            sql = "select node_id as root_id, value_id as edge_id, \
            'outgoing' as edge_direction, value_label as edge_label, value_properties as edge_properties, "\
            f"map_id as oth_id from {self.edges} "

        elif self.DIRECTION == "IN":
            sql = "select node_id as oth_id, value_id as edge_id, \
            'incoming' as edge_direction, value_label as edge_label, value_properties as edge_properties, "\
            f"map_id as root_id from {self.edges} "

        else:
            sql = "select node_id as root_id, value_id as edge_id, \
            'outgoing' as edge_direction, value_label as edge_label, value_properties as edge_properties, "\
            f"map_id as oth_id from {self.edges} \n"

            sql += "union all\n"

            sql += "select node_id as oth_id, value_id as edge_id, \
            'incoming' as edge_direction, value_label as edge_label, value_properties as edge_properties, "\
            f"map_id as root_id from {self.edges} "

        return sql

    def _apply_vertex_filters_on_parent_traversal(self, parent_sql):
        sql = f"select root_id, edge_id, edge_label, edge_properties, oth_id \
            from ({parent_sql}) ne inner join {self.master} nm on nm.node_id = oth_id"

        if self.REPEAT_FILTER["vertex"]["value"] != "":
            prop = self.REPEAT_FILTER["vertex"]["property"]
            val = self.REPEAT_FILTER["vertex"]["value"]

            condtn = f" where nm.properties:{prop} = '{val}' "
            sql += condtn
        return sql

    def _apply_edge_vertex_filters_on_parent_traversal_(self, edge_parent_sql):
        sql = f"select root_id, edge_direction, edge_id, edge_label, edge_properties, oth_id \
            from {self.master} nm, ({edge_parent_sql}) ne where nm.node_id = ne.oth_id"

        if self.REPEAT_FILTER["vertex"]["value"] != "":
            prop = self.REPEAT_FILTER["vertex"]["property"]
            val = self.REPEAT_FILTER["vertex"]["value"]
            predicate = self.REPEAT_FILTER["vertex"]["predicate"]

            if predicate == "within":
                values = [f"'{x}'" for x in val]
                condtn = f" and nm.properties:{prop} in ({','.join(values)}) "
            elif predicate == "between":
                condtn = f" and nm.properties:{prop} between '{val[0]}' and '{val[1]}' "
            elif predicate == "gte":
                condtn = f" and nm.properties:{prop} >= '{val[0]}'  "
            elif predicate == "lte":
                condtn = f" and nm.properties:{prop} <= '{val[0]}'  "
            elif predicate == "gt":
                condtn = f" and nm.properties:{prop} > '{val[0]}'  "
            elif predicate == "lt":
                condtn = f" and nm.properties:{prop} < '{val[0]}'  "
            elif predicate == "eq":
                condtn = f" and nm.properties:{prop} = '{val[0]}'  "
            else:
                if predicate != "":
                    print("Predicates supported are between/within/gte/lte/gt/lt/eq but got in repet edge_vertex" + predicate)
                    raise Exception()
                else:
                    condtn = ""

            sql += condtn
        return sql

    def _apply_edge_filters_on_parent_traversal_(self, root_sql):
        if self.DIRECTION != "BOTH":
            if self.REPEAT_FILTER["edge"]["value"] != "":
                prop = self.REPEAT_FILTER["edge"]["property"]
                val = self.REPEAT_FILTER["edge"]["value"]
                predicate = self.REPEAT_FILTER["edge"]["predicate"]

                if prop not in ["id", "label"]:
                    if predicate == "within":
                        values = [f"'{x}'" for x in val]
                        condtn = f" where edge_properties:{prop} in ({','.join(values)}) "
                    elif predicate == "between":
                        condtn = f" where edge_properties:{prop} between '{val[0]}' and '{val[1]}' "
                    elif predicate == "gte":
                        condtn = f" where edge_properties:{prop} >= '{val[0]}'  "
                    elif predicate == "lte":
                        condtn = f" where edge_properties:{prop} <= '{val[0]}'  "
                    elif predicate == "gt":
                        condtn = f" where edge_properties:{prop} > '{val[0]}'  "
                    elif predicate == "lt":
                        condtn = f" where edge_properties:{prop} < '{val[0]}'  "
                    elif predicate == "eq":
                        condtn = f" where edge_properties:{prop} = '{val[0]}'  "
                    else:
                        if predicate == "":
                            condtn = ""
                        else:
                            print("Predicates supported are between/within/gte/lte/gt/lt/eq but got in edge_repeat_parent" + predicate)
                            raise Exception()
                elif prop == "id":
                    if predicate == "within":
                        values = [f"'{x}'" for x in val]
                        condtn = f" where edge_id in ({','.join(values)}) "
                    elif predicate == "between":
                        condtn = f" where edge_id between '{val[0]}' and '{val[1]}' "
                    elif predicate == "gte":
                        condtn = f" where edge_id >= '{val[0]}'  "
                    elif predicate == "lte":
                        condtn = f" where edge_id <= '{val[0]}'  "
                    elif predicate == "gt":
                        condtn = f" where edge_id > '{val[0]}'  "
                    elif predicate == "lt":
                        condtn = f" where edge_id < '{val[0]}'  "
                    elif predicate == "eq":
                        condtn = f" where edge_id = '{val[0]}'  "
                    else:
                        if predicate == "":
                            condtn = ""
                        else:
                            print("Predicates supported are between/within/gte/lte/gt/lt/eq but got " + predicate)
                            raise Exception()
                else:
                    if predicate == "within":
                        values = [f"'{x}'" for x in val]
                        condtn = f" where edge_label in ({','.join(values)})"
                    elif predicate == "between":
                        condtn = f" where edge_label between '{val[0]}' and '{val[1]}' "
                    elif predicate == "gte":
                        condtn = f" where edge_label >= '{val[0]}'  "
                    elif predicate == "lte":
                        condtn = f" where edge_label <= '{val[0]}'  "
                    elif predicate == "gt":
                        condtn = f" where edge_label > '{val[0]}'  "
                    elif predicate == "lt":
                        condtn = f" where edge_label < '{val[0]}'  "
                    elif predicate == "eq":
                        condtn = f" where edge_label = '{val[0]}'  "
                    else:
                        if predicate == "":
                            condtn = ""
                        else:
                            print("Predicates supported are between/within/gte/lte/gt/lt/eq but got " + predicate)
                            raise Exception()
                #
                # if prop not in ["id", "label"]:
                #     if isinstance(val, list):
                #         predicate = val[0]
                #         if predicate == "within":
                #             values = [f"'{x}'" for x in val[1:]]
                #             condtn = f" where edge_properties:{prop} in ({','.join(values)}) "
                #         elif predicate == "between":
                #             condtn = f" where edge_properties:{prop} between '{val[1]}' and '{val[2]}' "
                #         elif predicate == "gte":
                #             condtn = f" where edge_properties:{prop} >= '{val[1]}'  "
                #         elif predicate == "lte":
                #             condtn = f" where edge_properties:{prop} <= '{val[1]}'  "
                #         elif predicate == "gt":
                #             condtn = f" where edge_properties:{prop} > '{val[1]}'  "
                #         elif predicate == "lt":
                #             condtn = f" where edge_properties:{prop} < '{val[1]}'  "
                #         elif predicate == "eq":
                #             condtn = f" where edge_properties:{prop} = '{val[1]}'  "
                #         else:
                #             print("Predicates supported are between/within/gte/lte/gt/lt/eq but got " + predicate)
                #             raise Exception()
                #     else:
                #         condtn = f" where edge_properties:{prop} = '{val}' "
                # elif prop == "id":
                #     if isinstance(val, list):
                #         predicate = val[0]
                #         if predicate == "within":
                #             values = [f"'{x}'" for x in val[1:]]
                #             condtn = f" where edge_id in ({','.join(values)}) "
                #         elif predicate == "between":
                #             condtn = f" where edge_id between '{val[1]}' and '{val[2]}' "
                #         elif predicate == "gte":
                #             condtn = f" where edge_id >= '{val[1]}'  "
                #         elif predicate == "lte":
                #             condtn = f" where edge_id <= '{val[1]}'  "
                #         elif predicate == "gt":
                #             condtn = f" where edge_id > '{val[1]}'  "
                #         elif predicate == "lt":
                #             condtn = f" where edge_id < '{val[1]}'  "
                #         elif predicate == "eq":
                #             condtn = f" where edge_id = '{val[1]}'  "
                #         else:
                #             print("Predicates supported are between/within/gte/lte/gt/lt/eq but got " + predicate)
                #             raise Exception()
                #     else:
                #         condtn = f" where edge_id = '{val}' "
                # else:
                #     if isinstance(val, list):
                #         predicate = val[0]
                #         if predicate == "within":
                #             values = [f"'{x}'" for x in val[1:]]
                #             condtn = f" where edge_label in ({','.join(values)})"
                #         elif predicate == "between":
                #             condtn = f" where edge_label between '{val[1]}' and '{val[2]}' "
                #         elif predicate == "gte":
                #             condtn = f" where edge_label >= '{val[1]}'  "
                #         elif predicate == "lte":
                #             condtn = f" where edge_label <= '{val[1]}'  "
                #         elif predicate == "gt":
                #             condtn = f" where edge_label > '{val[1]}'  "
                #         elif predicate == "lt":
                #             condtn = f" where edge_label < '{val[1]}'  "
                #         elif predicate == "eq":
                #             condtn = f" where edge_label = '{val[1]}'  "
                #         else:
                #             print("Predicates supported are between/within/gte/lte/gt/lt/eq but got " + predicate)
                #             raise Exception()
                #     else:
                #         condtn = f" where edge_label = '{val}' "
                root_sql += condtn
        else:
            if self.REPEAT_FILTER["edge"]["value"] != "":
                prop = self.REPEAT_FILTER["edge"]["property"]
                val = self.REPEAT_FILTER["edge"]["value"]
                predicate = self.REPEAT_FILTER["edge"]["predicate"]

                if prop not in ["id", "label"]:
                    if predicate == "within":
                        values = [f"'{x}'" for x in val]
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_properties:{prop} in ({','.join(values)})"
                    elif predicate == "between":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_properties:{prop} between '{val[0]}' and '{val[1]}' "
                    elif predicate == "gte":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_properties:{prop} >= '{val[0]}' "
                    elif predicate == "lte":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_properties:{prop} <= '{val[0]}' "
                    elif predicate == "gt":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_properties:{prop} > '{val[0]}' "
                    elif predicate == "lt":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_properties:{prop} < '{val[0]}' "
                    elif predicate == "eq":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_properties:{prop} = '{val[0]}' "
                    else:
                        if predicate == "":
                            condition_sql = ""
                        else:
                            print("Predicates supported are between/within/gte/lte/gt/lt/eq but got " + predicate)
                            raise Exception()

                elif prop == "id":
                    if predicate == "within":
                        values = [f"'{x}'" for x in val]
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_id in ({','.join(values)})"
                    elif predicate == "between":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_id between '{val[0]}' and '{val[1]}'"
                    elif predicate == "gte":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_id >= '{val[0]}'"
                    elif predicate == "lte":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_id <= '{val[0]}'"
                    elif predicate == "gt":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_id > '{val[0]}'"
                    elif predicate == "lt":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_id < '{val[0]}'"
                    elif predicate == "eq":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_id = '{val[0]}'"
                    else:
                        if predicate == "":
                            condition_sql = ""
                        else:
                            print("Predicates supported are between/within/gte/lte/gt/lt/eq but got " + predicate)
                            raise Exception()

                else:
                    if predicate == "within":
                        values = [f"'{x}'" for x in val]
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_label in ({','.join(values)}) "
                    elif predicate == "between":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_label between '{val[0]}' and '{val[1]}'"
                    elif predicate == "gte":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_label >= '{val[0]}'"
                    elif predicate == "lte":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_label <= '{val[0]}'"
                    elif predicate == "gt":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_label > '{val[0]}'"
                    elif predicate == "lt":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_label < '{val[0]}'"
                    elif predicate == "eq":
                        condition_sql = f"select * \
                        from ({root_sql}) where edge_label = '{val[0]}'"
                    else:
                        if predicate == "":
                            condition_sql = ""
                        else:
                            print("Predicates supported are between/within/gte/lte/gt/lt/eq but got " + predicate)
                            raise Exception()

                root_sql = condition_sql

        return root_sql

    def _generate_filter_query_(self):
        print("Generating filter query")

        if "edge" in self.REPEAT_FILTER:
            edge_parent_sql = self._generate_sql_for_given_traversal_direction_()
            edge_sql = self._apply_edge_filters_on_parent_traversal_(edge_parent_sql)
            edge_vertex_sql = self._apply_edge_vertex_filters_on_parent_traversal_(edge_sql)

            # tbl_prefix = "with" if self.ITERATION_NUM == 1 else ""
            sql = f" {self.RCTE_MAIN_VIEW} as ({edge_vertex_sql})"

        else:
            parent_sql = self._generate_sql_for_given_traversal_direction_()
            vertex_sql = self._apply_vertex_filters_on_parent_traversal(parent_sql)

            # tbl_prefix = "with" if self.ITERATION_NUM == 1 else ""
            sql = f" {self.RCTE_MAIN_VIEW} as ({vertex_sql})"

        self.REPEAT_QUERY = sql
        return sql

    def _combine_rcte_query_components_(self):
        repeat_traversal_query = self.REPEAT_QUERY
        repeat_times = self.REPEAT_TIMES
        if self.ITERATION_NUM == 1:
            # Meaning that Repeat is called directly, hence the filter here anchor will be VCI query
            anchor_query = self.CENTRIC_QUERY
        else:
            # Else, the anchor is map_id of previous step
            anchor_select = f"select root_id as node_id, oth_id as map_id, {self.ITERATION_NUM} as lvl from {self.RCTE_MAIN_VIEW} base "
            anchor_join = f"inner join level{self.ITERATION_NUM-1} l on l.map_id = base.root_id"
            anchor_query = anchor_select + anchor_join

        rcte_query = f"{anchor_query} \n union all \n \
                select base.root_id, base.oth_id, r.lvl + 1 as lvl from {self.RCTE_MAIN_VIEW} base \
                join {self.RCTE_REPEAT_VIEW} r on base.root_id = r.map_id and lvl < {self.ITERATION_NUM + repeat_times}"

        query = f"{repeat_traversal_query}, \n {self.RCTE_REPEAT_VIEW} as (\n{rcte_query}\n) "
        self.REPEAT_QUERY = query
        return self

    def _generate_repeat_filters_(self):
        traversal = self.REPEAT_STEP.middle_layer[1:]
        print(self.REPEAT_STEP)
        print("===")
        print(traversal)
        print("====")
        print(len(traversal))

        if 1 < len(traversal) <= 3:
            if len(traversal) == 3:
                print("1")
                print(traversal)
                edge_step = traversal[0]
                vertex_step = traversal[1]

                print(f"edge step if \n{edge_step} {type(edge_step)} {len(edge_step.inner_values)}and vertex step \n{vertex_step} {type(vertex_step)} {len(vertex_step.inner_values)}")

                assert type(edge_step) == InnerMostByteCode and type(vertex_step) == InnerMostByteCode
                assert len(edge_step.inner_values) == 3 and len(vertex_step.inner_values) == 3
                print("2")
                edge_step = edge_step.inner_values
                vertex_step = vertex_step.inner_values
                print("3")
                edge_condition = edge_step[2].split(",")
                vertex_condition = vertex_step[2].split(",")
                # edge_property = edge_step[1]
                edge_predicate = edge_condition[0]
                vertex_predicate = vertex_condition[0]
                print(type(edge_condition), "xxxxxx", edge_condition, edge_predicate)

                # if edge_predicate not in ["within", "between", "gte", "lte", "gt", "lt", "eq"]:
                #     value: str = edge_step[2]
                # else:
                value: list = edge_condition[1:]
                self.REPEAT_FILTER["edge"] = {
                    "direction": self.DIRECTION,
                    "property": edge_step[1] if edge_step[1] not in ["T.id", "T.label"] else edge_step[1].split("T.")[1],
                    "value": value,
                    "predicate": edge_predicate
                }

                # if vertex_step[2] not in ["within", "between", "gte", "lte", "gt", "lt", "eq"]:
                #     value: str = vertex_step[2]
                # else:
                value: list = vertex_condition[1:]
                self.REPEAT_FILTER["vertex"] = {
                    "direction": self.DIRECTION,
                    "property": vertex_step[1] if vertex_step[1] not in ["T.id", "T.label"] else vertex_step[1].split("T.")[1],
                    "value": value,
                    "predicate": vertex_predicate
                }
                print("4")

            else:
                print("5")
                vertex_step = traversal[1]
                assert type(vertex_step) == InnerMostByteCode
                assert len(vertex_step.inner_values) == 3
                vertex_step = vertex_step.inner_values
                print("6")

                self.REPEAT_FILTER["vertex"] = {
                    "direction": self.DIRECTION,
                    "property": vertex_step[1] if vertex_step[1] not in ["T.id", "T.label"] else vertex_step[1].split("T.")[1],
                    "value": vertex_step[2]
                }
                print("7")
        else:
            self.ERROR = "Current the Graph supports only 1 hop traversal within REPEAT whereas got more than 1"

        return self

    def _number_of_traversals_in_repeat_(self):
        print(self.REPEAT_STEP.middle_layer[1:])
        trs = [x for x in self.REPEAT_STEP.middle_layer[1:] if len(x.inner_values) > 0]
        return len(trs)

    def _get_repeat_direction_(self):
        traversal = self.REPEAT_STEP.middle_layer[1]
        direction = traversal.inner_values[0]
        print(direction)
        if direction == "out" or direction == "outE":
            self.DIRECTION = "OUT"
        elif direction == "in" or direction == "inE":
            self.DIRECTION = "IN"
        else:
            self.DIRECTION = "BOTH"
        return self

    def __str__(self):
        return "repeat"
