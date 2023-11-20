from query.steps.RepeatStep import RepeatStep
from query.steps.MixedTraversalStep import MixedTraversalStep
from query.steps.PropertiesStep import PropertiesStep
from query.steps.TraversalIdStep import TraversalIdStep
from query.steps.IteratationStepWrapper import IterationStepWrapper
from gen.graphdb_pb2 import MiddleMostByteCode
from query.steps.ProjectStep import ProjectStep
from google.protobuf.json_format import MessageToDict
from utils.utils import Utilities as U


class VertexCentricStep(object):
    FILTER_QUERY = None
    ERROR = "NA"
    ROOT_ELEMENT = None
    ITERATION_NUM = 1
    SELECTION_BY = None
    HOPS = 1

    def __init__(self, bytecode):
        self.QUERY = bytecode
        self.STEPS = bytecode.steps
        # print(f"8a: The query is being executed is {MessageToDict(self.QUERY)}")
        # print(f"8b: The query is being executed is {MessageToDict(self.QUERY).keys()}")
        # print(f"8c: The query is being executed is {self.STEPS}")

        self.ROOT_FILTERS = None
        self.ROOT_TRAVERSAL = None
        self.ROOT_UNION_COALSCE_TRAVERSAL = {
            "union": [],
            "coalesce": []
        }

        from utils.common_resources import Commons
        self.master = Commons.MASTER_TABLE
        self.edges = Commons.EDGES_TABLE

    def add_root_filters(self, filters: dict):
        self.ROOT_FILTERS = filters
        print(f"Root filters are {filters}")
        return self

    def add_root_traversal(self, traversal: list):
        self.ROOT_TRAVERSAL = traversal
        print(f"Root traversal are {traversal}")
        return self

    def add_union_coalesce_traversals(self, union, coalesce):
        if len(union) > 0:
            self.ROOT_UNION_COALSCE_TRAVERSAL["union"] = union
        if len(coalesce) > 0:
            self.ROOT_UNION_COALSCE_TRAVERSAL["coalesce"] = coalesce
        return self

    def execute(self):
        self.HOPS = self._generate_hops_()
        print(f"9: The number of hops is {self.HOPS}")
        # self.generate_vci_filter_query()

    def get_query(self):
        return self.FILTER_QUERY

    def generate_vci_filter_query(self):
        print(f"A: Generating VCI Filter query for {self.ROOT_FILTERS} and type {type(self.ROOT_FILTERS)}")
        print(f"Root traversals is {self.ROOT_TRAVERSAL}")

        direction = self._get_traversal_edge_direction_(self.ROOT_TRAVERSAL)
        direction = direction if direction is not "VCI" else "OUT"

        if len(self.ROOT_UNION_COALSCE_TRAVERSAL["union"]) == 0 and \
                len(self.ROOT_UNION_COALSCE_TRAVERSAL["coalesce"]) == 0:

            if direction == "BOTH":
                select_query = " select distinct ne.node_id as node_id, ne.map_id as map_id, '1' as lvl, ne.value_id, 'out' as direction, ne.value_label, ne.value_properties " \
                               f"\nfrom {self.edges} ne " + " \n{join_out} \n{root_filter_out} "
                select_query += "\n\t union all \n"
                select_query += " select distinct ne.map_id as node_id, ne.node_id as map_id, '1' as lvl, ne.value_id, 'in' as direction, ne.value_label, ne.value_properties " \
                                f"\nfrom {self.edges} ne " + " \n{join_in} \n{root_filter_in} "

            elif direction == "OUT":
                select_query = " select distinct ne.node_id as node_id, ne.map_id as map_id, '1' as lvl, ne.value_id, 'out' as direction, ne.value_label, ne.value_properties " \
                                   f"\nfrom {self.edges} ne " + " \n{join_out} \n{root_filter_out} "

            else:
                select_query = " select distinct ne.map_id as node_id, ne.node_id as map_id, '1' as lvl, ne.value_id, 'in' as direction, ne.value_label, ne.value_properties " \
                                    f"\nfrom {self.edges} ne " + " \n{join_in} \n{root_filter_in} "

            filter_dict = U.generate_filter_query_for_condition(self.ROOT_FILTERS["root_filter"],
                                                                self.ROOT_FILTERS["edge_filter"],
                                                                self.ROOT_FILTERS["dst_filter"], direction)

            # print(filter_dict)

            join_dict = U.generate_join_query_for_condition(direction, self.master, self.ROOT_FILTERS["root_filter"],
                                                            self.ROOT_FILTERS["dst_filter"])

            # print("The join condition is ")
            # print(join_dict)

            if direction == "OUT":
                out_query = filter_dict["OUT"]
                join_query = join_dict["OUT"]

                query = select_query.format(root_filter_out=out_query, join_out=join_query)
            elif direction == "IN":
                in_query = filter_dict["IN"]
                join_query = join_dict["IN"]

                query = select_query.format(root_filter_in=in_query, join_in=join_query)
            else:
                out_query = filter_dict["OUT"]
                in_query = filter_dict["IN"]
                join_out_query = join_dict["OUT"]
                join_in_query = join_dict["IN"]
                # edge_query = query_dict["EDGE"]

                query = select_query.format(root_filter_out=out_query, root_filter_in=in_query, join_in=join_in_query,
                                            join_out=join_out_query)

            # print("VCI query ", query)
            # print("======")

        else:
            if len(self.ROOT_UNION_COALSCE_TRAVERSAL["union"]) > 0:
                # print(f"Verifying len union: {len(self.ROOT_UNION_COALSCE_TRAVERSAL['union'])}, coalesce: {len(self.ROOT_UNION_COALSCE_TRAVERSAL['coalesce'])} inside union")

                union_steps = self.ROOT_UNION_COALSCE_TRAVERSAL["union"]
                from query.steps.UnionStep import UnionStep
                step = UnionStep(union_steps)
                union_view = "root"

                step.UNION_VIEW = union_view
                step.VCI_FILTER = self.ROOT_FILTERS
                step.ITERATION_NUM = 1
                step.execute()

                query = step.UNION_QUERY

            else:
                # print(f"Verifying len union: {len(self.ROOT_UNION_COALSCE_TRAVERSAL['union'])}, coalesce: {len(self.ROOT_UNION_COALSCE_TRAVERSAL['coalesce'])} inside coalesce")

                coalesce_steps = self.ROOT_UNION_COALSCE_TRAVERSAL["coalesce"]
                from query.steps.CoalesceStep import CoalesceStep
                step = CoalesceStep(coalesce_steps)
                coalesce_view = "root"

                step.COALESCE_VIEW = coalesce_view
                step.VCI_FILTER = self.ROOT_FILTERS
                step.ITERATION_NUM = 1
                step.execute()

                query = step.COALESCE_QUERY

        self.FILTER_QUERY = query
        return self

    def get_iteration_step(self):
        print("Root filters are ", self.ROOT_FILTERS)
        # print("Centric query before execution is ", self.FILTER_QUERY)
        self.generate_vci_filter_query()
        # print("Centric query after execution is ", self.FILTER_QUERY)

        iterate_step = self._identify_traversal_type_()
        print(f"Iterate step is {iterate_step}")

        selection_step = self._generate_selection_type_()
        print(f"Selection step is {selection_step}")

        iterate_step.with_selection_step(selection_step)
        print("Returning")

        return iterate_step

    def get_selection_step(self):
        return self.SELECTION_BY

    def with_selection_step(self, step):
        print("Here")
        self.SELECTION_BY = step
        print(f"Select by {self.SELECTION_BY}")
        return self

    def _generate_selection_type_(self):
        ty_type = self._identify_traversal_end_step_()
        print("Traversal end step is ", ty_type)
        if ty_type == "Project":
            return ProjectStep(self.QUERY)
        if ty_type == "Properties":
            return PropertiesStep(self.QUERY)
        if ty_type == "Traversal":
            return TraversalIdStep(self.QUERY)

        self.ERROR = "Currently supports Project as only Select step. Got " + str(ty_type)
        return

    def _generate_hops_(self):
        hops = 0
        prev_edge_step = False

        for step in self.STEPS:
            assert type(step) == MiddleMostByteCode

            # print(f"Current step is {step.middle_layer}")

            if self._is_root_element_(step.middle_layer):
                # print(f"Root step ignoring")
                continue

            tr_type = ProjectStep.identify_type_of_traversal(step.middle_layer)
            if tr_type == "Edge":
                if prev_edge_step:
                    self.ERROR = "Invalid traversal. You can't add EdgeTraversal to another EdgeTraversal"
                else:
                    hops += 1
                    prev_edge_step = True

                # print(f"Current traversal type is Edge and Previous edge status is {prev_edge_step} "
                #       f"for step {step.middle_layer} & updated hops {hops}")

            elif tr_type == "Vertex":
                # print(f"Current traversal type is Vertex and Previous edge status is {prev_edge_step}"
                      # f" for step {step.middle_layer} & updated hops {hops}")
                #
                if not prev_edge_step:
                    prev_edge_step = False
                    hops += 1
                else:
                    prev_edge_step = False
                    continue

            else: continue

        # print(hops)
        # print('-----')
        return hops

    def _is_root_element_(self, step):
        if step[0].inner_values[0] == "E" or step[0].inner_values[0] == "V":
            # print(f"Root element is {step}")
            self.ROOT_ELEMENT = step
            return True
        return False

    @staticmethod
    def _is_project_element_(step):
        if step[0].inner_values[0] == "project":
            return True
        return False

    @staticmethod
    def _is_repeat_element_(step):
        if step[0].inner_values[0] == "repeat":
            return True
        return False

    @staticmethod
    def _is_coalesce_element_(step):
        if step[0].inner_values[0] == "coalesce":
            return True
        return False

    @staticmethod
    def _is_union_element_(step):
        if step[0].inner_values[0] == "union":
            return True
        return False

    @staticmethod
    def _is_edge_vertex_traversal_element_(step):
        if step[0].inner_values[0] in ["both", "in", "out"]:
            return True
        return False

    @staticmethod
    def _is_deduplicate_element_(step):
        if step[0].inner_values[0] in ["dedup"]:
            return True
        return False

    @staticmethod
    def _is_limiting_element_(step):
        if step[0].inner_values[0] in ["limit"]:
            return True
        return False

    @staticmethod
    def _is_count_element_(step):
        if step[0].inner_values[0] in ["count"]:
            return True
        return False

    @staticmethod
    def _is_properties_element_(step):
        if step[0].inner_values[0] in ["properties"]:
            return True
        return False

    def _condense_steps_(self):
        steps = []
        i = 0

        # print("Union traversals till now")
        # print(self.ROOT_UNION_COALSCE_TRAVERSAL["union"])
        # print("Coalesce traversals for now")
        # print(self.ROOT_UNION_COALSCE_TRAVERSAL["coalesce"])

        while i < len(self.STEPS):
            step = self.STEPS[i]

            # print("Checking if the current step is part of already added root_traversals")
            # print(step)
            # print(i, len(self.ROOT_TRAVERSAL))
            # print("Root traversal")
            # print(self.ROOT_TRAVERSAL)
            if step in self.ROOT_TRAVERSAL and i < len(self.ROOT_TRAVERSAL):
                # print("Yes, step is part of root traversal. Continue")
                i += 1
                continue

            if step in self.ROOT_UNION_COALSCE_TRAVERSAL["union"]:
                # print("The above step was found as part of ROOT union traversal. Continue")
                i += 1
                continue

            if step in self.ROOT_UNION_COALSCE_TRAVERSAL["coalesce"]:
                # print("The above step was found as part of ROOT coalesce traversal. Continue")
                i += 1
                continue

            # print(f"Step at {i} is not part of traversal so going to condense")

            is_traversal_step, step_type = self._is_edge_edge_vertex_traversal_element_(step.middle_layer)
            if is_traversal_step:
                if step_type in ["inE", "outE", "bothE"]:
                    curr_step = step
                    next_step = self.STEPS[i+1]
                    i += 2
                    steps.append([curr_step, next_step])

                else:
                    steps.append([step])
                    i += 1
            else:
                if step.middle_layer[0].inner_values[0] == "coalesce":
                    j = i
                    coalesce_steps = []
                    while j < len(self.STEPS):
                        curr_step = self.STEPS[j]
                        if curr_step.middle_layer[0].inner_values[0] != "coalesce":
                            break
                        coalesce_steps.append(curr_step)
                        j += 1
                    steps.append(coalesce_steps)
                    i = j
                elif step.middle_layer[0].inner_values[0] == "union":
                    j = i
                    union_steps = []
                    while j < len(self.STEPS):
                        curr_step = self.STEPS[j]
                        if curr_step.middle_layer[0].inner_values[0] != "union":
                            break
                        union_steps.append(curr_step)
                        j += 1
                    steps.append(union_steps)
                    i = j
                else:
                    steps.append([step])
                    i += 1
        return steps

    @staticmethod
    def _get_traversal_edge_direction_(traversal):
        # print(len(traversal))

        if len(traversal) > 1:
            if traversal[1].middle_layer[0].inner_values[0] in ["both", "bothE"]:
                return "BOTH"
            if traversal[1].middle_layer[0].inner_values[0] in ["out", "outE"]:
                return "OUT"
            if traversal[1].middle_layer[0].inner_values[0] in ["in", "inE"]:
                return "IN"
        else:
            return "VCI"

    @staticmethod
    def _is_edge_edge_vertex_traversal_element_(tr_step):
        if tr_step[0].inner_values[0] in ["inE", "outE", "bothE", "in", "out", "both"]:
            return True, tr_step[0].inner_values[0]
        return False, "NA"

    def _mutate_traversals_into_dict_(self, traversals):
        traversal_dict = dict()
        for i in range(len(traversals)):
            traversal = traversals[i]
            traversal_type = self._identify_type_of_traversal_step_([traversal])
            assert (traversal_type != "ROOT") or (traversal_type != "Mixed")
            traversal_dict[i] = {
                "type": self._identify_type_of_traversal_step_([traversal]).lower(),
                "traversal": traversal
            }

        return traversal_dict

    def _identify_type_of_traversal_step_(self, steps):
        repeat_step = False
        traversal_step = False
        coalesce_step = False
        union_step = False

        # print(f"identifying the traversal type for {steps}")
        for step in steps:
            for substep in step:
                if self._is_repeat_element_(substep.middle_layer):
                    # print(f"I'm repeat element : {substep.middle_layer}")
                    repeat_step = True
                    continue

                if self._is_coalesce_element_(substep.middle_layer):
                    # print(f"I'm coalesce element : {substep.middle_layer}")
                    coalesce_step = True
                    continue

                if self._is_union_element_(substep.middle_layer):
                    # print(f"I'm union element : {substep.middle_layer}")
                    union_step = True
                    continue

                if self._is_edge_edge_vertex_traversal_element_(substep.middle_layer)[0]:
                    # print(f"I'm traversal element : {substep.middle_layer}")
                    traversal_step = True
                    continue

        if repeat_step:
            if traversal_step:
                if coalesce_step:
                    if union_step:
                        return "Mixed"
                    else:
                        return "Mixed"
                else:
                    if union_step:
                        return "Mixed"
                    else:
                        return "Mixed"
            else:
                if coalesce_step:
                    if union_step:
                        return "Mixed"
                    else:
                        return "Mixed"
                else:
                    if union_step:
                        return "Mixed"
                    else:
                        return "Repeat"
        else:
            if traversal_step:
                if coalesce_step:
                    if union_step:
                        return "Mixed"
                    else:
                        return "Mixed"
                else:
                    if union_step:
                        return "Mixed"
                    else:
                        return "Traversal"
            else:
                if coalesce_step:
                    if union_step:
                        return "Mixed"
                    else:
                        return "Coalesce"
                else:
                    if union_step:
                        return "Union"
                    else:
                        return "ROOT"

    def _identify_traversal_type_(self):
        traversals = []
        # print("Identifying the traversal type for steps:")
        #
        # print(100*"=")

        condensed_steps = self._condense_steps_()
        # print("Steps got condensed and are as follows")
        # print(condensed_steps)

        for step in condensed_steps:
            if len(step) == 1:
                if self._is_root_element_(step[0].middle_layer):
                    # print("Root step encountered while computing ITERATION step, ignoring")
                    print("ERROR ERROR ERROR: I should not have got a root step here. Strange I got it!!!!")
                    continue

                if self._is_project_element_(step[0].middle_layer):
                    # print("Project step encountered while computing ITERATION step, ignoring")
                    continue

                if self._is_repeat_element_(step[0].middle_layer):
                    # print("Got repeat element continue")
                    traversals.append(step)
                    continue

                if self._is_coalesce_element_(step[0].middle_layer):
                    # print("Got coalesce element continue")
                    traversals.append(step)
                    continue

                if self._is_union_element_(step[0].middle_layer):
                    # print("Got union element continue")
                    traversals.append(step)
                    continue

                if self._is_edge_vertex_traversal_element_(step[0].middle_layer):
                    # print("Got traversal element continue")
                    traversals.append(step)
                    continue

                if self._is_deduplicate_element_(step[0].middle_layer):
                    # print("Got deduplicate element continue")
                    traversals.append(step)
                    continue

                if self._is_limiting_element_(step[0].middle_layer):
                    # print("Got limit element continue")
                    traversals.append(step)
                    continue

                if self._is_count_element_(step[0].middle_layer):
                    # print("Got count element continue")
                    traversals.append(step)
                    continue

                if self._is_properties_element_(step[0].middle_layer):
                    # print("Got properties element continue")
                    traversals.append(step)
                    continue

                print(f"ERROR: Strange that the length of traversal is 1, but got an element which is neither "
                      f"root/project/repeat/both/in/out/dedup/limit/properties. Got \n{step[0].middle_layer}")
                self.ERROR = f"ERROR: Strange that the length of traversal is 1, but got an element which is neither \
                root/project/repeat/both/in/out/dedup/limit/properties. Got \n{step[0].middle_layer}"
                # raise ValueError("Strange that the length of traversal is 1, but got an element which is neither "
                #                  "root/project/repeat/both/in/out/dedup/limit. Got ", step[0].middle_layer)

            else:
                if len(step) == 2:
                    first_step = step[0]
                    if first_step.middle_layer[0].inner_values[0] in ["bothE", "inE", "outE"]:
                        traversals.append(step)
                        continue
                    elif first_step.middle_layer[0].inner_values[0] in ["coalesce", "union"]:
                        traversals.append(step)
                        continue
                else:
                    # Meaning that, it can only be coalesce/union step for now
                    for s in step:
                        assert s.middle_layer[0].inner_values[0] in ["coalesce", "union"]
                    traversals.append(step)
                    continue

                print(f"ERROR: Strange that the length of traversal is {len(step)}. Max should be 2 for step \n{step}\n=====")
                raise ValueError(f"ERROR: Strange that the length of traversal is {len(step)}. Max should be 2")

        # print(f"For root step as : \n{self.ROOT_ELEMENT}, \nfollowing are the traversals applied on it")
        # for traversal in traversals:
            # print(f"Traversal is: \n{traversal}\n")
            # print("=====")

        traversal_type = self._identify_type_of_traversal_step_(traversals)
        traversal_dict = self._mutate_traversals_into_dict_(traversals)
        print("The traversal type identified is ", traversal_type)
        # print(f"Generated traversal dict as follows: {traversal_dict}")

        if traversal_type == "Mixed":
            return IterationStepWrapper(mixed_step=MixedTraversalStep(traversals)).add_centric_step(self)

        elif traversal_type == "Repeat":
            iteration_wrapper = IterationStepWrapper()
            for i in range(len(traversal_dict)):
                step = traversal_dict[i]
                if step["type"] == "repeat":
                    iteration_wrapper.add_repeat_step(step["traversal"])
            return iteration_wrapper.add_centric_step(self)

        elif traversal_type == "Traversal":
            iteration_wrapper = IterationStepWrapper()
            for i in range(len(traversal_dict)):
                step = traversal_dict[i]
                if step["type"] == "traversal":
                    # print(f"Adding traversal step ======\n{step['traversal']}\n in idx {i}========")
                    iteration_wrapper.add_traversal_step(step["traversal"])
            return iteration_wrapper.add_centric_step(self)

        elif traversal_type == "Coalesce":
            iteration_wrapper = IterationStepWrapper()
            for i in range(len(traversal_dict)):
                step = traversal_dict[i]
                if step["type"] == "coalesce":
                    # print(f"Adding coalesce step ======\n{step['traversal']}\n in idx {i}========")
                    iteration_wrapper.add_coalesce_step(step["traversal"])
            return iteration_wrapper.add_centric_step(self)

        elif traversal_type == "Union":
            iteration_wrapper = IterationStepWrapper()
            for i in range(len(traversal_dict)):
                step = traversal_dict[i]
                if step["type"] == "union":
                    # print(f"Adding union step ======\n{step['traversal']}\n in idx {i}========")
                    iteration_wrapper.add_union_step(step["traversal"])
            return iteration_wrapper.add_centric_step(self)

        else:
            # print(f"Traversal type is {traversal_type}")
            assert traversal_type == "ROOT"
            return self

    def _identify_traversal_end_step_(self):
        for step in self.STEPS:
            # Step is basically list of Inner steps
            step_type = step.middle_layer[0].inner_values[0]
            # print("Step is ")
            # print(step)
            # print(f"Step type: {step_type} and equality with project {step_type=='project'}, with path {step_type=='path'}, with properties: {step_type=='properties'}")
            if step_type == "project":
                return "Project"
            if step_type == "path":
                return "Path"
            if step_type == "properties":
                return "Properties"

        return "Traversal"
