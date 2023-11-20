import datetime as dt
from gen.graphdb_pb2 import Time, ConditionalURLs, ConditionalHosts, ConditionalUsers, ConditionalIPs, CaseInformation
from typing import Union


# RESOURCES_PREFIX = "../../"
RESOURCES_PREFIX = "/app/src/main/"
APPLICATION_PROPERTIES = f"{RESOURCES_PREFIX}/resources/application.properties"


class Utilities:
    @staticmethod
    def load_properties(filepath, sep='=', comment_char='#'):
        """
        Read the file passed as parameter as a properties file.
        """
        props = {}
        with open(filepath, "rt") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith(comment_char):
                    key_value = l.split(sep)
                    key = key_value[0].strip()
                    value = sep.join(key_value[1:]).strip().strip('"')
                    props[key] = value
        return props

    @staticmethod
    def convert_proto_time_to_python_datetime(time) -> Union[dt.datetime, None]:
        if time is None:
            return time
        elif f":{time}:" == "::":
            return None
        elif time == "":
            return None
        date = dt.datetime(year=time.year, month=time.month, day=time.day, hour=time.hour, minute=time.minutes, second=time.seconds)
        return date

    @staticmethod
    def convert_python_time_to_proto_time(time: dt.datetime):
        t = Time()
        t.year = time.year
        t.month = time.month
        t.day = time.day
        t.hour = time.hour
        t.minutes = time.minute
        t.seconds = time.second
        return t

    @staticmethod
    def convert_query_dict_to_case_info_proto(case_query:dict):
        ip_list = []
        user_list = []
        url_list = []
        host_list = []

        for case in case_query:
            property_key = case["propertyKey"]
            value = case["propertyValue"]
            if property_key == "userName":
                elem = ConditionalUsers(USER=value)
                user_list.append(elem)
            elif property_key == "hostname":
                elem = ConditionalHosts(HOST=value)
                host_list.append(elem)
            elif property_key == "ip":
                elem = ConditionalIPs(IP=value)
                ip_list.append(elem)
            else:
                elem = ConditionalURLs(URL=value)
                url_list.append(elem)

        obj = CaseInformation(IPs=ip_list, users=user_list, hosts=host_list, urls=url_list)

        return obj

    @staticmethod
    def convert_case_information_proto_to_case_query_dict(case_information):
        ips = case_information.IPs
        users = case_information.users
        hosts = case_information.hosts
        urls = case_information.urls

        case_query_dict = dict()
        case_query_dict["IP"] = {"entityQueries": []}
        case_query_dict["user"] = {"entityQueries": []}
        case_query_dict["host"] = {"entityQueries": []}
        case_query_dict["url"] = {"entityQueries": []}

        for ip in ips:
            IP = ip.IP
            start_time = Utilities.convert_proto_time_to_python_datetime(ip.startTime)
            end_time = Utilities.convert_proto_time_to_python_datetime(ip.endTime)
            ds = ip.dataSource
            ip_dict = {"value": IP, "startTime": start_time, "endTime": end_time, "dataSource": ds}
            case_query_dict["IP"]["entityQueries"].append(ip_dict)

        for user in users:
            USER = user.USER
            start_time = Utilities.convert_proto_time_to_python_datetime(user.startTime)
            end_time = Utilities.convert_proto_time_to_python_datetime(user.endTime)
            ds = user.dataSource
            user_dict = {"value": USER, "startTime": start_time, "endTime": end_time, "dataSource": ds}
            case_query_dict["user"]["entityQueries"].append(user_dict)

        for host in hosts:
            HOST = Utilities.convert_proto_time_to_python_datetime(host.HOST)
            start_time = Utilities.convert_proto_time_to_python_datetime(host.startTime)
            end_time = Utilities.convert_proto_time_to_python_datetime(host.endTime)
            ds = host.dataSource
            host_dict = {"value": HOST, "startTime": start_time, "endTime": end_time, "dataSource": ds}
            case_query_dict["host"]["entityQueries"].append(host_dict)

        for url in urls:
            URL = url.URL
            start_time = Utilities.convert_proto_time_to_python_datetime(url.startTime)
            end_time = Utilities.convert_proto_time_to_python_datetime(url.endTime)
            ds = url.dataSource
            url_dict = {"value": URL, "startTime": start_time, "endTime": end_time, "dataSource": ds}
            case_query_dict["url"]["entityQueries"].append(url_dict)

        return case_query_dict

    @staticmethod
    def generate_join_query_for_condition(direction: str, nodes_tbl: str, node_filter: dict, dst_filter: dict):
        print(f"Gen join query condition for dir: {direction}, root: {node_filter}, {len(node_filter)}, "
              f"dst: {dst_filter}, {len(dst_filter)}")

        if direction == "OUT":
            if len(node_filter) >= 1 and len(dst_filter) >= 1:
                join_query = f" inner join {nodes_tbl} nms on nms.node_id = ne.node_id "
                join_query += f" inner join {nodes_tbl} nmd on nmd.node_id = ne.map_id "
            elif len(node_filter) >= 1:
                join_query = f" inner join {nodes_tbl} nms on nms.node_id = ne.node_id "
            else:
                join_query = f" inner join {nodes_tbl} nmd on nmd.node_id = ne.node_id "

            join_condition = {direction: join_query}

        elif direction == "IN":
            if len(node_filter) >= 1 and len(dst_filter) >= 1:
                join_query = f" inner join {nodes_tbl} nms on nms.node_id = ne.map_id "
                join_query += f" inner join {nodes_tbl} nmd on nmd.node_id = ne.node_id "
            elif len(node_filter) >= 1:
                join_query = f" inner join {nodes_tbl} nms on nms.node_id = ne.map_id "
            else:
                join_query = f" inner join {nodes_tbl} nmd on nmd.node_id = ne.node_id "

            join_condition = {direction: join_query}

        else:
            if direction != "VCI":
                print("Generating for out inside both")
                out_join_condition = Utilities.generate_join_query_for_condition("OUT", nodes_tbl, node_filter, dst_filter)
                print(f"Out as {out_join_condition}")
                in_join_condition = Utilities.generate_join_query_for_condition("IN", nodes_tbl, node_filter, dst_filter)
                print(f"In as {in_join_condition}")

                join_condition = {
                    "OUT": out_join_condition["OUT"], "IN": in_join_condition["IN"]
                }
            else:
                print("Generating for out inside VCI")
                out_join_condition = Utilities.generate_join_query_for_condition("OUT", nodes_tbl, node_filter, dst_filter)
                print(f"Out as {out_join_condition}")

                join_condition = {
                    "OUT": out_join_condition["OUT"], "IN": ""
                }

        print(f"Returning join condition {join_condition}")

        return join_condition

    @staticmethod
    def generate_filter_query_for_condition(node_filter: dict, edge_filter: dict, dst_filter: dict, direction: str):
        print(f"Generating the filter query for node: {node_filter}, edge: {edge_filter}, dst: {dst_filter}, dir: {direction}")

        if direction == "OUT":
            sql = ""
            for k, v in node_filter.items():
                prefix = " where " if sql == "" else " and "
                query = Utilities.generate_node_filter_query_for_src(k, v, prefix, direction)
                sql += query

            for k, v in dst_filter.items():
                prefix = " where " if sql == "" else " and "
                query = Utilities.generate_node_filter_query_for_dst(k, v, prefix, direction)
                sql += query

            for k, v in edge_filter.items():
                prefix = " where " if sql == "" else " and "
                query = Utilities.generate_edge_filter_query(k, v, prefix)
                sql += query

            filter_query = {direction: sql}

        elif direction == "IN":
            sql = ""
            for k, v in node_filter.items():
                prefix = " where " if sql == "" else " and "
                query = Utilities.generate_node_filter_query_for_src(k, v, prefix, direction)
                sql += query

            for k, v in dst_filter.items():
                prefix = " where " if sql == "" else " and "
                query = Utilities.generate_node_filter_query_for_dst(k, v, prefix, direction)
                sql += query

            for k, v in edge_filter.items():
                prefix = " where " if sql == "" else " and "
                query = Utilities.generate_edge_filter_query(k, v, prefix)
                sql += query

            filter_query = {direction: sql}

        else:
            if direction is not "VCI":
                print("Generating fiter query for both direction components")
                out_query = Utilities.generate_filter_query_for_condition(node_filter, edge_filter, dst_filter, "OUT")
                print(f"Generated for out as {out_query}")
                in_query = Utilities.generate_filter_query_for_condition(node_filter, edge_filter, dst_filter, "IN")
                print(f"Generated for in as {in_query}")
            else:
                out_query = Utilities.generate_filter_query_for_condition(node_filter, edge_filter, dst_filter, "OUT")
                in_query = {"IN": ""}

            # are_conditions_already_added = True if (out_query["OUT"] != "" and in_query["IN"] != "") else False
            #
            # print("In both query filter gen")
            # print("Out query ", out_query)
            # print("In query ", in_query)
            # print("Are conditions added ", are_conditions_already_added)
            #
            # edge_query = ""
            # for k, v in edge_filter.items():
            #     prefix = " and " if are_conditions_already_added else " where "
            #     query = Utilities.generate_edge_filter_query(k, v, prefix)
            #     edge_query += query

            filter_query = {
                "OUT": out_query["OUT"],
                "IN": in_query["IN"]
            }

        return filter_query

    @staticmethod
    def generate_node_filter_query_for_src(prop, val, prefix, direction):
        print(f"Generating node filter for src with prop: {prop}, val: {val}, prefix: {prefix} and dir: {direction}")

        sf_config = Utilities.load_properties(Utilities.load_properties(APPLICATION_PROPERTIES)["snowflake.credentials.file"])
        case_tbl = sf_config["case_tbl"]

        CASE_CONDITION = False
        if prop == "id":
            property_ref = "ne.node_id" if direction == "OUT" else "ne.map_id"
        elif prop == "caseId":
            property_ref = "nms.node_id"
            CASE_CONDITION = True
        elif prop == "label":
            property_ref = "nms.label"
        else:
            property_ref = f"get(nms.properties:{prop}, 0)"
            property_ref = f"nms.properties:{prop}"

        vals = val.split(",")
        if len(vals) == 1:
            predicate = "eq"
            value = vals[0]
        else:
            predicate = vals[0]
            value = vals[1:]
            if len(value) == 1 and predicate not in ("within", "between"):
                value = value[0]

        if isinstance(value, list):
            print("Got list value in src filter gen as ", value)
            print("First condition is ", value[0])
            time = value[0] == "time"
            if time:
                cast = "::datetime"
                value = value[1:]
            else:
                cast = ""

            if predicate == "within":
                vals = [f"'{x}'" for x in value]
                query = f" {prefix} {property_ref}{cast} in ({','.join(vals)})"
            elif predicate == "between":
                query = f" {prefix} {property_ref}{cast} between '{value[0]}' and '{value[1]}'"
            elif predicate == "gte":
                query = f" {prefix} {property_ref}{cast} >= '{value[0]}'"
            elif predicate == "lte":
                query = f" {prefix} {property_ref}{cast} <= '{value[0]}'"
            elif predicate == "gt":
                query = f" {prefix} {property_ref}{cast} > '{value[0]}'"
            elif predicate == "lt":
                query = f" {prefix} {property_ref}{cast} < '{value[0]}'"
            elif predicate == "eq":
                if CASE_CONDITION:
                    CASE_ALL_HANDLER = "case when lower(q.value:\"propertyValue\") = 'all' \
                                                then lower(n.value:value) != lower(q.value:\"propertyValue\") \
                                                else lower(n.value:value) = lower(q.value:\"propertyValue\") \
                                            end"

                    case_criteria = "select n.value:node_id::numeric as node_id \n" \
                                    f"from {case_tbl} c, lateral flatten(input => nodes) n, lateral flatten(input => query) q \n" \
                        f"where c.case_id = '{value[0]}' \n" \
                        f"and n.value:property = q.value:\"propertyKey\" \n\
                        and {CASE_ALL_HANDLER}"
                    query = f" {prefix} {property_ref} in ({case_criteria}) "
                else:
                    query = f" {prefix} {property_ref}{cast} = '{value[0]}'"
            elif predicate == "neq":
                query = f" {prefix} {property_ref}{cast} != '{value[0]}'"
            else:
                print("Predicates supported are between/within/gte/lte/gt/lt/eq but got in node_filter_out_utils " + predicate)
                raise Exception()
        else:
            if CASE_CONDITION:
                CASE_ALL_HANDLER = "case when lower(q.value:\"propertyValue\") = 'all' \
                                                then lower(n.value:value) != lower(q.value:\"propertyValue\") \
                                                else lower(n.value:value) = lower(q.value:\"propertyValue\") \
                                            end"

                case_criteria = "select n.value:node_id::numeric as node_id \n" \
                                f"from {case_tbl} c, lateral flatten(input => nodes) n, lateral flatten(input => query) q \n" \
                    f"where c.case_id = '{value}' \n" \
                    f"and n.value:property = q.value:\"propertyKey\" \n\
                    and {CASE_ALL_HANDLER}"
                query = f" {prefix} {property_ref} in ({case_criteria}) "
            else:
                query = f" {prefix} {property_ref} = '{value}'"

        return query

    @staticmethod
    def generate_node_filter_query_for_dst(prop, val, prefix, direction):
        print(f"Generating node filter for dst with prop: {prop}, val: {val}, prefix: {prefix} and dir: {direction}")

        if prop == "id":
            property_ref = "ne.map_id" if direction == "OUT" else "ne.node_id"
        elif prop == "label":
            property_ref = "nmd.label"
        else:
            property_ref = f"get(nmd.properties:{prop}, 0)"
            property_ref = f"nmd.properties:{prop}"

        vals = val.split(",")
        if len(vals) == 1:
            predicate = "eq"
            value = vals[0]
        else:
            predicate = vals[0]
            value = vals[1:]
            if len(value) == 1 and predicate not in ("within", "between"):
                value = value[0]

        if isinstance(value, list):
            # predicate = val[0]
            # values = val[1:]
            if predicate == "within":
                vals = [f"'{x}'" for x in value]
                query = f" {prefix} {property_ref} in ({','.join(vals)})"
            elif predicate == "between":
                query = f" {prefix} {property_ref} between '{value[0]}' and '{value[1]}'"
            elif predicate == "gte":
                query = f" {prefix} {property_ref} >= '{value[0]}'"
            elif predicate == "lte":
                query = f" {prefix} {property_ref} <= '{value[0]}'"
            elif predicate == "gt":
                query = f" {prefix} {property_ref} > '{value[0]}'"
            elif predicate == "lt":
                query = f" {prefix} {property_ref} < '{value[0]}'"
            elif predicate == "eq":
                query = f" {prefix} {property_ref} = '{value[0]}'"
            elif predicate == "neq":
                query = f" {prefix} {property_ref} != '{value[0]}'"
            else:
                print("Predicates supported are between/within/gte/lte/gt/lt/eq but got node_filter_in_utils " + predicate)
                raise Exception()
        else:
            query = f" {prefix} {property_ref} = '{value}'"

        return query

    @staticmethod
    def generate_edge_filter_query(prop, val, prefix):
        if prop == "id":
            property_ref = "ne.value_id"
        elif prop == "label":
            property_ref = "ne.value_label"
        else:
            property_ref = f"get(ne.value_properties:{prop}, 0)"
            property_ref = f"ne.value_properties:{prop}"

        print(f"Generating edge filter join condition on prop: {prop}, val: {val} and prefix: {prefix}")

        vals = val.split(",")
        if len(vals) == 1:
            predicate = "eq"
            value = vals[0]
        else:
            predicate = vals[0]
            value = vals[1:]
            if len(value) == 1 and predicate not in ("within", "between"):
                value = value[0]

        if isinstance(value, list):
            print("Got list value in edge filter gen as ", value)
            print("First condition is ", value[0])
            time = value[0] == "time"
            if time:
                cast = "::datetime"
                value = value[1:]
            else:
                cast = ""

            if predicate == "within":
                vals = [f"'{x}'" for x in value]
                query = f" {prefix} {property_ref}{cast} in ({','.join(vals)})"
            elif predicate == "between":
                query = f" {prefix} {property_ref}{cast} between '{value[0]}' and '{value[1]}'"
            elif predicate == "gte":
                query = f" {prefix} {property_ref}{cast} >= '{value[0]}'"
            elif predicate == "lte":
                query = f" {prefix} {property_ref}{cast} <= '{value[0]}'"
            elif predicate == "gt":
                query = f" {prefix} {property_ref}{cast} > '{value[0]}'"
            elif predicate == "lt":
                query = f" {prefix} {property_ref}{cast} < '{value[0]}'"
            elif predicate == "eq":
                query = f" {prefix} {property_ref}{cast} = '{value[0]}'"
            elif predicate == "neq":
                query = f" {prefix} {property_ref}{cast} != '{value[0]}'"
            else:
                print("Predicates supported are between/within/gte/lte/gt/lt/eq but got in utils edgE_filter_utils " + predicate)
                raise Exception()
        else:
            query = f" {prefix} {property_ref} = '{val}'"

        return query
