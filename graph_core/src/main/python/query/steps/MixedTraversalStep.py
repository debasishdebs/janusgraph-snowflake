from gen.graphdb_pb2 import MiddleMostByteCode, InnerMostByteCode
from query.steps.TraversalStep import TraversalStep
from query.steps.RepeatStep import RepeatStep
from query.steps.CoalesceStep import CoalesceStep
from query.steps.UnionStep import UnionStep
from typing import List


class MixedTraversalStep(object):
    # REPEAT_STEP = None
    # REPEAT_FILTER = dict()
    # SNOWFLAKE_FN = " call something_here()"
    # DIRECTION = "NA"
    SELECTION_BY = None
    # REPEAT_QUERY = ""
    # REPEAT_TIMES = None
    ERROR = "NA"
    MIXES_STEP_OBJECTS = []
    CENTRIC_QUERY = None
    MIXED_QUERY = None
    VIEWS = []

    def __init__(self, steps: List[List[MiddleMostByteCode]]):
        self.MIXED_QUERY_STEPS = steps

    def total_steps(self):
        return len(self.MIXED_QUERY_STEPS)

    def get_selection_step(self):
        return self.SELECTION_BY

    def with_selection_step(self, step):
        # print("Here")
        self.SELECTION_BY = step
        # print(f"Select by {self.SELECTION_BY}")
        return self

    def execute(self):
        self._convert_query_steps_to_query_objects_()
        # print("Converted query steps to query objects as ")
        # print(self.MIXES_STEP_OBJECTS)

        self._aggregate_steps_()
        # print("Aggregated the queries into single query without project")
        return self

    @staticmethod
    def _is_repeat_step_(step):
        first_step = step[0]
        # print(f"Asserting repeat step \n{first_step}\n with type {type(first_step)}")
        assert type(first_step) == MiddleMostByteCode
        # print("Asserted the type of first step in repeat step as MiddleMostByteCode")

        commands = first_step.middle_layer[0]
        assert type(commands) == InnerMostByteCode

        command = commands.inner_values[0]
        return command.lower() == "repeat"

    @staticmethod
    def _is_coalesce_step_(step):
        first_step = step[0]
        # print(f"Asserting coalesce step \n{first_step}\n with type {type(first_step)}")
        assert type(first_step) == MiddleMostByteCode
        # print("Asserted the type of first step in repeat step as MiddleMostByteCode")

        commands = first_step.middle_layer[0]
        assert type(commands) == InnerMostByteCode

        command = commands.inner_values[0]
        return command.lower() == "coalesce"

    @staticmethod
    def _is_union_step_(step):
        first_step = step[0]
        # print(f"Asserting coalesce step \n{first_step}\n with type {type(first_step)}")
        assert type(first_step) == MiddleMostByteCode
        # print("Asserted the type of first step in repeat step as MiddleMostByteCode")

        commands = first_step.middle_layer[0]
        assert type(commands) == InnerMostByteCode

        command = commands.inner_values[0]
        return command.lower() == "union"

    @staticmethod
    def _is_traversal_step_(step):
        first_step = step[0]
        assert type(first_step) == MiddleMostByteCode
        # print("Asserted the type of first step in traversal step as MiddleMostByteCode")

        commands = first_step.middle_layer[0]
        # print(f"Asserting commands step \n{commands}\n with type {type(commands)}")
        assert type(commands) == InnerMostByteCode

        command = commands.inner_values[0]
        # print("Returning from traversal identifier")
        return command in ["inE", "outE", "bothE", "in", "out", "both"]

    def _convert_query_steps_to_query_objects_(self):
        steps = []
        for step in self.MIXED_QUERY_STEPS:
            assert len(step) <= 2 if not (self._is_coalesce_step_(step) or self._is_union_step_(step)) else len(step) > 0
            # print("Asserted the length of query step as less than 2 for not coalesce step")
            step_dict = dict()
            if self._is_repeat_step_(step):
                step_dict["step"] = "repeat"
                step_dict["query"] = step
                steps.append(step_dict)
                continue

            if self._is_coalesce_step_(step):
                step_dict["step"] = "coalesce"
                step_dict["query"] = step
                steps.append(step_dict)
                continue

            if self._is_union_step_(step):
                step_dict["step"] = "union"
                step_dict["query"] = step
                steps.append(step_dict)
                continue

            if self._is_traversal_step_(step):
                step_dict["step"] = "traversal"
                step_dict["query"] = step
                steps.append(step_dict)
                continue

        step_objects = []
        for step_dict in steps:
            if step_dict["step"] == "repeat":
                obj = RepeatStep(step_dict["query"])
                step_objects.append(obj)
            elif step_dict["step"] == "coalesce":
                obj = CoalesceStep(step_dict["query"])
                step_objects.append(obj)
            elif step_dict["step"] == "union":
                obj = UnionStep(step_dict["query"])
                step_objects.append(obj)
            else:
                obj = TraversalStep(step_dict["query"])
                step_objects.append(obj)

        self.MIXES_STEP_OBJECTS = step_objects
        return self

    def _aggregate_steps_(self):
        aggregated_query = ""

        iter_num = 0
        prev_view = None
        for i in range(len(self.MIXES_STEP_OBJECTS)):
            if iter_num == 0:
                iter_num = i+1

            step = self.MIXES_STEP_OBJECTS[i]

            if str(step) == "traversal":
                traversal_view = "level{lvl}".format(lvl=iter_num)

                step.TRAVERSAL_VIEW = traversal_view
                step.ITERATION_NUM = iter_num
                step.PREVIOUS_VIEW = prev_view if prev_view is not None else 'main'
                step.execute()

                query = step.TRAVERSAL_QUERY
                prev_view = traversal_view
                if traversal_view not in self.VIEWS:
                    # print(f"Current view inside traversal is {traversal_view} and total till now {self.VIEWS}")
                    self.VIEWS.append(traversal_view)

                # print(f"Executed {iter_num}th traversal with curr view {traversal_view} and prev view {prev_view}")
                iter_num += 1

            elif str(step) == "coalesce":
                coalesce_view = "level{lvl}".format(lvl=iter_num)

                step.COALESCE_VIEW = coalesce_view
                step.ITERATION_NUM = iter_num
                step.PREVIOUS_VIEW = prev_view if prev_view is not None else "main"
                step.execute()
                # print(f"The previous view before executing is {prev_view if prev_view is not None else 'main'}")

                query = step.COALESCE_QUERY
                prev_view = coalesce_view
                if coalesce_view not in self.VIEWS:
                    # print(f"Current view inside traversal is {coalesce_view} and total till now {self.VIEWS}")
                    self.VIEWS.append(coalesce_view)

                # print(f"Executed {iter_num}th traversal with curr view {coalesce_view} and prev view {prev_view}")
                iter_num += 1

            elif str(step) == "union":
                union_view = "level{lvl}".format(lvl=iter_num)

                step.UNION_VIEW = union_view
                step.ITERATION_NUM = iter_num
                step.PREVIOUS_VIEW = prev_view if prev_view is not None else "main"
                step.execute()
                # print(f"The previous view before executing is {prev_view if prev_view is not None else 'main'}")

                query = step.UNION_QUERY
                prev_view = union_view
                if union_view not in self.VIEWS:
                    # print(f"Current view inside traversal is {union_view} and total till now {self.VIEWS}")
                    self.VIEWS.append(union_view)

                # print(f"Executed {iter_num}th traversal with curr view {union_view} and prev view {prev_view}")
                iter_num += 1

            else:
                repeat_view = "repeat{lvl}".format(lvl=iter_num)
                repeat_rcte_view = "repeat{lvl}_rcte".format(lvl=iter_num)

                step.RCTE_MAIN_VIEW = repeat_view
                step.RCTE_REPEAT_VIEW = repeat_rcte_view
                step.ITERATION_NUM = iter_num
                step.CENTRIC_QUERY = self.CENTRIC_QUERY
                step.execute()

                prev_view = repeat_rcte_view
                if repeat_rcte_view not in self.VIEWS:
                    # print(f"Current view inside traversal is {repeat_rcte_view} and total till now {self.VIEWS}")
                    self.VIEWS.append(repeat_rcte_view)

                query = step.REPEAT_QUERY
                # print(f"Executed {iter_num}th repeat with curr view {repeat_rcte_view}, repeat_times: {step.REPEAT_TIMES}")
                iter_num += step.REPEAT_TIMES

            if aggregated_query == "":
                aggregated_query += f"with main as ({self.CENTRIC_QUERY}), \n"
            aggregated_query += query
            aggregated_query += "\n"
            if i < len(self.MIXES_STEP_OBJECTS)-1:
                # print("Added comma to " + aggregated_query)
                aggregated_query += ","
            # if i == len(self.MIXES_STEP_OBJECTS):
            # Stripping off the last comma and removing the duplicate commas
        # print("Computed the aggregated query removing queryu now")
        # print(aggregated_query[-1])
        # print("===")
        # print(aggregated_query[-2:])
        # print("===")
        # print(aggregated_query[-1] == ",")
        # print(aggregated_query[-1] == "\n")
        # print(aggregated_query[-2:] == ",\n")

        if aggregated_query[-2:] == ",\n":
            aggregated_query = aggregated_query[:-2]
            aggregated_query += "\n"
        # print(aggregated_query[-10:])

        self.MIXED_QUERY = aggregated_query
        return self
    #
    # def _get_repeat_times_(self):
    #     repeat_times_step = self.REPEAT_STEP.middle_layer[-1]
    #     times = repeat_times_step.inner_values[1]
    #     self.REPEAT_TIMES = times
    #     return self
    #
    # def _generate_sql_for_given_traversal_direction_(self):
    #     if self.DIRECTION == "OUT":
    #         sql = "select node_id as root_id, value_id as edge_id, \
    #         'outgoing' as edge_direction, value_label as edge_label, value_properties as edge_properties, \
    #         map_id as oth_id from nodes_with_edges_all "
    #
    #     elif self.DIRECTION == "IN":
    #         sql = "select node_id as oth_id, value_id as edge_id, \
    #         'incoming' as edge_direction, value_label as edge_label, value_properties as edge_properties, \
    #         map_id as root_id from nodes_with_edges_all "
    #
    #     else:
    #         sql = "select node_id as root_id, value_id as edge_id, \
    #         'outgoing' as edge_direction, value_label as edge_label, value_properties as edge_properties, \
    #         map_id as oth_id from nodes_with_edges_all\n"
    #
    #         sql += "union all\n"
    #
    #         sql += "select node_id as oth_id, value_id as edge_id, \
    #         'incoming' as edge_direction, value_label as edge_label, value_properties as edge_properties, \
    #         map_id as root_id from nodes_with_edges_all "
    #
    #     return sql

    # def _apply_vertex_filters_on_parent_traversal(self, parent_sql):
    #     sql = f"select root_id, edge_id, edge_label, edge_properties, oth_id \
    #         from ({parent_sql}) ne inner join nodes_master nm on nm.node_id = oth_id"
    #
    #     if self.REPEAT_FILTER["vertex"]["value"] != "":
    #         prop = self.REPEAT_FILTER["vertex"]["property"]
    #         val = self.REPEAT_FILTER["vertex"]["value"]
    #
    #         condtn = f" where nm.properties:{prop} = {val}"
    #         sql += condtn
    #     return sql
    #
    # def _apply_edge_vertex_filters_on_parent_traversal_(self, edge_parent_sql):
    #     sql = f"select root_id, edge_direction, edge_id, edge_label, edge_properties, oth_id \
    #         from nodes_master nm, ({edge_parent_sql}) ne where nm.node_id = ne.oth_id"
    #
    #     if self.REPEAT_FILTER["vertex"]["value"] != "":
    #         prop = self.REPEAT_FILTER["vertex"]["property"]
    #         val = self.REPEAT_FILTER["vertex"]["value"]
    #
    #         condtn = f" where nm.properties:{prop} = {val}"
    #         sql += condtn
    #     return sql

    # def _apply_edge_filters_on_parent_traversal_(self, root_sql):
    #     if self.DIRECTION != "BOTH":
    #         if self.REPEAT_FILTER["edge"]["value"] != "":
    #             prop = self.REPEAT_FILTER["edge"]["property"]
    #             val = self.REPEAT_FILTER["edge"]["value"]
    #
    #             condtn = f" where edge_properties:{prop} = {val}"
    #             root_sql += condtn
    #     else:
    #         if self.REPEAT_FILTER["edge"]["value"] != "":
    #             prop = self.REPEAT_FILTER["edge"]["property"]
    #             val = self.REPEAT_FILTER["edge"]["value"]
    #
    #             condition_sql = f"select * \
    #                     from ({root_sql}) where edge_properties:{prop} = {val}"
    #             root_sql = condition_sql
    #
    #     return root_sql

    # def _generate_filter_query_(self):
    #     print("Generating filter query")
    #
    #     if "edge" in self.REPEAT_FILTER:
    #
    #         edge_parent_sql = self._generate_sql_for_given_traversal_direction_()
    #         edge_sql = self._apply_edge_filters_on_parent_traversal_(edge_parent_sql)
    #         edge_vertex_sql = self._apply_edge_vertex_filters_on_parent_traversal_(edge_sql)
    #
    #         sql = f" with edges as ({edge_vertex_sql})"
    #         print(sql)
    #
    #     else:
    #         parent_sql = self._generate_sql_for_given_traversal_direction_()
    #         vertex_sql = self._apply_vertex_filters_on_parent_traversal(parent_sql)
    #
    #         sql = f" with edges as ({vertex_sql})"
    #
    #     self.REPEAT_QUERY = sql
    #     return sql

    # def _generate_repeat_filters_(self):
    #     traversal = self.REPEAT_STEP.middle_layer[1:]
    #
    #     if 1 < len(traversal) <= 3:
    #         if len(traversal) == 3:
    #             print("1")
    #             print(traversal)
    #             edge_step = traversal[0]
    #             vertex_step = traversal[1]
    #
    #             print(f"edge step if \n{edge_step} {type(edge_step)} {len(edge_step.inner_values)}and vertex step \n{vertex_step} {type(vertex_step)} {len(vertex_step.inner_values)}")
    #
    #             assert type(edge_step) == InnerMostByteCode and type(vertex_step) == InnerMostByteCode
    #             assert len(edge_step.inner_values) == 3 and len(vertex_step.inner_values) == 3
    #             print("2")
    #             edge_step = edge_step.inner_values
    #             vertex_step = vertex_step.inner_values
    #             print("3")
    #
    #             self.REPEAT_FILTER["edge"] = {
    #                 "direction": self.DIRECTION,
    #                 "property": edge_step[1] if edge_step[1] not in ["T.id", "T.label"] else edge_step[1].split("T.")[1],
    #                 "value": edge_step[2]
    #             }
    #
    #             self.REPEAT_FILTER["vertex"] = {
    #                 "direction": self.DIRECTION,
    #                 "property": vertex_step[1] if vertex_step[1] not in ["T.id", "T.label"] else vertex_step[1].split("T.")[1],
    #                 "value": vertex_step[2]
    #             }
    #             print("4")
    #
    #         else:
    #             print("5")
    #             vertex_step = traversal[1]
    #             assert type(vertex_step) == InnerMostByteCode
    #             assert len(vertex_step.inner_values) == 3
    #             vertex_step = vertex_step.inner_values
    #             print("6")
    #
    #             self.REPEAT_FILTER["vertex"] = {
    #                 "direction": self.DIRECTION,
    #                 "property": vertex_step[1] if vertex_step[1] not in ["T.id", "T.label"] else vertex_step[1].split("T.")[1],
    #                 "value": vertex_step[2]
    #             }
    #             print("7")
    #     else:
    #         self.ERROR = "Current the Graph supports only 1 hop traversal within REPEAT whereas got more than 1"
    #
    #     return self

    # def _number_of_traversals_in_repeat_(self):
    #     print(self.REPEAT_STEP.middle_layer[1:])
    #     trs = [x for x in self.REPEAT_STEP.middle_layer[1:] if len(x.inner_values) > 0]
    #     return len(trs)

    # def _get_repeat_direction_(self):
    #     traversal = self.REPEAT_STEP.middle_layer[1]
    #     direction = traversal.inner_values[0]
    #     print(direction)
    #     if direction == "out" or direction == "outE":
    #         self.DIRECTION = "OUT"
    #     elif direction == "in" or direction == "inE":
    #         self.DIRECTION = "IN"
    #     else:
    #         self.DIRECTION = "BOTH"
    #     return self
