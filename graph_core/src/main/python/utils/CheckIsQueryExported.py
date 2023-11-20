from gen.graphdb_pb2 import CaseSubmissionPayload, CaseExportStatus
import json
from utils.common_resources import Commons
from utils.utils import Utilities as U, APPLICATION_PROPERTIES
import pandas as pd
from google.protobuf.json_format import MessageToDict


class CheckQueryExported:
    def __init__(self, query):
        assert type(query) == CaseSubmissionPayload
        self.QUERY = query.query
        self.start_time = U.convert_proto_time_to_python_datetime(query.startTime)
        self.end_time = U.convert_proto_time_to_python_datetime(query.endTime)
        self.datasources = query.dataSource

        self.LABELS = [x for x in self.QUERY]

        connection = Commons.get_connection()
        sf_config = U.load_properties(U.load_properties(APPLICATION_PROPERTIES)["snowflake.credentials.file"])

        self.CASE_TBL = sf_config["case_tbl"]
        self.engine = connection.SNOWFLAKE_ENGINE

    def convert_query_to_python_dict(self):
        query_info = []
        for label in self.LABELS:
            entityQueries = self.QUERY[label].entityQuery
            for queryValue in entityQueries:
                if label == "IP":
                    query_dict = {"propertyKey": "ip", "propertyValue": queryValue}
                elif label == "user":
                    query_dict = {"propertyKey": "userName", "propertyValue": queryValue}
                else:
                    query_dict = {"propertyKey": "hostname", "propertyValue": queryValue}

                query_info.append(query_dict)
        return query_info

    def get_status(self):
        query_info = self.convert_query_to_python_dict()

        start_time = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time = self.end_time.strftime("%Y-%m-%d %H:%M:%S")

        data_source_condition = []
        for ds in self.datasources:
            data_source_condition.append(f"array_contains('{ds}'::variant, datasources)")
        data_source_condition = " and ".join(data_source_condition)

        array_condition = ""
        for query in query_info:
            prefix = " where " if array_condition == "" else " and "
            obj = {"propertyKey": query["propertyKey"], "propertyValue": MessageToDict(query["propertyValue"])["value"]}
            condition = f" {prefix} array_contains(parse_json('{json.dumps(obj)}')::variant, query) "
            array_condition += condition

        search_sql = f" select distinct case_id as case_id from {self.CASE_TBL} {array_condition} "
        search_sql += f" and ('{start_time}'::datetime >= query_start_time and '{end_time}'::datetime <= query_end_time) " \
                      f"and {data_source_condition}"
        print(f"Executing query {search_sql}")

        data = pd.read_sql_query(search_sql, con=self.engine)
        print(data)

        status = CaseExportStatus()
        if len(data) > 0:
            caseId = data["case_id"].values.tolist()[0]
            status.caseId = caseId
            status.status = True
            return status
        else:
            print("Running fallback method now")
            return self.fall_back_method_for_search()

    def fall_back_method_for_search(self):
        query_info = self.convert_query_to_python_dict()
        start_time = self.start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time = self.end_time.strftime("%Y-%m-%d %H:%M:%S")

        data_source_condition = []
        for ds in self.datasources:
            data_source_condition.append(f"array_contains('{ds}'::variant, datasources)")
        data_source_condition = " and ".join(data_source_condition)

        array_condition = ""
        tot_query_elements = len(query_info)
        for query in query_info:
            prefix = " " if array_condition == "" else " or "
            condtn = f" n.value:property = '{query['propertyKey']}' and n.value:value = '{MessageToDict(query['propertyValue'])['value']}' "
            condition = f" {prefix} {condtn} "
            array_condition += condition

        search_sql = f" select distinct n.value as value, case_id as case_id from {self.CASE_TBL}, lateral flatten(input=>nodes) n where ({array_condition}) "
        search_sql += f" and ('{start_time}'::datetime >= query_start_time and '{end_time}'::datetime <= query_end_time) " \
                      f"and {data_source_condition}"

        print(f"Executing fallback query as {search_sql}")
        data = pd.read_sql_query(search_sql, con=self.engine)
        print(data)
        status = CaseExportStatus()
        if len(data) > 0 and len(data) == tot_query_elements:
            caseId = data["case_id"].values.tolist()[0]
            status.caseId = caseId
            status.status = True
            return status
        else:
            if len(data) != tot_query_elements and len(data) > 0:
                print("Got the data, but not all elements queried are present so going to return as false")

            status.status = False
            status.caseId = "NA"
            return status
