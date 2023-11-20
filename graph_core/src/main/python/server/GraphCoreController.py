import json

from sqlalchemy import inspect

import gen.graphdb_pb2_grpc as graphdb_pb2_grpc
import gen.graphdb_pb2 as graphdb_pb2
from ByteCodeExecutor import ByteCodeExecutor
from utils.CaseStatusObject import CaseStatusObject
from google.protobuf.json_format import MessageToDict
from utils.CheckIsQueryExported import CheckQueryExported
from utils.utils import Utilities as U, APPLICATION_PROPERTIES
from utils.utils import RESOURCES_PREFIX
from utils.common_resources import Commons
from utils.SQLQueryExecutor import SQLQueryExecutor
import datetime as dt


class GraphCoreController(graphdb_pb2_grpc.ServicesToGraphCoreServicer):

    # calculator.square_root is exposed here
    # the request and response are of the data types
    # generated as calculator_pb2.Number
    def ExecuteByteCode(self, request, context):
        print(50*"=")
        # print(f"Got bytecode as \n{request} \nfor executing on server side")
        executor = ByteCodeExecutor(request)
        executor.execute()

        response = executor.get_response()

        return response

    def ExecuteStoredProcedure(self, request, context):
        procedure = request.procedure
        parameters = request.parameters
        order = request.order

        properties = Commons.get_properties()
        credentials = U.load_properties(properties["snowflake.credentials.file"])
        params = {}
        for k in parameters:
            v = parameters[k]
            if v == "DEFAULT":
                if "NODE" in procedure or "node" in procedure:
                    params[k] = credentials["nodes_tbl"]
                else:
                    params[k] = credentials["edges_tbl"]
            else:
                params[k] = v
        print(f"incoming param: {params} and procedure {procedure}")

        parameter_list = []
        for o in order:
            parameter_list.append(f"'{params[o]}'")
        query_params = ",".join(parameter_list)
        # if procedure == "SP_GRAPH_NODE_LOAD":
        #     query_params = f"'{params['CASE_ID_VAL']}', '{params['TARGET_NODE_TBL']}'"
        # elif procedure == "SP_GRAPH_EDGE_LOAD":
        #     query_params = f"'{params['CASE_ID_VAL']}', '{params['TARGET_EDGE_TBL']}'"
        # else:
        #     query_params = f"'{params['CASE_ID_VAL']}'"

        print(f"query params: {query_params}")
        query = f"call {procedure}({query_params});"
        print(f"query: {query}")

        executor = SQLQueryExecutor(query)
        res = executor.execute()
        print(f"Output of stored proc {procedure} is {res}")
        return graphdb_pb2.google_dot_protobuf_dot_empty__pb2.Empty()

    def UpdateAddedTimeToTrackingTableForRawData(self, request, context):
        connection = Commons.get_connection()
        engine = connection.SNOWFLAKE_ENGINE
        con = engine.connect()

        at = request.added_time
        added_timestamp = dt.datetime(year=at.year, month=at.month, day=at.day, hour=at.hour,
                                      minute=at.minutes, second=at.seconds).strftime("%Y-%m-%d %H:%M:%S")
        tables = request.tables
        data_sources = request.data_sources

        tables_query = []
        for tbl in tables:
            tables_query.append(f"'{tbl}'")
        tables_query = ",".join(tables_query)

        datasources = []
        for ds in data_sources:
            datasources.append(f"'{ds}'")
        ds_query = ",".join(datasources)

        sf_config = U.load_properties(U.load_properties(APPLICATION_PROPERTIES)["snowflake.credentials.file"])
        query_tracker_tbl = sf_config["query_tracker_tbl"]

        sql = f"insert into {query_tracker_tbl} (added_time, processed_time, table_name, datasource) \
                select to_timestamp_ntz('{added_timestamp}'), null, \
                array_construct({tables_query}), array_construct({ds_query});"

        res = con.execute(sql)
        query = self.object_as_dict(res)
        print(sql)
        print(f"Inserted added time and the response is {query}")
        con.close()
        return graphdb_pb2.StringMessage(msg=json.dumps(query))

    def UpdateProcessedTimeToTrackingTableForRawData(self, request, context):
        connection = Commons.get_connection()
        engine = connection.SNOWFLAKE_ENGINE
        con = engine.connect()

        pt = request.processed_time
        processed_timestamp = dt.datetime(year=pt.year, month=pt.month, day=pt.day, hour=pt.hour,
                                      minute=pt.minutes, second=pt.seconds).strftime("%Y-%m-%d %H:%M:%S")

        sf_config = U.load_properties(U.load_properties(APPLICATION_PROPERTIES)["snowflake.credentials.file"])
        query_tracker_tbl = sf_config["query_tracker_tbl"]

        sql = f"update {query_tracker_tbl} set processed_time = to_timestamp_ntz('{processed_timestamp}') " \
              f"where processed_time is null and added_time >= \
              (select max(case when processed_time is not null then processed_time else '1970-01-01 00:00:00'::datetime end) from stream_graph_import_tracker);"

        res = con.execute(sql)
        query = self.object_as_dict(res)
        print(f"Updated processed time and the response is {query} for records which are new and fresh")
        con.close()
        return graphdb_pb2.StringMessage(msg=json.dumps(query))

    def GetTheDataToQueryInNextIteration(self, request, context):
        connection = Commons.get_connection()
        engine = connection.SNOWFLAKE_ENGINE
        con = engine.connect()
        buffer_sec = 30
        sf_config = U.load_properties(U.load_properties(APPLICATION_PROPERTIES)["snowflake.credentials.file"])
        query_tracker_tbl = sf_config["query_tracker_tbl"]

        # sql = f"select \
        #     case when count(*) > 0 then \
        #     object_construct( \
        #         'status', case when count(*) > 0 then 'yes' else 'no' end, \
        #          'query', GENERATE_ALL_ETL_QUERY(\
        #              to_timestamp_ntz(datediff(sec, '00:00:{buffer_sec}'::datetime, to_timestamp_ntz(min(added_time))))::varchar, \
        #              dateadd(sec, {buffer_sec}, to_timestamp_ntz(max(added_time)))::varchar, \
        #              get_overall_data_sources(array_agg(distinct f.value))\
        #          ) \
        #     ) \
        #     else \
        #     object_construct('status', case when count(*) > 0 then 'yes' else 'no' end) \
        #     end as QUERY \
        #     from \
        #         {query_tracker_tbl}, lateral flatten(input => datasource) f \
        #     where added_time > (select max(case when processed_time is not null \
        #     then processed_time else '1970-01-01 00:00:00'::datetime end) from {query_tracker_tbl});"

        sql = f"select \
            case when count(*) > 0 then \
            object_construct( \
                'status', case when count(*) > 0 then 'yes' else 'no' end, \
                 'query', GENERATE_ALL_ETL_QUERY(\
                     to_timestamp_ntz(datediff(sec, '00:00:{buffer_sec}'::datetime, to_timestamp_ntz(min(added_time))))::varchar, \
                     dateadd(sec, {buffer_sec}, to_timestamp_ntz(max(added_time)))::varchar, \
                     get_overall_data_sources(array_agg(distinct f.value))\
                 ) \
            ) \
            else \
            object_construct('status', case when count(*) > 0 then 'yes' else 'no' end) \
            end as QUERY \
            from \
                {query_tracker_tbl}, lateral flatten(input => datasource) f \
            where processed_time is null;"
            # where added_time >= (select max(added_time) from {query_tracker_tbl} where processed_time is not null);"

        res = con.execute(sql)
        print(f"Executed query {sql}")
        query = self.object_as_dict(res)
        print(query)
        query = query[0]["query"]
        con.close()
        return graphdb_pb2.StringMessage(msg=json.dumps(query))

    @staticmethod
    def object_as_dict(obj):
        d, a = {}, []
        for rowproxy in obj:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                # build up the dictionary
                d = {**d, **{column: value}}
            a.append(json.loads(d) if isinstance(d, str) else d)
        return a

    def GetSnowFlakeCredentials(self, request, context):
        database = request.database
        schema = request.schema
        caller = request.caller

        print("Going to return credentials")

        file_name = f"{database}-{schema}-credentials.properties"
        full_fname = f"{RESOURCES_PREFIX}/resources/{file_name}"
        print(f"From file {full_fname}")

        credential_dict = U.load_properties(full_fname)

        assert database == credential_dict["database"]
        assert schema == credential_dict["schema"]

        account = credential_dict["account"]

        jdbc_prefix = "jdbc:snowflake"
        odbc_prefix = "https"
        base_url = f"{account}.snowflakecomputing.com"

        URL = f"{jdbc_prefix}://{base_url}" if caller == "java" else f"{odbc_prefix}://{base_url}/"

        credentials = graphdb_pb2.Credentials()
        credentials.account = account
        credentials.url = URL
        credentials.user = credential_dict["user"]
        credentials.password = credential_dict["password"]
        credentials.warehouse = credential_dict["warehouse"]
        credentials.database = credential_dict["database"]
        credentials.schema = credential_dict["schema"]
        credentials.role = credential_dict["role"]

        for k, v in credential_dict.items():
            if k not in ["user", "password", "warehouse", "database", "schema", "role", "account"]:
                credentials.additionalParameters[k] = v
                # print(f"Additional parameter {k} = {v} found so adding as additional param map field in Credentials msg")
        # print(f"As {credentials}")
        return credentials

    @staticmethod
    def single_update(case: CaseStatusObject, start_time: graphdb_pb2.Time, end_time: graphdb_pb2.Time,
                      query_export_time: graphdb_pb2.Time, data_sources: list, procTime: graphdb_pb2.Time, status: str):
        if start_time is not None and f":{start_time}:" != "::":
            print(f"Going to update startTime :{start_time}: and endTime :{end_time}:")
            case.update("QUERY_START_TIME", U.convert_proto_time_to_python_datetime(start_time))
            case.update("QUERY_END_TIME", U.convert_proto_time_to_python_datetime(end_time))

        if query_export_time is not None and f":{query_export_time}:" != "::":
            print(f"Going to update queryExportTime :{query_export_time}:")
            case.update("START_TIME", U.convert_proto_time_to_python_datetime(query_export_time))

        if data_sources is not None and len(data_sources) != 0:
            print(f"Going to update data source {data_sources}")
            case.update("DATASOURCES", list(set(data_sources)))

        print(f"Processing time as : {procTime.year}, {procTime.month}, {procTime.day}, {procTime.hour}, {procTime.minutes}")
        case.update("PROCESSING_TIME", U.convert_proto_time_to_python_datetime(procTime))

        case.update("status", status)
        print("Case loading status updated to " + str(status))

    @staticmethod
    def multi_update(case: CaseStatusObject, case_id: str, start_time: graphdb_pb2.Time, end_time: graphdb_pb2.Time,
                     query_export_time: graphdb_pb2.Time, data_sources: list, procTime: graphdb_pb2.Time, status: str):
        to_update = {
            "case_id": case_id,
            "QUERY_START_TIME": U.convert_proto_time_to_python_datetime(start_time),
            "QUERY_END_TIME": U.convert_proto_time_to_python_datetime(end_time),
            "START_TIME": U.convert_proto_time_to_python_datetime(query_export_time),
            "PROCESSING_TIME": U.convert_proto_time_to_python_datetime(procTime),
            "status": status
        }

        to_update_updated = {}
        # print(f"Before poping, {to_update}")
        for k, v in to_update.items():
            if v is not None:
                to_update_updated[k] = v

        # print(f"After poping {to_update_updated}")
        # print(f"Updating in single go with value {to_update_updated}")
        case.update(to_update_updated)
        # print(f"Updated {to_update_updated}")

        print("Updating data sources now")
        if data_sources is not None and len(data_sources) != 0:
            print(f"Going to update data source {data_sources}")
            case.update("DATASOURCES", list(set(data_sources)))

    def UpdateCaseLoadingStatus(self, request, context):
        print(f"Updating case status to {request.status} for caseId {request.caseId}")

        assert type(request) == graphdb_pb2.CaseLoadingStatus

        status = request.status
        case_id = request.caseId
        query = request.query
        start_time = request.startTime
        end_time = request.endTime
        procTime = request.processingTime
        query_export_time = request.queryExportTime
        data_sources = request.dataSources

        case = CaseStatusObject(case_ids=[case_id], query=query)
        # caseIdentifier = getattr(request, request.WhichOneof('caseIdentifier'))
        #
        # if isinstance(caseIdentifier, graphdb_pb2.CaseInfo):
        #     case_id = caseIdentifier.caseid
        #
        #     case = CaseStatusObject(case_id=case_id)
        # else:
        #     cases_all = CaseStatusObject(case_id=None)
        #     case_query = Commons.convert_case_information_proto_to_case_query_dict(caseIdentifier)
        #     case_id = cases_all.get_case_id(case_query)
        #
        #     case = CaseStatusObject(case_id=case_id)
        # print("Initialized case status obj")
        # print(start_time, end_time, query_export_time, data_sources)
        # print(start_time is None, start_time == "", start_time == " ", f":{start_time}:" == "::")
        # print(f":{start_time}:")
        # print(query_export_time is None, query_export_time == "", query_export_time == " ", f":{query_export_time}:" == "::")
        # print(f":{query_export_time}:")
        # print(data_sources is None, data_sources == "", len(data_sources) == 0)
        self.multi_update(case, case_id, start_time, end_time, query_export_time, data_sources, procTime, status)

        self.update_case_query_tracker(case, status, U.convert_proto_time_to_python_datetime(procTime))
        request.status = status
        return request

    def update_case_query_tracker(self, case: CaseStatusObject, status: str, time: dt.datetime):
        case.update_tracker(status, time)
        return case

    def convert_to_python_obj(self, obj):
        objects = []
        for elem in obj:
            data = elem["structValue"]["fields"]
            cols = list(data.keys())
            node_simple = {}
            for col in cols:
                node_simple[col] = list(data[col].values())[0]
            objects.append(node_simple)
        return objects

    def IsCaseExported(self, request, context):
        print("Going to get the status of case")
        # print(request)
        status = CheckQueryExported(request)
        return status.get_status()

    def UpdateCaseLoadingProperties(self, request, context):
        print(f"Updating case properties to {request.property}")
        print(f"Case id is {request.caseId}")
        assert type(request) == graphdb_pb2.CaseLoadingProperties

        case_id = request.caseId

        properties = MessageToDict(request)["property"]
        assert len(properties) == 1
        col_name = list(properties.keys())[0]

        print(col_name)
        column_data = properties[col_name]
        # print(column_data)
        # print("Before conversion")
        obj = self.convert_to_python_obj(column_data["listValue"]["values"])
        # print("After conversion")
        # print(obj)

        case = CaseStatusObject(case_ids=[case_id])
        case.update(col_name, obj)
        print("Initialized case status obj")

        # case.update("status", status)
        # print("Case loading status updated to " + str(status))
        # request.status = status
        return graphdb_pb2.google_dot_protobuf_dot_empty__pb2.Empty()

    def UpdateNodesForCase(self, request_iterator, context):
        print("Updating the nodes for the case")

        nodes = []
        case_id = None

        for record in request_iterator:
            case_id = record.caseId
            node = record.node

            field = getattr(node, node.WhichOneof("kind"))
            assert type(field) == graphdb_pb2.GenericStructure

            node_dict = {}
            for key in field.fields:
                prop_struct = field.fields[key]
                prop_val = getattr(prop_struct, prop_struct.WhichOneof("kind"))
                node_dict[key] = prop_val
            nodes.append(node_dict)

        print("Iterated over nodes to generate node dict list")

        case = CaseStatusObject(case_ids=[case_id])
        print("Updating the nodes for case")
        case.update("nodes", nodes)
        print("Updated the nodes for case")
        #
        # for record in request_iterator:
        #     if i < (batch_num*batch):
        #         case_id = record.caseId
        #         node = record.node
        #
        #         field = getattr(node, node.WhichOneof("kind"))
        #         assert type(field) == graphdb_pb2.GenericStructure
        #
        #         node_dict = {}
        #         for key in field.fields:
        #             prop_struct = field.fields[key]
        #             prop_val = getattr(prop_struct, prop_struct.WhichOneof("kind"))
        #             node_dict[key] = prop_val
        #         nodes.append(node_dict)
        #
        #     else:
        #         print(f"Nodes {i} with batch num {batch_num} over. going to load to SF now")
        #         if case_id is None:
        #             raise AttributeError("ERROR. Case Id should not have been none")
        #
        #         case = CaseStatusObject(case_ids=[case_id])
        #         case.update("nodes", nodes)
        #         nodes = []
        #         batch_num += 1
        #         print(f"Finished loading nodes in batch {batch_num} and i size is {i}")
        #
        #     i += 1
        #
        # if len(nodes) > 0:
        #     print("Going to load the remaing nodes now")
        #     case = CaseStatusObject(case_ids=[case_id])
        #     case.update("nodes", nodes)

        empty = graphdb_pb2.google_dot_protobuf_dot_empty__pb2.Empty()
        return empty

    def GetCaseLoadingStatus(self, request, context):
        assert type(request) == graphdb_pb2.CaseInfo
        case_ids = request.caseId
        case = CaseStatusObject(case_ids=case_ids)
        # status = case.status()
        case_status = case.read_and_get_status()
        # response = graphdb_pb2.CaseLoadingStatus(caseId=case_id, status=status)
        print("Returning status of case as ")
        return case_status

    def GetCaseIds(self, request, context):
        print("Gettng all case ids")
        case = CaseStatusObject(case_ids=list())
        cases = case.read_all(True)
        print("Read all case ids")
        for case in cases:
            obj = graphdb_pb2.CaseExportStatus(caseId=case["case_id"])
            yield obj
