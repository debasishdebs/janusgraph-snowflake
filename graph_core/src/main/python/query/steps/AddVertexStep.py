from gen.graphdb_pb2 import MiddleMostByteCode, InnerMostByteCode
import json


class AddVertexStep:
    def __init__(self, query):
        self.GRAPH_STEPS = query.steps
        self.SQL_QUERY = ""

        from utils.common_resources import Commons
        self.master = Commons.MASTER_TABLE
        self.edges = Commons.EDGES_TABLE

        self.ERROR = "NA"

    def execute(self):
        # print("Generating vertex query")
        self._generate_query_()
        return self

    def _generate_vertex_addition_metadata_(self):
        vertices = []
        for step in self.GRAPH_STEPS:
            assert type(step) == MiddleMostByteCode
            vertex_info = step.middle_layer

            vertex = {"properties": []}
            for info in vertex_info:
                assert type(info) == InnerMostByteCode
                if info.inner_values[0] == "AddVertex":
                    vertex["update"] = (info.inner_values[1].lower() == 'true')

                elif info.inner_values[0] == "properties":
                    properties = {}
                    property_infos = info.inner_values[1:]
                    property_key = property_infos[0]
                    property_values = property_infos[1:]
                    properties[property_key] = property_values
                    vertex["properties"].append(properties)

                else:
                    key = info.inner_values[0].split("T.")[1]
                    value = info.inner_values[1]
                    vertex[key] = value

            properties = vertex["properties"]
            properties_dict = {}
            for prop in properties:
                properties_dict[list(prop.keys())[0]] = list(prop.values())[0]
            vertex["properties"] = properties_dict
            vertices.append(vertex)

        return vertices

    def _generate_query_(self):
        vertices = self._generate_vertex_addition_metadata_()

        node_ids = []
        using_query = ""
        for vertex in vertices:
            if vertex['id'] != 'random':
                query = f" select {vertex['id']} as node_id, '{vertex['label']}' as label, parse_json('{json.dumps(vertex['properties'])}') as properties "
                node_ids.append(vertex['id'])
            else:
                query = f" select (select max(node_id)+1 from nodes_master_demo) as node_id, '{vertex['label']}' as label, parse_json('{json.dumps(vertex['properties'])}') as properties "

            if using_query == "":
                using_query += query
            else:
                using_query += "\n union all \n"
                using_query += query

        using_query = f" (\n{using_query}\n) "

        merge_queries = []
        for vertex in vertices:
            update = vertex["update"]
            if update:
                if "label" in vertex and "properties" in vertex:
                    if "ip" in vertex["properties"]:
                        merge = " (t.properties:ip = s.properties:ip and t.label = s.label) "
                    elif "userName" in vertex["properties"]:
                        merge = " (t.properties:userName = s.properties:userName and t.label = s.label) "
                    elif "hostname" in vertex["properties"]:
                        merge = " (t.properties:hostname = s.properties:hostname and t.label = s.label) "
                    elif "emailSubject" in vertex["properties"]:
                        merge = " (t.properties:emailSubject = s.properties:emailSubject and t.label = s.label) "
                    elif "fileName" in vertex["properties"]:
                        merge = " (t.properties:fileName = s.properties:fileName and t.label = s.label) "
                    elif "URL" in vertex["properties"]:
                        merge = " (t.properties:URL = s.properties:URL and t.label = s.label) "
                    else:
                        self.ERROR = "Invalid vertex passed to update, doesn't contain primary keys among ip/userName/hostname/emailSubject/fileName/URL"
                        return self

                    id_present = False

                elif "id" in vertex:
                    merge = " (t.node_id = s.node_id) "
                    id_present = True

                else:
                    self.ERROR = f"You need to pass either ID or LABEL + PROPERTIES combination to update the vertex {vertex}"
                    return self

                if merge not in merge_queries:
                    merge_queries.append(merge)
            else:
                self.ERROR = "Currently not implemented adding without update (fail if exists) in backend"
                return self

        merge_query = " or ".join(merge_queries)

        query = f" merge into {self.master} t using " \
            f" {using_query} as s \n" \
            f"\n on {merge_query} \
                \n when matched then update set t.properties = update_variant(t.properties, s.properties), t.label = s.label \
                \n WHEN NOT MATCHED THEN INSERT (node_id, label, properties) values (s.node_id, s.label, s.properties) "
            #
            #     if id_present:
            #         query = f" merge into {self.master} t using "\
            #         " {using} \n"\
            #         f"\n {merge} \
            #         \n when matched then update set t.properties = s.properties, t.label = s.label, t.node_id = s.node_id \
            #         \n WHEN NOT MATCHED THEN INSERT (node_id, label, properties) values (s.node_id, s.label, s.properties) "
            #     else:
            #         query = f" merge into {self.master} t using "\
            #         " {using} \n"\
            #         f"\n {merge} \
            #         \n when matched then update set t.properties = s.properties, t.label = s.label \
            #         \n WHEN NOT MATCHED THEN INSERT (node_id, label, properties) values (s.node_id, s.label, s.properties) "
            #
            # else:
            #     self.ERROR = "Currently not implemented adding without update (fail if exists) in backend"
            #     return self
            #
            # sql_query += f" {query} "

        self.SQL_QUERY = query
        self.READ_QUERY = f" select n.* from {self.master} as n where n.node_id in ({','.join(node_ids)}) "

        return self
