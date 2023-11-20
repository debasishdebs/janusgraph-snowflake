class PropertiesStep:
    NUM_TRAVERSALS = 0
    ERROR = "NA"
    SELECTION_QUERY = "NA"
    DEDUPLICATE = False

    def __init__(self, bytecode):
        from utils.common_resources import Commons

        self.QUERY = bytecode
        self._is_deduplicate_query_()

        self.master = Commons.MASTER_TABLE
        self.edges = Commons.EDGES_TABLE

    def __str__(self):
        return "properties"

    def execute(self):
        self._get_number_of_traversals_()
        self._build_query_()
        return self

    def _is_deduplicate_query_(self):
        # Need to make this logic more better. Usually deduplicate will be found among last 3 steps. if before not supported
        end_steps = self.QUERY.steps[-3:]
        for step in end_steps:
            if step.middle_layer[0].inner_values[0] == "dedup":
                self.DEDUPLICATE = True
                return self
        return self

    def get_query(self):
        query = "with temp as \n(\n\t{traversal}\n)\n" + self.SELECTION_QUERY
        return query

    def _build_query_(self):
        deduplicate_prefix = " distinct " if self.DEDUPLICATE else ""
        # print(f"Number of trversals {self.NUM_TRAVERSALS}")

        src_id_case_q = "(case when (t.direction = 'out') then t.node_id else t.map_id end)"
        dst_id_case_q = "(case when (t.direction = 'out') then t.map_id else t.node_id end)"

        q = f"select {deduplicate_prefix} {src_id_case_q} as src_id, ns.label as src_label, ns.properties as src_properties, " \
            f"{dst_id_case_q} as dst_id, no.label as dst_label, no.properties as dst_properties, " \
            f"t.direction, t.lvl, t.value_id, ne.value_label, ne.value_properties " \
            f"from temp t " \
            f"inner join {self.master} ns on ns.node_id = {src_id_case_q} " \
            f"inner join {self.master} no on no.node_id = {dst_id_case_q} " \
            f"inner join {self.edges} ne on ne.value_id = t.value_id " \
            f"where src_id != dst_id "
        #
        # if self.NUM_TRAVERSALS == 0:
        #     query = " select " + deduplicate_prefix + "nm.node_id, nm.properties, nm.label, ne.value_id, ne.value_label, ne.value_properties from ({traversal}) t "\
        #     f"inner join {self.master} nm on nm.node_id = t.node_id inner join {self.edges} ne on ne.node_id = t.node_id "
        # else:
        #     query = " select " + deduplicate_prefix + "nm.node_id, nm.properties, nm.label, ne.value_id, ne.value_label, ne.value_properties from ({traversal}) t "\
        #     f"inner join {self.master} nm on nm.node_id = t.map_id inner join {self.edges} ne on ne.node_id = t.map_id where t.lvl = {self.NUM_TRAVERSALS} "

        self.SELECTION_QUERY = q
        return self

    def _get_number_of_traversals_(self):
        idx = 0
        while idx < len(self.QUERY.steps):
            step = self.QUERY.steps[idx]

            if self._is_root_element_(step.middle_layer):
                idx += 1
                continue
            if self._is_edge_edge_vertex_traversal_element_(step.middle_layer):
                self.NUM_TRAVERSALS += 1
                if self._is_edge_traversal_element_(step.middle_layer):
                    idx += 2
                    continue
                idx += 1
                continue
            repeat, repeat_times = self._is_repeat_traversal_element_(step.middle_layer)
            if repeat:
                self.NUM_TRAVERSALS += repeat_times
                idx += 1
                continue

            idx += 1
            continue
        return self

    def _is_root_element_(self, step):
        if step[0].inner_values[0] == "E" or step[0].inner_values[0] == "V":
            # print(f"Root element is {step}")
            return True
        return False

    @staticmethod
    def _is_edge_edge_vertex_traversal_element_(tr_step):
        if tr_step[0].inner_values[0] in ["inE", "outE", "bothE", "in", "out", "both"]:
            return True
        return False

    @staticmethod
    def _is_edge_traversal_element_(tr_step):
        if tr_step[0].inner_values[0] in ["inE", "outE", "bothE"]:
            return True
        return False

    def _is_repeat_traversal_element_(self, tr_step):
        if tr_step[0].inner_values[0] in ["repeat"]:
            return True, self._get_repeat_times_(tr_step)
        return False, 0

    def _get_repeat_times_(self, repeat_step):
        repeat_times_step = repeat_step[-1]
        times = repeat_times_step.inner_values[1]
        return int(times)
