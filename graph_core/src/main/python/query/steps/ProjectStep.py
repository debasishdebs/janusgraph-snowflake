from gen.graphdb_pb2 import MiddleMostByteCode, InnerMostByteCode


class ProjectStep(object):
    AS_STEP = dict()
    PROJECT_STEP = dict()
    ERROR = "NA"
    SELECTION_QUERY = ""
    COLUMN_PROJECTION = False
    COLUMN_PROJECTION_BY = ""
    DEDUPLICATE = False
    LIMIT = -1
    COUNT = False

    def __init__(self, bytecode, current=None):
        self.QUERY = bytecode
        self.STEPS = bytecode.steps
        self._is_deduplicate_query_()
        self._is_limiting_query_()
        self._is_count_query_()
        print(f"Duplicate status: {self.DEDUPLICATE} and Limit status: {self.LIMIT} and count {self.COUNT}")

        from utils.common_resources import Commons
        self.master = Commons.MASTER_TABLE
        self.edges = Commons.EDGES_TABLE

    def __str__(self):
        return "project"

    def execute(self):
        self._get_as_steps_()
        print(f"As Steps {self.AS_STEP}")

        self._get_projected_elements_()
        self._build_query_()
        return self

    def get_query(self):
        query = "with temp as \n(\n\t{traversal}\n)\n" + self.SELECTION_QUERY
        return query

    def get_select_statement(self):
        return self.SELECTION_QUERY

    def _is_deduplicate_query_(self):
        # Need to make this logic more better. Usually deduplicate will be found among last 3 steps. if before not supported
        end_steps = self.STEPS[-3:]
        for step in end_steps:
            if step.middle_layer[0].inner_values[0] == "dedup":
                self.DEDUPLICATE = True
                return self
        return self

    def _is_limiting_query_(self):
        # Need to make better logic. Currently supports limiting only in last 2 value of final result
        # (dedup -> limit -> count / dedup -> count / dedup -> limit / limit -> count / count / dedup / limit )
        # Need to implement limit on sub query / sub traversals later on so that lesser records are processed

        end_steps = self.STEPS[-2:]
        for step in end_steps:
            if step.middle_layer[0].inner_values[0] == "limit":
                self.LIMIT = int(step.middle_layer[0].inner_values[1])
                return self
        return self

    def _is_count_query_(self):
        # Need to make better logic. Currently supports limiting only in last 2 value of final result
        # (dedup -> limit -> count / dedup -> count / dedup -> limit / limit -> count / count / dedup / limit )
        # Need to implement limit on sub query / sub traversals later on so that lesser records are processed

        end_step = self.STEPS[-1]
        if end_step.middle_layer[0].inner_values[0] == "count":
            self.COUNT = True
            return self
        return self

    def _build_query_(self):
        print("AS Steps")
        print(self.AS_STEP)
        print("Project steps")
        print(self.PROJECT_STEP)
        COLUMN_PROJECTION = False
        COLUMN = None

        sql = "select * from recursive "
        iter = 0
        for column, col_ref in self.PROJECT_STEP.items():
            print(f"For columns {column} and ref {col_ref}")

            if len([k for k in self.AS_STEP.keys() if "edge" in k]) > 0:
                self.ERROR = "Implemented storing of side effects and projecting only for Vertices not Edges"
                return self

            as_for_column = [k for k, v in self.AS_STEP.items() if v == column]

            if len(as_for_column) == 0:
                if col_ref["ref"][:2] != "C.":
                    self.ERROR = "Mismatch in number of as() store side effect key and by() projection. " \
                                 "Mismatch supported only when you pass Column.{} in project/by clause"
                    return self
                else:
                    COLUMN_PROJECTION = True
                    COLUMN = col_ref["ref"]
                    as_for_column = "*"
                    # if col_ref["ref"] == "C.all":
                    #     as_for_column = "*"
                    # else:
                    #     self.ERROR = "Currently supports Column.all() only got " + col_ref["ref"]
                    #     return self
            else:
                as_for_column = as_for_column[0]

            if as_for_column != "*":
                if iter == 0:
                    condition = " where lvl = " + as_for_column
                else:
                    condition = " or lvl = " + as_for_column
            else:
                condition = ""

            sql += condition
            iter += 1

        subquery = sql

        deduplicate_prefix = " distinct " if self.DEDUPLICATE else ""
        limit_suffix = f" limit {self.LIMIT} " if self.LIMIT != -1 else ""

        if self.COLUMN_PROJECTION:
            src_id_case_q = "(case when (t.direction = 'out') then t.node_id else t.map_id end)"
            dst_id_case_q = "(case when (t.direction = 'out') then t.map_id else t.node_id end)"
            if self.COLUMN_PROJECTION_BY == "C.all":
                q = \
                    f"select {deduplicate_prefix} temp.*, ns.label as src_label, ns.properties as src_properties, no.label as dst_label, no.properties as dst_properties, ne.value_id, ne.value_label, ne.value_properties \
                    from temp "\
                    f"inner join {self.master} ns on ns.node_id = temp.node_id "\
                    f"inner join {self.master} no on no.node_id = temp.map_id "\
                    f"inner join {self.edges} ne on ne.value_id = temp.value_id \
                        {limit_suffix} "

                # f"t.direction, t.lvl::int as lvl, t.value_id, ne.value_label, ne.value_properties " \
                # f"inner join {self.edges} ne on ne.value_id = t.value_id " \
                q = f"select {deduplicate_prefix} {src_id_case_q} as src_id, ns.label as src_label, ns.properties as src_properties, " \
                    f"{dst_id_case_q} as dst_id, no.label as dst_label, no.properties as dst_properties, " \
                    "t.value_label, t.lvl::int as lvl " \
                    f"from temp t " \
                    f"inner join {self.master} ns on ns.node_id = {src_id_case_q} " \
                    f"inner join {self.master} no on no.node_id = {dst_id_case_q} " \
                    f"where src_id != dst_id "

                q += limit_suffix

                # q = f"select *, t.* from edges, ({subquery}) t"
                sql = q

            elif self.COLUMN_PROJECTION_BY == "C.id":
                # q = "select r.lvl as lvl, edges.root_id, edges.edge_id, edges.oth_id, edges.edge_direction, edges.edge_label from recursive r \
                #     inner join edges on r.root_id = edges.root_id and r.oth_id = edges.oth_id"

                q = f"select {deduplicate_prefix} t.node_id, t.map_id, t.lvl::int as lvl, t.value_id "\
                    "from temp t " \
                    f"inner join {self.edges} ne on ne.value_id = t.value_id "

                q = f"select {deduplicate_prefix} {src_id_case_q} as src_id, {dst_id_case_q} as dst_id, t.direction, t.lvl::int as lvl, t.value_id " \
                    f"from temp t " \
                    f"where src_id != dst_id "

                q += limit_suffix
                sql = q
            #
            # elif self.COLUMN_PROJECTION_BY == "C.firstAll":
            #     q = f"select {deduplicate_prefix} temp.*, ns.label as src_label, ns.properties as src_properties, no.label as dst_label, no.properties as dst_properties, ne.value_id, ne.value_label, ne.value_properties " \
            #         "from temp " \
            #         f"inner join {self.master} ns on ns.node_id = temp.node_id " \
            #         f"inner join {self.master} no on no.node_id = temp.map_id " \
            #         f"inner join {self.edges} ne on ne.value_id = temp.value_id " \
            #         "where temp.lvl = 1"
            #     q += limit_suffix
            #     sql = q
            #
            # elif self.COLUMN_PROJECTION_BY == "C.firstId":
            #     q = f"select {deduplicate_prefix} t.node_id, t.map_id, t.lvl, t.value_id " \
            #         "from temp t " \
            #         f"inner join {self.edges} ne on ne.value_id = t.value_id " \
            #         "where t.lvl = 1"
            #     q += limit_suffix
            #     sql = q

            elif "C.selectNId" in self.COLUMN_PROJECTION_BY:
                lvl = self.COLUMN_PROJECTION_BY.split("C.selectNId_")[1]

                q = f"select {deduplicate_prefix} {src_id_case_q} as src_id, {dst_id_case_q} as dst_id, t.direction, t.lvl::int as lvl, t.value_id " \
                    f"from temp t " \
                    f"where src_id != dst_id " \
                    f"and lvl = {lvl}"
                q += limit_suffix
                sql = q

            elif "C.selectNAll" in self.COLUMN_PROJECTION_BY:
                lvl = self.COLUMN_PROJECTION_BY.split("C.selectNAll_")[1]

                q = f"select {deduplicate_prefix} {src_id_case_q} as src_id, ns.label as src_label, ns.properties as src_properties, " \
                    f"{dst_id_case_q} as dst_id, no.label as dst_label, no.properties as dst_properties, " \
                    f"t.direction, t.lvl, t.value_id, ne.value_label, ne.value_properties " \
                    f"from temp t " \
                    f"inner join {self.master} ns on ns.node_id = {src_id_case_q} " \
                    f"inner join {self.master} no on no.node_id = {dst_id_case_q} " \
                    f"inner join {self.edges} ne on ne.value_id = t.value_id " \
                    f"where src_id != dst_id " \
                    f"and t.lvl = {lvl}"
                q += limit_suffix
                sql = q

            elif "C.basic" == self.COLUMN_PROJECTION_BY:
                q = f"select {deduplicate_prefix} {src_id_case_q} as src_id, ns.label as src_label,  " \
                    f"{dst_id_case_q} as dst_id, no.label as dst_label, " \
                    f"t.direction, t.lvl, t.value_id, ne.value_label " \
                    f"from temp t " \
                    f"inner join {self.master} ns on ns.node_id = {src_id_case_q} " \
                    f"inner join {self.master} no on no.node_id = {dst_id_case_q} " \
                    f"inner join {self.edges} ne on ne.value_id = t.value_id " \
                    f"where src_id != dst_id "
                q += limit_suffix
                sql = q

            else:
                self.ERROR = "Currently supports Column.all()/id()/selectNId()/selectNAll()/basic() only got " + COLUMN
        else:
            sql = subquery

        if self.COUNT:
            query = f" select count(*) as count from ({sql})"
            sql = query

        self.SELECTION_QUERY = sql
        print(sql)
        return self

    def _get_projected_elements_(self):
        print("Getting projected elements")

        project_steps = self._get_project_query_()
        print(f"1: Project steps are \n{project_steps}")

        project_key_step = project_steps[0].middle_layer[0]
        project_value_steps = project_steps[0].middle_layer[1:]
        print(f"2Project key step: \n{project_key_step} and value \n{project_value_steps}")

        print(f"Project key: \n{project_key_step} and value \n{project_value_steps}")
        print(type(project_key_step), type(project_value_steps))

        assert type(project_key_step) == InnerMostByteCode
        assert type(project_value_steps) == list

        if len(project_value_steps) > 0:
            assert type(project_value_steps[0]) == InnerMostByteCode
        else:
            column_project_type = False
            for val in project_key_step.inner_values:
                if val in ["C.all", "C.id", "C.firstAll", "C.last", "C.firstId"]:
                    column_project_type = True
                    self.COLUMN_PROJECTION = True
                    self.COLUMN_PROJECTION_BY = val

            if not column_project_type:
                self.ERROR = "Project valid key passed but no projection using by_()"
            assert column_project_type == True

        project_keys = self._parse_project_key_(project_key_step)
        print(f"3: Project keys are: {project_keys}")

        self._parse_project_values_(project_keys, project_value_steps)
        return self

    def _parse_project_values_(self, keys, project_values):
        try:
            if len(project_values) > 0:
                assert len(keys) == len(project_values)
        except AssertionError:
            self.ERROR = "Number of project keys is different than number of project values"
            return self

        for i in range(len(project_values)):
            project_value = project_values[i]

            print(f"For value \n{project_value} of len {len(project_values)}")
            print("xx")
            print(project_value)
            print("xx")
            print(len(project_value.inner_values))
            print("xx")
            print(project_value.inner_values[0])

            assert type(project_value) == InnerMostByteCode
            assert len(project_value.inner_values) == 4
            assert project_value.inner_values[0] == "by"

            project_value_passed = project_value.inner_values[1:]

            assert len(project_value_passed) == 3

            choose_step_type = project_value_passed[0]
            choose_step_key = project_value_passed[1]
            choose_step_agg = project_value_passed[2]

            if choose_step_type not in ["select", "constant", "coalesce"]:
                self.ERROR = "Currently supports only select/constant/coalesce step as column value for project step got " + choose_step_type
                return self

            if choose_step_type in ["constant", "coalesce"]:
                raise NotImplementedError("Not implemented constant/coalesce for project column values yet TODO")

            print(self.AS_STEP)
            print(choose_step_key)
            print(self.AS_STEP.values())
            print(type(choose_step_key))
            print(choose_step_key not in self.AS_STEP.values())
            print(choose_step_key[:2] != "C.")
            print("==xx==")
            if choose_step_type == "select":
                if choose_step_key not in self.AS_STEP.values() and choose_step_key[:2] != "C.":
                    print("I'm in error section")
                    self.ERROR = f"Passed key {choose_step_key} is not defined via AS_ in query. Defined: [{list(self.AS_STEP.values())}]"
                    return self

            print("Building project dict")
            self.PROJECT_STEP[keys[i]] = {
                "ref": choose_step_key,
                "agg": choose_step_agg
            }

        return self

    def _parse_project_key_(self, project_key):
        print("Parsing project keys")
        print(type(project_key))

        keys = []

        for i in range(len(project_key.inner_values)):
            key = project_key.inner_values[i]
            print(key, type(key))
            if i == 0:
                assert key == "project"
                continue
            # assert key.inner_values[0] == "column"
            if key not in keys:
                keys.append(key)
            else:
                self.ERROR = f"Got duplicate column in Project. Already present = [{keys}] and got {key.inner_values[1]}"
        print(keys)
        return keys

    def _get_project_query_(self):
        for i in range(len(self.STEPS)):
            step = self.STEPS[i].middle_layer

            if step[0].inner_values[0] == "project":
                break_idx = len(self.QUERY.steps)
                for j in range(len(self.STEPS[i:])):
                    # print(f"Curr idx: {i} loop idx {j} start step {step[0].inner_values[0]} iter step {self.STEPS[i+j].middle_layer[0].inner_values[0]} iter over {self.STEPS[i:]} and len {len([self.STEPS[i:]])}")
                    if self.STEPS[i+j].middle_layer[0].inner_values[0] in ["dedup", "order", "group", "limit"]:
                        break_idx = i+j
                        break

                return self.QUERY.steps[i:break_idx]
        raise AttributeError("ProjectStep is being called when there is no project query? Contact developers")

    def _get_as_steps_(self):
        print(f"B: Generating as steps")

        hop = 1
        prev_edge_step = self._is_root_step_edge_()
        print(prev_edge_step)

        for i in range(len(self.STEPS)):
            step = self.STEPS[i].middle_layer
            as_exist, as_key = self._does_step_contain_as_(step)
            print(as_exist, as_key)

            tr_type = self.identify_type_of_traversal(step)
            print(tr_type)

            if tr_type is not None:
                if as_exist:
                    if tr_type == "Edge":
                        as_step_key = f"{hop}-{hop+1}_edge"
                    else:
                        as_step_key = f"{hop}"

                    self.AS_STEP[as_step_key] = as_key

                if tr_type == "Edge":
                    if prev_edge_step:
                        self.ERROR = "Invalid traversal. You can't add EdgeTraversal to another EdgeTraversal"
                    else:
                        hop += 1
                        prev_edge_step = True
                else:
                    if not prev_edge_step:
                        prev_edge_step = False
                        hop += 1
                    else:
                        prev_edge_step = False
                        continue

        print("xxxxx")

        return self

    def _is_root_step_edge_(self):
        vci_step = self.STEPS[0].middle_layer
        print(vci_step[0].inner_values)
        return True if vci_step[0].inner_values[0] == "E" else False

    @staticmethod
    def identify_type_of_traversal(step):
        trs = step[0].inner_values
        tr = trs[0]
        if tr == "outE" or tr == "inE" or tr == "bothE":
            return "Edge"
        if tr == "out" or tr == "in" or tr == "both":
            return "Vertex"
        if tr == "outV" or tr == "inV" or tr == "otherV":
            return "Vertex"
        return None

    def _does_step_contain_as_(self, step):
        print(f"Check for step containing as for step \n{step}")

        as_info = step[-1].inner_values  # We know if we add as_ condition, it will be last element in step
        print(as_info)

        if len(as_info) == 0:
            print("a")
            return False, ""

        if as_info[0] != "as":
            print("b")
            return False, ""

        if len(as_info) == 1:
            print("c")
            self.ERROR = "As specified, but not side effect key to save is mentioned"

        print("d")
        return True, as_info[1]
