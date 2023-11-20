from gen.graphdb_pb2 import MiddleMostByteCode, InnerMostByteCode
import json


class AddEdgeStep:
    def __init__(self, query):
        self.GRAPH_STEPS = query.steps
        self.SQL_QUERY = ""

        from utils.common_resources import Commons
        self.master = Commons.MASTER_TABLE
        self.edges = Commons.EDGES_TABLE

        self.ERROR = "NA"

    def execute(self):
        # print("Generating edge query")
        self._generate_query_()
        return self

    def _generate_edge_addition_metadata_(self):
        edges = []
        for step in self.GRAPH_STEPS:
            # print(f"For step {step}")

            assert type(step) == MiddleMostByteCode
            edge_info = step.middle_layer
            # print(f"The middle layer is {edge_info}")

            edge = {"properties": []}
            for info in edge_info:
                assert type(info) == InnerMostByteCode

                # print(f"Extracting metadata for info: {info}")

                if info.inner_values[0] == "AddEdge":
                    edge["update"] = (info.inner_values[1].lower() == 'true')

                elif info.inner_values[0] == "properties":
                    properties = {}
                    property_infos = info.inner_values[1:]
                    property_key = property_infos[0]
                    property_values = property_infos[1:]
                    properties[property_key] = property_values
                    edge["properties"].append(properties)

                else:
                    if info.inner_values[0] in ["from", "to"]:
                        prop = info.inner_values[1]
                        if prop == "T.id":
                            edge[info.inner_values[0]] = info.inner_values[2]
                        else:
                            edge[info.inner_values[0]] = info.inner_values[1:]

                    else:
                        key = info.inner_values[0].split("T.")[1]
                        value = info.inner_values[1]
                        edge[key] = value

            properties = edge["properties"]
            properties_dict = {}
            for prop in properties:
                properties_dict[list(prop.keys())[0]] = list(prop.values())[0]
            edge["properties"] = properties_dict
            edges.append(edge)

        return edges

    def _generate_query_(self):
        edges = self._generate_edge_addition_metadata_()
        # print("Generated edge addition metadata")

        using_queries = []
        for edge in edges:
            # print(f"Using query being generated for {edge}")

            from_ref = edge["from"]
            to_ref = edge["to"]

            if isinstance(from_ref, list):
                prop = from_ref[0]
                val = from_ref[1]
                from_query = f" (select node_id from {self.master} where properties:\"{prop}\" = '{val}') "
                from_query = f" (select node_id from {self.master} where array_contains('{val}'::variant, properties:\"{prop}\") limit 1) "
                # from_query = f"'{val}'::varchar as source_value, '{prop}'::varchar as source_property, 'source'::varchar as source_label "
            else:
                from_query = edge["from"]

            if isinstance(to_ref, list):
                prop = to_ref[0]
                val = to_ref[1]
                to_query = f" (select node_id from {self.master} where array_contains('{val}'::variant, properties:\"{prop}\") limit 1) "
                # to_query = f"'{val}'::varchar as dst_value, '{prop}'::varchar as dst_property, 'source'::varchar as dst_label "
            else:
                to_query = edge["to"]

            # print(f"While generating using query, the from is | {from_query} | and to is | {to_query}")

            query = f" select {from_query} as node_id, s.label as label, '{edge['id']}' as value_id, 'out' as direction, " \
                f"'{edge['label']}' as value_label, parse_json('{json.dumps(edge['properties'])}') as value_properties, " \
                f"{to_query} as map_id, t.label as map_label " \
                f"from root s, root t where s.node_id = {from_query} and t.node_id = {to_query} "

            # query = f" select {from_query}, '{edge['id']}' as value_id, 'out' as direction, " \
            #     f"'{edge['label']}' as value_label, parse_json('{json.dumps(edge['properties'])}') as value_properties, " \
            #     f"{to_query} "

            using_queries.append(query)

        using_query = " \nunion all\n ".join(using_queries)
        using_query = f" (\n with root as ( \n select * from {self.master} \n ) \n {using_query} \n ) "
        using_query = f" (\n{using_query}\n) "

        merge_queries = []
        homogenous_update = []
        homogenous_insert = []
        insert_values = []
        edge_ids = []
        for edge in edges:
            update = edge["update"]
            # print(edge, update)
            if update:
                homogenous_update.append(True)

                if "id" in edge:
                    merge = " on t.value_id = s.value_id "
                    edge_ids.append(edge["id"])
                else:
                    self.ERROR = "Invalid edge passed to update, doesn't contain primary keys ID"
                    return self

                if merge not in merge_queries:
                    merge_queries.append(merge)
            else:
                homogenous_insert.append(True)

                from_ref = edge["from"]
                to_ref = edge["to"]

                if isinstance(from_ref, list):
                    prop = from_ref[0]
                    val = from_ref[1]
                    from_query = f" (select node_id from {self.master} where array_contains('{val}'::variant, properties:\"{prop}\") limit 1) "
                else:
                    from_query = edge["from"]

                if isinstance(to_ref, list):
                    prop = to_ref[0]
                    val = to_ref[1]
                    to_query = f" (select node_id from {self.master} where array_contains('{val}'::variant, properties:\"{prop}\") limit 1) "
                else:
                    to_query = edge["to"]

                # print(f"While generating insert query, the from is | {from_query} | and to is | {to_query}")

                query = f" select {from_query}, s.label, '{edge['id']}', 'out', '{edge['label']}', " \
                    f"parse_json('{json.dumps(edge['properties'])}'), {to_query}, t.label " \
                    f"from root s, root t where s.node_id={from_query} and t.node_id = {to_query} "

                insert_values.append(query)
                edge_ids.append(edge["id"])

                # self.ERROR = "Currently not implemented adding without update (fail if exists) in backend"

                # return self
        # print(homogenous_update)
        # print(homogenous_insert)
        if all(homogenous_update) and len(homogenous_update) > 0:
            # print("Im using homo update")
            merge_query = " or ".join(merge_queries)

            query = f" merge into {self.edges} t using " \
                f" {using_query} as s \n" \
                f"\n {merge_query} \
                    \n when matched then update set t.value_properties = update_variant(t.value_properties, s.value_properties), t.value_label = s.value_label \
                    \n WHEN NOT MATCHED THEN INSERT " \
                f"(node_id, label, value_id, direction, value_label, value_properties, map_id, map_label) " \
                f"values (s.node_id, s.label, s.value_id, s.direction, s.value_label, s.value_properties, s.map_id, s.map_label) "

            self.SQL_QUERY = query

            # self.READ_QUERY = f" select e.* from {self.edges} as e, {using_query} as s where n.node_id = s.node_id "

        else:
            if all(homogenous_insert) and len(homogenous_insert) > 0:
                # print("I'm in homo insert")
                query = f" insert into {self.edges} " \
                    f"with root as (select * from {self.master}) {' union all '.join(insert_values)}"

                self.SQL_QUERY = query

            else:
                self.ERROR = "Supports only homogenous updates or homogenous inserts"
                return self

        edge_ids_in = ""
        for eid in edge_ids:
            e = f"'{eid}'"
            if edge_ids_in == "":
                edge_ids_in += e
            else:
                edge_ids_in += ","
                edge_ids_in += e

        self.READ_QUERY = f" select e.* from {self.edges} as e where e.value_id in ({edge_ids_in})"

        return self
