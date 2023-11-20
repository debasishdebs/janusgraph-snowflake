
class TraversalIdStep(object):
    AS_STEP = dict()
    PROJECT_STEP = dict()
    ERROR = "NA"
    SELECTION_QUERY = ""
    COLUMN_PROJECTION = False
    COLUMN_PROJECTION_BY = ""
    DEDUPLICATE = False
    LIMIT = -1
    COUNT = False

    def __init__(self, bytecode):
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
        return "last_id"

    def execute(self):
        # self._get_as_steps_()
        # print(f"As Steps {self.AS_STEP}")

        # self._get_projected_elements_()
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
        print("Last Id steps")
        print(self.PROJECT_STEP)

        deduplicate_prefix = " distinct " if self.DEDUPLICATE else ""
        limit_suffix = f" limit {self.LIMIT} " if self.LIMIT != -1 else ""

        src_id_case_q = "(case when (t.direction = 'out') then t.node_id else t.map_id end)"
        dst_id_case_q = "(case when (t.direction = 'out') then t.map_id else t.node_id end)"

        q = f"select {deduplicate_prefix} {src_id_case_q} as src_id, {dst_id_case_q} as dst_id, t.direction, t.lvl, t.value_id " \
            f"from temp t " \
            f"where src_id != dst_id " \
            f"and t.lvl = (select max(lvl) from temp)"
        q += limit_suffix
        sql = q

        if self.COUNT:
            query = f" select count(*) as count from ({sql})"
            sql = query

        self.SELECTION_QUERY = sql
        return self
