from gen.graphdb_pb2 import ByteCode, MiddleMostByteCode
from query.steps.VertexCentricStep import VertexCentricStep


class QueryParser(object):

    def __init__(self, bytecode):
        print("1: Parsing the bytecode")
        self.ROOT_FILTERS = dict()
        self.ROOT_TRAVERSAL = []
        self.QUERY = None
        self.UNION_TRAVERSALS = []
        self.COALESCE_TRAVERSALS = []
        assert type(bytecode) == ByteCode
        # print("a")
        self.QUERY = bytecode
        self._identify_root_traversal_()
        # print("c")
        self._generate_root_filters_()
        # print("b")

    def get_query_type(self):
        query_type = self._calculate_query_type_()
        if query_type in ["VertexCentric", "EdgeCentric"]:
            return "read"
        elif query_type in ["VertexAdd", "EdgeAdd", "MixedElementAdd"]:
            return "write"

    def get_centric_query(self):
        centric = self._calculate_centric_type_query_()
        # print(f"6: Centric is {centric}")
        if centric == "VertexCentric":
            # print(f"7: Root filters are {self.ROOT_FILTERS} & {len(self.ROOT_FILTERS)}")
            # assert len(self.ROOT_FILTERS) > 0
            return VertexCentricStep(self.QUERY).add_root_filters(self.ROOT_FILTERS).\
                add_root_traversal(self.ROOT_TRAVERSAL).\
                add_union_coalesce_traversals(union=self.UNION_TRAVERSALS, coalesce=self.COALESCE_TRAVERSALS)

        return self

    def get_element_addition_query(self):
        query_type = self._calculate_query_type_()

        if query_type == "VertexAdd":
            from query.steps.AddVertexStep import AddVertexStep
            return AddVertexStep(self.QUERY)
        if query_type == "EdgeAdd":
            from query.steps.AddEdgeStep import AddEdgeStep
            return AddEdgeStep(self.QUERY)

        return

    def _calculate_centric_type_query_(self):
        root_step = self.QUERY.steps[0]
        assert type(root_step) == MiddleMostByteCode
        root_step_info = root_step.middle_layer

        if root_step_info[0].inner_values[0] == "V":
            return "VertexCentric"
        elif root_step_info[0].inner_values[0] == "E":
            return "EdgeCentric"
        return "NA"

    def _calculate_query_type_(self):
        root_step = self.QUERY.steps[0]
        assert type(root_step) == MiddleMostByteCode
        root_step_info = root_step.middle_layer

        if root_step_info[0].inner_values[0] == "V":
            return "VertexCentric"

        elif root_step_info[0].inner_values[0] == "E":
            return "EdgeCentric"

        elif root_step_info[0].inner_values[0] == "AddVertex":
            for middle in root_step_info[1:]:
                if middle.inner_values[0] == "AddEdge":
                    return "MixedElementAdd"
            return "VertexAdd"

        elif root_step_info[0].inner_values[0] == "AddEdge":
            for middle in root_step_info[1:]:
                if middle.inner_values[0] == "AddVertex":
                    return "MixedElementAdd"
            return "EdgeAdd"

        return "NA"

    def _generate_root_filters_(self):
        print("generating root filter")
        print(self.ROOT_TRAVERSAL[-1])
        print("------------------")
        root_step = self.ROOT_TRAVERSAL[0]
        edge_step = self.ROOT_TRAVERSAL[1] if len(self.ROOT_TRAVERSAL) == 3 else None
        dst_step = self.ROOT_TRAVERSAL[-1] if len(self.ROOT_TRAVERSAL) > 1 else None

        # print("cc")
        assert type(root_step) == MiddleMostByteCode
        # print("c")
        # print("Root step ", root_step, type(root_step))
        # print("Edge step ", edge_step, type(edge_step))
        # print("dst ste ", dst_step, type(dst_step))

        self.ROOT_FILTERS = {
            "root_filter": {},
            "edge_filter": {},
            "dst_filter": {}
        }

        i = 0
        for step in root_step.middle_layer:
            print(f"For step {step}")
            if i == 0:
                i += 1
                # Ignoring the root step
                continue

            prop_name = step.inner_values[0]
            prop_name = prop_name if prop_name not in ["T.id", "T.label", "T.caseId"] else prop_name.split("T.")[1]
            prop_val = step.inner_values[1:]
            print(f"Propname: {prop_name} and value: {prop_val}")

            # print(prop_name, prop_val)
            if prop_val[0] == "within":
                # print("Got within predicate inside root_step, joining it")
                prop_val = [",".join(prop_val)]

            if len(prop_val) == 1:
                self.ROOT_FILTERS["root_filter"][prop_name] = prop_val[0]
            else:
                self.ROOT_FILTERS["root_filter"][prop_name] = prop_val
            i += 1

            print(f"Root filters root step {i}", self.ROOT_FILTERS)

        print(f"Generated root filters {self.ROOT_FILTERS}")
        i = 0
        if edge_step is not None:
            for step in edge_step.middle_layer:
                print(f"For edge step {step}")
                if i == 0:
                    i += 1
                    # Ignoring the base step
                    continue

                if len(step.inner_values) > 0:
                    prop_name = step.inner_values[0]
                    prop_name = prop_name if prop_name not in ["T.id", "T.label"] else prop_name.split("T.")[1]
                    prop_val = step.inner_values[1:]
                    print(f"Edge step prop name: {prop_name} and value {prop_val}")

                    # print(prop_name, prop_val)
                    if prop_val[0] == "within":
                        # print("Got within predicate inside edge_step, joining it")
                        prop_val = [",".join(prop_val)]

                    if len(prop_val) == 1:
                        self.ROOT_FILTERS["edge_filter"][prop_name] = prop_val[0]
                    else:
                        self.ROOT_FILTERS["edge_filter"][prop_name] = prop_val
                    i += 1

                print(f"Root filters edge step {i}", self.ROOT_FILTERS)
        i = 0
        # print(dst_step.middle_layer)
        if dst_step is not None:
            for step in dst_step.middle_layer:
                print(f"For vertex step {step}")
                if i == 0:
                    i += 1
                    # Ignoring the base step
                    continue

                print(step.inner_values, len(step.inner_values))
                if len(step.inner_values) > 0:
                    prop_name = step.inner_values[0]
                    prop_name = prop_name if prop_name not in ["T.id", "T.label"] else prop_name.split("T.")[1]
                    prop_val = step.inner_values[1:]
                    print(f"Vertex step prop name: {prop_name} and value {prop_val}")

                    # print(prop_name, prop_val)
                    if prop_val[0] == "within":
                        # print("Got within predicate inside dst_step, joining it")
                        prop_val = [",".join(prop_val)]

                    if len(prop_val) == 1:
                        self.ROOT_FILTERS["dst_filter"][prop_name] = prop_val[0]
                    else:
                        self.ROOT_FILTERS["dst_filter"][prop_name] = prop_val
                    i += 1

                print(f"Root filters dst step {i} ", self.ROOT_FILTERS)

        print(f"2: Root step is \n{root_step}")
        print(f"3: Root filters are: \n{self.ROOT_FILTERS}")
        return self

    @staticmethod
    def _is_edge_traversal_(step):
        return step.inner_values[0] in ["outE", "bothE", "inE"]

    @staticmethod
    def _is_vertex_traversal_(step):
        return step.inner_values[0] in ["outV", "otherV", "inV"]

    @staticmethod
    def _is_edge_vertex_traversal_(step):
        return step.inner_values[0] in ["out", "both", "in"]

    @staticmethod
    def _is_union_element_(step):
        if step.inner_values[0] == "union":
            return True
        return False

    @staticmethod
    def _is_coalesce_element_(step):
        if step.inner_values[0] == "coalesce":
            return True
        return False

    def _identify_union_coalesce_traversals_(self):
        for step in self.QUERY.steps:
            if self._is_union_element_(step.middle_layer[0]):
                self.UNION_TRAVERSALS.append(step)
            elif self._is_coalesce_element_(step.middle_layer[0]):
                self.COALESCE_TRAVERSALS.append(step)
            else:
                if len(self.UNION_TRAVERSALS) > 0 or len(self.COALESCE_TRAVERSALS) > 0:
                    break
        return self

    def _identify_root_traversal_(self):
        print("Identifying the root traversal ")

        root_step_with_traversal = []
        for step in self.QUERY.steps:
            centric_type = self._calculate_centric_type_query_()
            # print(step.middle_layer)
            # print("==========")
            if len(root_step_with_traversal) == 2:
                if self._is_edge_vertex_traversal_(root_step_with_traversal[-1].middle_layer[0]):
                    # print(f"{root_step_with_traversal[-1].middle_layer[0]} is edge_vertex_traversal so breaking")
                    break

            if len(root_step_with_traversal) == 3:
                if self._is_vertex_traversal_(root_step_with_traversal[-1].middle_layer[0]):
                    # print(f"{root_step_with_traversal[-1].middle_layer[0]} is vertex_traversal so breaking")
                    break

            if self._is_union_element_(step.middle_layer[0]):
                # print(f"Element \n{step.middle_layer[0]}\n is union step so going to break")
                # print("I'm first break here, so this is encountered only when union is attached to root traversal")
                self._identify_union_coalesce_traversals_()
                break

            if self._is_coalesce_element_(step.middle_layer[0]):
                # print(f"Element \n{step.middle_layer[0]}\n is coalesce step so going to break")
                # print("I'm first break here, so this is encountered only when coalesce is attached to root traversal")
                self._identify_union_coalesce_traversals_()
                break

            if self._is_edge_traversal_(step.middle_layer[0]):
                # print(f"{step.middle_layer[0]} is edge traversal so adding")
                root_step_with_traversal.append(step)
                continue
            if self._is_vertex_traversal_(step.middle_layer[0]):
                # print(f"{step.middle_layer[0]} is vertex traversal so adding")
                root_step_with_traversal.append(step)
                continue
            if "add" not in centric_type.lower() and centric_type.lower() != "NA":
                # print(f"{centric_type} is not element add so adding")
                root_step_with_traversal.append(step)
                continue

        self.ROOT_TRAVERSAL = root_step_with_traversal
        return self
